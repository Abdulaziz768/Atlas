from pyspark.sql import SparkSession
from atlas.spark.session import create_spark_session


def test_create_spark_session():
    session = create_spark_session()

    assert isinstance(session, SparkSession)

    session.stop()