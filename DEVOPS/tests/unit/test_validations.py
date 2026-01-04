from src.utils.validations.data_quality import run_data_quality_checks
from src.jobs.member_etl import clean_member_data

def test_data_quality_checks(spark):
    # Use same test data as before
    data = [
        ("M001", "ACTIVE", 45, "2025-01-01"),      # good
        ("M002", None, -5, "2026-01-01"),          # bad → filtered out
        ("M003", "TERMINATED", 130, "2024-12-31"), # bad → filtered
        ("ABC123", "ACTIVE", 30, "2025-03-15"),    # bad ID → filtered
        ("M001", "ACTIVE", 45, "2025-01-01"),      # duplicate → deduped
        ("M004", "ACTIVE", 25, "2025-06-01")       # good
    ]
    columns = ["member_id", "status", "age", "enrollment_date"]
    df = spark.createDataFrame(data, columns)

    cleaned_df = clean_member_data(df)
    results = run_data_quality_checks(cleaned_df)

    # After cleaning, should pass all
    assert results["overall"]["passed"] is True
    assert results["no_null_keys"]["passed"] is True
    assert results["no_duplicates"]["passed"] is True
    assert results["valid_status"]["passed"] is True