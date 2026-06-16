def extract_enem_data(spark, file_path):
    df = (
        spark.read
        .option("header", True)
        .option("sep", ";")
        .option("encoding", "ISO-8859-1")
        .option("inferSchema", True)
        .csv(file_path)
    )

    return df