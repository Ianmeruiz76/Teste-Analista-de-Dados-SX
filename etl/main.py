from spark_session import get_spark_session
from extract import extract_enem_data
from transform import transform_enem_data
from load import load_tables


USAR_AMOSTRA = True
QTD_AMOSTRA = 50000


def main():
    spark = get_spark_session()

    file_path = "data/MICRODADOS_ENEM_2020.csv"

    print("Lendo base do ENEM 2020...")
    df = extract_enem_data(spark, file_path)

    print("Base carregada com sucesso.")
    print(f"Quantidade de colunas: {len(df.columns)}")

    if USAR_AMOSTRA:
        print(f"Executando ETL com amostra de {QTD_AMOSTRA} registros...")
        df_processamento = df.limit(QTD_AMOSTRA)
    else:
        print("Executando ETL com a base completa...")
        df_processamento = df

    print("Transformando dados...")
    tabelas = transform_enem_data(df_processamento)

    for nome_tabela in tabelas.keys():
        print(f"Tabela criada: {nome_tabela}")

    print("Carregando dados no MySQL...")
    load_tables(tabelas, clear_before_load=True)

    print("ETL finalizado com sucesso.")

    spark.stop()


if __name__ == "__main__":
    main()