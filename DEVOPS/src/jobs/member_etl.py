from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, lit, regexp_extract, length

def clean_member_data(df: DataFrame) -> DataFrame:
    """
    Clean member data for healthcare ETL:
    - Handle missing/null eligibility → set to 'UNKNOWN'
    - Validate & clean age (set invalid to null, filter out)
    - Validate member_id format (M followed by digits)
    - Remove duplicates based on member_id
    - Add validation flags
    """
    # Step 1: Clean eligibility
    df = df.withColumn(
        "eligibility_status",
        when(col("status").isNull() | (col("status") == ""), "UNKNOWN")
         .otherwise(col("status"))
    )

    # Step 2: Clean age & add flag
    df = df.withColumn(
        "clean_age",
        when((col("age").cast("int") >= 0) & (col("age").cast("int") <= 120), col("age").cast("int"))
         .otherwise(None)
    )

    # Step 3: Validate member_id format (simple regex: starts with M + digits)
    df = df.withColumn(
        "is_valid_id",
        when(
            (col("member_id").isNotNull()) &
            (regexp_extract(col("member_id"), r"^M\d+$", 0) != ""), lit(True)
        ).otherwise(lit(False))
    )

    # Step 4: Filter invalid records (for demo; in real pipeline you might log instead)
    df = df.filter(
        (col("clean_age").isNotNull()) &
        (col("is_valid_id") == True)
    )

    # Step 5: Drop duplicates (keep first)
    df = df.dropDuplicates(["member_id"])

    return df