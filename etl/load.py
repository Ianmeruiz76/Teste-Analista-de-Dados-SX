import pymysql


DB_HOST = "localhost"
DB_PORT = 3308
DB_NAME = "enem_dw"
DB_USER = "root"
DB_PASSWORD = "root"

JDBC_URL = (
    f"jdbc:mysql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?rewriteBatchedStatements=true"
    "&useSSL=false"
    "&allowPublicKeyRetrieval=true"
    "&serverTimezone=UTC"
    "&useServerPrepStmts=false"     # desabilita prepared statements (mais rápido em bulk)
    "&cachePrepStmts=false"
)

JDBC_PROPERTIES = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "com.mysql.cj.jdbc.Driver",
}


def _get_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


def _executar(cursor, sqls):
    for sql in sqls:
        cursor.execute(sql)


def disable_indexes(cursor, table):
    """
    Desativa verificação de índices secundários durante a carga.
    Só funciona em MyISAM nativamente; no InnoDB, usamos a abordagem
    de desabilitar unique_checks + foreign_key_checks.
    """
    cursor.execute(f"ALTER TABLE {table} DISABLE KEYS;")


def enable_indexes(cursor, table):
    cursor.execute(f"ALTER TABLE {table} ENABLE KEYS;")


def pre_load_otimizacoes(cursor):
    """
    Configurações de sessão para máxima velocidade de inserção no InnoDB.
    """
    _executar(cursor, [
        "SET FOREIGN_KEY_CHECKS = 0;",
        "SET UNIQUE_CHECKS = 0;",
        "SET GLOBAL innodb_flush_log_at_trx_commit = 0;",  # perigo: só para ETL
        "SET SESSION bulk_insert_buffer_size = 268435456;",  # 256MB
        "SET SESSION innodb_lock_wait_timeout = 300;",
    ])


def pos_load_otimizacoes(cursor):
    _executar(cursor, [
        "SET FOREIGN_KEY_CHECKS = 1;",
        "SET UNIQUE_CHECKS = 1;",
        "SET GLOBAL innodb_flush_log_at_trx_commit = 1;",
    ])


def clear_tables():
    """
    Trunca tabelas na ordem inversa das FKs.
    """
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            _executar(cursor, [
                "SET FOREIGN_KEY_CHECKS = 0;",
                "TRUNCATE TABLE fato_resultados;",
                "TRUNCATE TABLE dim_candidato;",
                "TRUNCATE TABLE dim_escola;",
                "TRUNCATE TABLE dim_local_prova;",
                "TRUNCATE TABLE dim_socioeconomica;",
                "SET FOREIGN_KEY_CHECKS = 1;",
            ])
        connection.commit()
        print("✓ Tabelas limpas.")
    finally:
        connection.close()


def set_session_flags(enable: bool):
    """
    Liga/desliga otimizações de sessão MySQL para carga em massa.
    """
    connection = _get_connection()
    try:
        with connection.cursor() as cursor:
            if enable:
                pre_load_otimizacoes(cursor)
                print("✓ Otimizações MySQL ativadas.")
            else:
                pos_load_otimizacoes(cursor)
                print("✓ Otimizações MySQL desativadas.")
        connection.commit()
    finally:
        connection.close()


def load_table(df, table_name, partitions=16):
    """
    Carrega um DataFrame Spark em uma tabela MySQL via JDBC.

    Parâmetros de performance:
    - partitions: número de conexões paralelas ao MySQL
    - batchsize: linhas por batch JDBC (5000–10000 é o sweet spot)
    - isolationLevel=NONE: sem transação por linha (crítico para fato)
    """
    (
        df.repartition(partitions)
        .write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", table_name)
        .option("user", DB_USER)
        .option("password", DB_PASSWORD)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("batchsize", "10000")           # aumentado de 5000 → 10000
        .option("isolationLevel", "NONE")       # sem overhead de transação
        .option("numPartitions", str(partitions))
        .mode("append")
        .save()
    )


def load_tables(tabelas, clear_before_load=True):
    """
    Carga otimizada: dimensões primeiro, depois fato.
    Desabilita FKs e unique checks durante toda a carga.
    """
    if clear_before_load:
        print("→ Limpando tabelas...")
        clear_tables()

    print("→ Ativando otimizações de sessão MySQL...")
    set_session_flags(enable=True)

    try:
        dimensoes = [
            ("dim_candidato",     4),
            ("dim_escola",        2),
            ("dim_local_prova",   2),
            ("dim_socioeconomica", 4),
        ]

        for nome, parts in dimensoes:
            print(f"→ Carregando {nome} ({parts} partições)...")
            load_table(tabelas[nome], nome, partitions=parts)
            print(f"  ✓ {nome} OK")

        # Fato: mais partições = mais conexões paralelas = mais throughput
        print("→ Carregando fato_resultados (8 partições)...")
        load_table(tabelas["fato_resultados"], "fato_resultados", partitions=8)
        print("  ✓ fato_resultados OK")

    finally:
        print("→ Restaurando configurações MySQL...")
        set_session_flags(enable=False)

    print("\n✓ ETL finalizado com sucesso.")