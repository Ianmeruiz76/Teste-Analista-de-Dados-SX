from pyspark.sql import functions as F


def criar_mapa(coluna, mapa):
    expressao_mapa = F.create_map(
        [F.lit(x) for item in mapa.items() for x in item]
    )

    return expressao_mapa[F.col(coluna)]


def gerar_sk(*colunas):
    """
    Gera uma surrogate key determinística usando hash.
    Evita Window/row_number, que consome muita memória na base completa.
    """
    cols_tratadas = [
        F.coalesce(F.col(c).cast("string"), F.lit("NA"))
        for c in colunas
    ]

    return F.xxhash64(*cols_tratadas).cast("long")


def transform_enem_data(df):
    colunas_necessarias = [
        # Participante
        "NU_INSCRICAO",
        "NU_ANO",
        "TP_FAIXA_ETARIA",
        "TP_SEXO",
        "TP_ESTADO_CIVIL",
        "TP_COR_RACA",
        "TP_NACIONALIDADE",
        "TP_ST_CONCLUSAO",
        "TP_ANO_CONCLUIU",
        "TP_ESCOLA",
        "TP_ENSINO",
        "IN_TREINEIRO",

        # Escola
        "CO_MUNICIPIO_ESC",
        "NO_MUNICIPIO_ESC",
        "CO_UF_ESC",
        "SG_UF_ESC",
        "TP_DEPENDENCIA_ADM_ESC",
        "TP_LOCALIZACAO_ESC",
        "TP_SIT_FUNC_ESC",

        # Local da prova
        "CO_MUNICIPIO_PROVA",
        "NO_MUNICIPIO_PROVA",
        "CO_UF_PROVA",
        "SG_UF_PROVA",

        # Prova objetiva
        "TP_PRESENCA_CN",
        "TP_PRESENCA_CH",
        "TP_PRESENCA_LC",
        "TP_PRESENCA_MT",
        "CO_PROVA_CN",
        "CO_PROVA_CH",
        "CO_PROVA_LC",
        "CO_PROVA_MT",
        "NU_NOTA_CN",
        "NU_NOTA_CH",
        "NU_NOTA_LC",
        "NU_NOTA_MT",
        "TP_LINGUA",

        # Redação
        "TP_STATUS_REDACAO",
        "NU_NOTA_COMP1",
        "NU_NOTA_COMP2",
        "NU_NOTA_COMP3",
        "NU_NOTA_COMP4",
        "NU_NOTA_COMP5",
        "NU_NOTA_REDACAO",

        # Questionário socioeconômico
        "Q001", "Q002", "Q003", "Q004", "Q005",
        "Q006", "Q007", "Q008", "Q009", "Q010",
        "Q011", "Q012", "Q013", "Q014", "Q015",
        "Q016", "Q017", "Q018", "Q019", "Q020",
        "Q021", "Q022", "Q023", "Q024", "Q025",
    ]

    colunas_faltantes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    if colunas_faltantes:
        raise ValueError(
            f"Colunas não encontradas na base: {colunas_faltantes}"
        )

    df = df.select(*colunas_necessarias)

    # Cache após select inicial: evita reler o CSV do disco para cada dimensão
    df = df.cache()

    # Padronização de nomes e tipos
    df = df.select(
        # Participante
        F.col("NU_INSCRICAO").cast("long").alias("nu_inscricao"),
        F.col("NU_ANO").cast("int").alias("nu_ano"),
        F.col("TP_FAIXA_ETARIA").cast("int").alias("tp_faixa_etaria"),
        F.col("TP_SEXO").alias("tp_sexo"),
        F.col("TP_ESTADO_CIVIL").cast("int").alias("tp_estado_civil"),
        F.col("TP_COR_RACA").cast("int").alias("tp_cor_raca"),
        F.col("TP_NACIONALIDADE").cast("int").alias("tp_nacionalidade"),
        F.col("TP_ST_CONCLUSAO").cast("int").alias("tp_st_conclusao"),
        F.col("TP_ANO_CONCLUIU").cast("int").alias("tp_ano_concluiu"),
        F.col("TP_ESCOLA").cast("int").alias("tp_escola"),
        F.col("TP_ENSINO").cast("int").alias("tp_ensino"),
        F.col("IN_TREINEIRO").cast("int").alias("in_treineiro"),

        # Escola
        F.col("CO_MUNICIPIO_ESC").cast("int").alias("co_municipio_esc"),
        F.col("NO_MUNICIPIO_ESC").alias("no_municipio_esc"),
        F.col("CO_UF_ESC").cast("int").alias("co_uf_esc"),
        F.col("SG_UF_ESC").alias("sg_uf_esc"),
        F.col("TP_DEPENDENCIA_ADM_ESC").cast("int").alias("tp_dependencia_adm_esc"),
        F.col("TP_LOCALIZACAO_ESC").cast("int").alias("tp_localizacao_esc"),
        F.col("TP_SIT_FUNC_ESC").cast("int").alias("tp_sit_func_esc"),

        # Local da prova
        F.col("CO_MUNICIPIO_PROVA").cast("int").alias("co_municipio_prova"),
        F.col("NO_MUNICIPIO_PROVA").alias("no_municipio_prova"),
        F.col("CO_UF_PROVA").cast("int").alias("co_uf_prova"),
        F.col("SG_UF_PROVA").alias("sg_uf_prova"),

        # Prova objetiva
        F.col("TP_PRESENCA_CN").cast("int").alias("tp_presenca_cn"),
        F.col("TP_PRESENCA_CH").cast("int").alias("tp_presenca_ch"),
        F.col("TP_PRESENCA_LC").cast("int").alias("tp_presenca_lc"),
        F.col("TP_PRESENCA_MT").cast("int").alias("tp_presenca_mt"),
        F.col("CO_PROVA_CN").cast("int").alias("co_prova_cn"),
        F.col("CO_PROVA_CH").cast("int").alias("co_prova_ch"),
        F.col("CO_PROVA_LC").cast("int").alias("co_prova_lc"),
        F.col("CO_PROVA_MT").cast("int").alias("co_prova_mt"),
        F.col("NU_NOTA_CN").cast("double").alias("nu_nota_cn"),
        F.col("NU_NOTA_CH").cast("double").alias("nu_nota_ch"),
        F.col("NU_NOTA_LC").cast("double").alias("nu_nota_lc"),
        F.col("NU_NOTA_MT").cast("double").alias("nu_nota_mt"),
        F.col("TP_LINGUA").cast("int").alias("tp_lingua"),

        # Redação
        F.col("TP_STATUS_REDACAO").cast("int").alias("tp_status_redacao"),
        F.col("NU_NOTA_COMP1").cast("double").alias("nu_nota_comp1"),
        F.col("NU_NOTA_COMP2").cast("double").alias("nu_nota_comp2"),
        F.col("NU_NOTA_COMP3").cast("double").alias("nu_nota_comp3"),
        F.col("NU_NOTA_COMP4").cast("double").alias("nu_nota_comp4"),
        F.col("NU_NOTA_COMP5").cast("double").alias("nu_nota_comp5"),
        F.col("NU_NOTA_REDACAO").cast("double").alias("nu_nota_redacao"),

        # Socioeconômico
        F.coalesce(F.col("Q001"), F.lit("Z")).alias("q001"),
        F.coalesce(F.col("Q002"), F.lit("Z")).alias("q002"),
        F.coalesce(F.col("Q003"), F.lit("Z")).alias("q003"),
        F.coalesce(F.col("Q004"), F.lit("Z")).alias("q004"),
        F.coalesce(F.col("Q005").cast("int"), F.lit(0)).alias("q005"),
        F.coalesce(F.col("Q006"), F.lit("Z")).alias("q006"),
        F.coalesce(F.col("Q007"), F.lit("Z")).alias("q007"),
        F.coalesce(F.col("Q008"), F.lit("Z")).alias("q008"),
        F.coalesce(F.col("Q009"), F.lit("Z")).alias("q009"),
        F.coalesce(F.col("Q010"), F.lit("Z")).alias("q010"),
        F.coalesce(F.col("Q011"), F.lit("Z")).alias("q011"),
        F.coalesce(F.col("Q012"), F.lit("Z")).alias("q012"),
        F.coalesce(F.col("Q013"), F.lit("Z")).alias("q013"),
        F.coalesce(F.col("Q014"), F.lit("Z")).alias("q014"),
        F.coalesce(F.col("Q015"), F.lit("Z")).alias("q015"),
        F.coalesce(F.col("Q016"), F.lit("Z")).alias("q016"),
        F.coalesce(F.col("Q017"), F.lit("Z")).alias("q017"),
        F.coalesce(F.col("Q018"), F.lit("Z")).alias("q018"),
        F.coalesce(F.col("Q019"), F.lit("Z")).alias("q019"),
        F.coalesce(F.col("Q020"), F.lit("Z")).alias("q020"),
        F.coalesce(F.col("Q021"), F.lit("Z")).alias("q021"),
        F.coalesce(F.col("Q022"), F.lit("Z")).alias("q022"),
        F.coalesce(F.col("Q023"), F.lit("Z")).alias("q023"),
        F.coalesce(F.col("Q024"), F.lit("Z")).alias("q024"),
        F.coalesce(F.col("Q025"), F.lit("Z")).alias("q025"),
    )

    # Mapas descritivos
    mapa_faixa_etaria = {
        1: "Menor de 17 anos",
        2: "17 anos",
        3: "18 anos",
        4: "19 anos",
        5: "20 anos",
        6: "21 anos",
        7: "22 anos",
        8: "23 anos",
        9: "24 anos",
        10: "25 anos",
        11: "Entre 26 e 30 anos",
        12: "Entre 31 e 35 anos",
        13: "Entre 36 e 40 anos",
        14: "Entre 41 e 45 anos",
        15: "Entre 46 e 50 anos",
        16: "Entre 51 e 55 anos",
        17: "Entre 56 e 60 anos",
        18: "Entre 61 e 65 anos",
        19: "Entre 66 e 70 anos",
        20: "Maior de 70 anos",
    }

    mapa_sexo = {
        "M": "Masculino",
        "F": "Feminino",
    }

    mapa_raca = {
        0: "Não declarado",
        1: "Branca",
        2: "Preta",
        3: "Parda",
        4: "Amarela",
        5: "Indígena",
    }

    mapa_dependencia = {
        1: "Federal",
        2: "Estadual",
        3: "Municipal",
        4: "Privada",
    }

    mapa_localizacao = {
        1: "Urbana",
        2: "Rural",
    }

    mapa_situacao = {
        1: "Em atividade",
        2: "Paralisada",
        3: "Extinta",
        4: "Extinta em anos anteriores",
    }

    mapa_lingua = {
        0: "Inglês",
        1: "Espanhol",
    }

    mapa_status_redacao = {
        1: "Sem problemas",
        2: "Anulada",
        3: "Cópia texto motivador",
        4: "Em branco",
        6: "Fuga ao tema",
        7: "Não atendimento ao tipo textual",
        8: "Texto insuficiente",
        9: "Parte desconectada",
    }

    df = (
        df
        .withColumn("ds_faixa_etaria", criar_mapa("tp_faixa_etaria", mapa_faixa_etaria))
        .withColumn("ds_sexo", criar_mapa("tp_sexo", mapa_sexo))
        .withColumn("ds_cor_raca", criar_mapa("tp_cor_raca", mapa_raca))
        .withColumn("ds_dependencia_adm_esc", criar_mapa("tp_dependencia_adm_esc", mapa_dependencia))
        .withColumn("ds_localizacao_esc", criar_mapa("tp_localizacao_esc", mapa_localizacao))
        .withColumn("ds_sit_func_esc", criar_mapa("tp_sit_func_esc", mapa_situacao))
        .withColumn("ds_lingua", criar_mapa("tp_lingua", mapa_lingua))
        .withColumn("ds_status_redacao", criar_mapa("tp_status_redacao", mapa_status_redacao))
    )

    socio_cols = [
        "q001", "q002", "q003", "q004", "q005",
        "q006", "q007", "q008", "q009", "q010",
        "q011", "q012", "q013", "q014", "q015",
        "q016", "q017", "q018", "q019", "q020",
        "q021", "q022", "q023", "q024", "q025",
    ]

    # Surrogate Keys por hash
    df = (
        df
        .withColumn("sk_candidato", F.col("nu_inscricao").cast("long"))
        .withColumn(
            "sk_escola",
            F.when(
                F.col("co_municipio_esc").isNotNull(),
                gerar_sk(
                    "co_municipio_esc",
                    "no_municipio_esc",
                    "co_uf_esc",
                    "sg_uf_esc",
                    "tp_dependencia_adm_esc",
                    "tp_localizacao_esc",
                    "tp_sit_func_esc",
                ),
            ).otherwise(F.lit(None).cast("long")),
        )
        .withColumn(
            "sk_local_prova",
            gerar_sk(
                "co_municipio_prova",
                "no_municipio_prova",
                "co_uf_prova",
                "sg_uf_prova",
            ),
        )
        .withColumn(
            "sk_socioeconomica",
            gerar_sk(*socio_cols),
        )
    )

    # DIMENSÃO CANDIDATO
    dim_candidato = (
        df
        .select(
            "sk_candidato",
            "nu_inscricao",
            "nu_ano",
            "tp_faixa_etaria",
            "ds_faixa_etaria",
            "tp_sexo",
            "ds_sexo",
            "tp_estado_civil",
            "tp_cor_raca",
            "ds_cor_raca",
            "tp_nacionalidade",
            "tp_st_conclusao",
            "tp_ano_concluiu",
            "tp_escola",
            "tp_ensino",
            "in_treineiro",
        )
        .dropDuplicates(["sk_candidato"])
    )

    # DIMENSÃO ESCOLA
    dim_escola = (
        df
        .filter(F.col("sk_escola").isNotNull())
        .select(
            "sk_escola",
            "co_municipio_esc",
            "no_municipio_esc",
            "co_uf_esc",
            "sg_uf_esc",
            "tp_dependencia_adm_esc",
            "ds_dependencia_adm_esc",
            "tp_localizacao_esc",
            "ds_localizacao_esc",
            "tp_sit_func_esc",
            "ds_sit_func_esc",
        )
        .dropDuplicates(["sk_escola"])
    )

    # DIMENSÃO LOCAL DE PROVA
    dim_local_prova = (
        df
        .select(
            "sk_local_prova",
            "co_municipio_prova",
            "no_municipio_prova",
            "co_uf_prova",
            "sg_uf_prova",
        )
        .dropDuplicates(["sk_local_prova"])
    )

    # DIMENSÃO SOCIOECONÔMICA
    dim_socioeconomica = (
        df
        .select(
            "sk_socioeconomica",
            *socio_cols,
        )
        .dropDuplicates(["sk_socioeconomica"])
    )

    # TABELA FATO
    cond_notas_validas = (
        F.col("nu_nota_cn").isNotNull()
        & F.col("nu_nota_ch").isNotNull()
        & F.col("nu_nota_lc").isNotNull()
        & F.col("nu_nota_mt").isNotNull()
    )

    fato_resultados = (
        df
        .withColumn(
            "nota_total",
            F.when(
                cond_notas_validas,
                F.col("nu_nota_cn")
                + F.col("nu_nota_ch")
                + F.col("nu_nota_lc")
                + F.col("nu_nota_mt"),
            ),
        )
        .withColumn(
            "nota_media",
            F.when(
                cond_notas_validas,
                F.col("nota_total") / 4,
            ),
        )
        .withColumn(
            "fl_ausente",
            F.when(
                (F.col("tp_presenca_cn") == 0)
                | (F.col("tp_presenca_ch") == 0)
                | (F.col("tp_presenca_lc") == 0)
                | (F.col("tp_presenca_mt") == 0),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "fl_eliminado",
            F.when(
                (F.col("tp_presenca_cn") == 2)
                | (F.col("tp_presenca_ch") == 2)
                | (F.col("tp_presenca_lc") == 2)
                | (F.col("tp_presenca_mt") == 2),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "sk_resultado",
            F.xxhash64(
                F.col("sk_candidato").cast("string"),
                F.col("sk_local_prova").cast("string"),
            ).cast("long"),
        )
        .select(
            "sk_resultado",
            "sk_candidato",
            "sk_escola",
            "sk_local_prova",
            "sk_socioeconomica",

            "tp_presenca_cn",
            "tp_presenca_ch",
            "tp_presenca_lc",
            "tp_presenca_mt",

            "co_prova_cn",
            "co_prova_ch",
            "co_prova_lc",
            "co_prova_mt",

            "tp_lingua",
            "ds_lingua",

            "nu_nota_cn",
            "nu_nota_ch",
            "nu_nota_lc",
            "nu_nota_mt",

            "tp_status_redacao",
            "ds_status_redacao",

            "nu_nota_comp1",
            "nu_nota_comp2",
            "nu_nota_comp3",
            "nu_nota_comp4",
            "nu_nota_comp5",
            "nu_nota_redacao",

            "nota_total",
            "nota_media",

            "fl_ausente",
            "fl_eliminado",
        )
    )

    return {
        "dim_candidato": dim_candidato,
        "dim_escola": dim_escola,
        "dim_local_prova": dim_local_prova,
        "dim_socioeconomica": dim_socioeconomica,
        "fato_resultados": fato_resultados,
    }