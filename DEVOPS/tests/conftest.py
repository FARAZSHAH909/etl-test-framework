import pytest
from pyspark.sql import SparkSession
import os
import sys

@pytest.fixture(scope="session")
def spark():
    # Set Python path for Spark workers
    python_path = sys.executable
    os.environ['PYSPARK_PYTHON'] = python_path
    os.environ['PYSPARK_DRIVER_PYTHON'] = python_path
    
    spark = SparkSession.builder \
        .appName("simple_etl_test") \
        .master("local[1]") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.sql.shuffle.partitions", "1") \
        .config("spark.app.name", "test_app") \
        .getOrCreate()
    yield spark
    spark.stop()