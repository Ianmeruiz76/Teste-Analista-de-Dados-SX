import os

HADOOP_HOME = "C:/hadoop"

os.environ["HADOOP_HOME"] = HADOOP_HOME
os.environ["hadoop.home.dir"] = HADOOP_HOME
os.environ["PATH"] = f"{HADOOP_HOME}/bin;" + os.environ.get("PATH", "")

from pyspark.sql import SparkSession


def get_spark_session():
    spark = (
        SparkSession.builder
        .appName("ETL ENEM 2020")
        .master("local[*]")
        .config("spark.jars.packages", "com.mysql:mysql-connector-j:8.0.33")

        # Memória — ajuste spark.driver.memory conforme sua RAM:
        # 8GB RAM  → use "4g"
        # 16GB RAM → use "8g"
        # 32GB RAM → use "16g"
        .config("spark.driver.memory", "10g")
        .config("spark.driver.maxResultSize", "2g")

        # Partições de shuffle menores evitam OOM em local[*]
        .config("spark.sql.shuffle.partitions", "8")

        # Evita OOM no cache e shuffle
        .config("spark.memory.fraction", "0.8")
        .config("spark.memory.storageFraction", "0.3")

        # Adaptive Query Execution: Spark ajusta partições automaticamente
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")

        # Hadoop
        .config("spark.driver.extraJavaOptions", "-Dhadoop.home.dir=C:/hadoop")
        .config("spark.executor.extraJavaOptions", "-Dhadoop.home.dir=C:/hadoop")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark