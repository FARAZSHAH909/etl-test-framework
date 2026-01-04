def test_basic_data_cleaning(spark):
    # Sample input data (like member records)
    data = [
        ("M001", "ACTIVE", 45, "2025-01-01"),
        ("M002", None, -5, "2026-13-01"),   # bad age + invalid date
        ("M003", "TERMINATED", 120, "2024-12-31")
    ]
    columns = ["member_id", "status", "age", "enrollment_date"]
    df = spark.createDataFrame(data, columns)

    # Simple cleaning logic (you will replace this with your real function later)
    cleaned_df = df.filter("age >= 0") \
                   .withColumnRenamed("status", "eligibility_status")

    # Assertions - what should be true after cleaning
    assert cleaned_df.count() == 2                      # removed invalid age
    assert "eligibility_status" in cleaned_df.columns
    assert cleaned_df.filter("age < 0").count() == 0    # no negative ages