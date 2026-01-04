from pyspark.sql import SparkSession
from src.jobs.member_etl import clean_member_data
from src.utils.validations.data_quality import run_data_quality_checks

def run_etl_pipeline(input_data_path=None, spark=None):
    """
    Simple orchestrator:
    - Load sample data (or from path if provided)
    - Clean
    - Validate
    - Reconcile (basic row count comparison)
    - Return report
    """
    if spark is None:
        spark = SparkSession.builder.appName("etl_pipeline_test").master("local[*]").getOrCreate()

    # Sample data if no path provided (for local testing)
    if input_data_path is None:
        data = [
            ("M001", "ACTIVE", 45, "2025-01-01"),
            ("M002", None, -5, "2026-01-01"),
            ("M003", "TERMINATED", 130, "2024-12-31"),
            ("ABC123", "ACTIVE", 30, "2025-03-15"),
            ("M001", "ACTIVE", 45, "2025-01-01"),  # duplicate
            ("M004", "ACTIVE", 25, "2025-06-01"),
            ("M005", "ACTIVE", 121, "2025-07-10")
        ]
        columns = ["member_id", "status", "age", "enrollment_date"]
        input_df = spark.createDataFrame(data, columns)
    else:
        # In real use: read from CSV/Parquet (add later)
        input_df = spark.read.csv(input_data_path, header=True, inferSchema=True)

    input_count = input_df.count()

    # Step 1: Clean
    cleaned_df = clean_member_data(input_df)
    cleaned_count = cleaned_df.count()

    # Step 2: Validate
    dq_results = run_data_quality_checks(cleaned_df)

    # Step 3: Basic reconciliation
    reconciliation = {
        "input_rows": input_count,
        "output_rows": cleaned_count,
        "rows_dropped": input_count - cleaned_count,
        "drop_percentage": round((input_count - cleaned_count) / input_count * 100, 2) if input_count > 0 else 0
    }

    # Build simple report
    report = {
        "reconciliation": reconciliation,
        "data_quality": dq_results,
        "status": "PASS" if dq_results["overall"]["passed"] else "FAIL"
    }

    print("ETL Pipeline Report:")
    print(report)

    return report, cleaned_df