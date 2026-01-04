from src.jobs.member_etl import clean_member_data

def test_clean_member_data_full(spark):
    # More realistic test data
    data = [
        ("M001", "ACTIVE", 45, "2025-01-01"),      # good
        ("M002", None, -5, "2026-01-01"),          # bad age + null status
        ("M003", "TERMINATED", 130, "2024-12-31"), # age too high
        ("ABC123", "ACTIVE", 30, "2025-03-15"),    # invalid ID format
        ("M001", "ACTIVE", 45, "2025-01-01"),      # duplicate
        ("M004", "ACTIVE", 25, "2025-06-01")       # good
    ]
    columns = ["member_id", "status", "age", "enrollment_date"]
    df = spark.createDataFrame(data, columns)

    result_df = clean_member_data(df)

    # Assertions
    assert result_df.count() == 2                       # only M001 and M004 should remain
    assert result_df.filter("eligibility_status = 'UNKNOWN'").count() == 0  # nulls cleaned but filtered out
    assert result_df.filter("clean_age > 120").count() == 0
    assert result_df.filter("is_valid_id = false").count() == 0
    assert "clean_age" in result_df.columns
    assert "is_valid_id" in result_df.columns