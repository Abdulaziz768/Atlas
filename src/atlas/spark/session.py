from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("Atlas")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-hadoop-cloud_2.13:4.2.0",
        )
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.auth.ProfileAWSCredentialsProvider",
        )
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.profile",
            "default",
        )
        .getOrCreate()
    )