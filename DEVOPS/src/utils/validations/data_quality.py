from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when, lit

def run_data_quality_checks(df: DataFrame, member_id_col="member_id", age_col="clean_age", status_col="eligibility_status") -> dict:
    """
    Run basic DQ checks on cleaned member data.
    Returns a dict with pass/fail status and details.
    """
    checks = {}

    # 1. No nulls in key columns
    null_check = df.filter(
        col(member_id_col).isNull() |
        col(age_col).isNull() |
        col(status_col).isNull()
    ).count()
    checks["no_null_keys"] = {
        "passed": null_check == 0,
        "details": f"{null_check} records with null in key columns"
    }

    # 2. All ages in realistic range (already filtered, but double-check)
    invalid_age = df.filter(
        (col(age_col) < 0) | (col(age_col) > 120)
    ).count()
    checks["age_range"] = {
        "passed": invalid_age == 0,
        "details": f"{invalid_age} invalid ages"
    }

    # 3. No duplicates on member_id
    dup_count = df.groupBy(member_id_col).agg(count("*").alias("cnt")) \
                  .filter(col("cnt") > 1).count()
    checks["no_duplicates"] = {
        "passed": dup_count == 0,
        "details": f"{dup_count} duplicate member_ids"
    }

    # 4. Eligibility status is meaningful
    invalid_status = df.filter(
        ~col(status_col).isin(["ACTIVE", "TERMINATED", "UNKNOWN"])
    ).count()
    checks["valid_status"] = {
        "passed": invalid_status == 0,
        "details": f"{invalid_status} invalid eligibility statuses"
    }

    # Overall pass/fail
    all_passed = all(check["passed"] for check in checks.values())
    checks["overall"] = {"passed": all_passed, "details": "All checks passed" if all_passed else "Some checks failed"}

    return checks