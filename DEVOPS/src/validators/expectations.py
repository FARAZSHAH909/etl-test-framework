"""
Great Expectations integration for ETL data quality rules.
Provides expectation suite definitions and validation.
"""

from typing import Dict, List, Any
import pandas as pd


class ExpectationSuite:
    """Great Expectations-style validation suite for data quality."""

    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.expectations = []

    def expect_column_values_to_be_in_set(self, column: str, value_set: List[str]) -> Dict[str, Any]:
        """Expect column values to be in a defined set."""
        expectation = {
            "expectation_type": "expect_column_values_to_be_in_set",
            "kwargs": {
                "column": column,
                "value_set": value_set
            }
        }
        self.expectations.append(expectation)
        return expectation

    def expect_column_values_to_be_between(self, column: str, min_value: float, max_value: float) -> Dict[str, Any]:
        """Expect column values to be between min and max."""
        expectation = {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {
                "column": column,
                "min_value": min_value,
                "max_value": max_value
            }
        }
        self.expectations.append(expectation)
        return expectation

    def expect_column_to_exist(self, column: str) -> Dict[str, Any]:
        """Expect column to exist in data."""
        expectation = {
            "expectation_type": "expect_column_to_exist",
            "kwargs": {"column": column}
        }
        self.expectations.append(expectation)
        return expectation

    def expect_column_values_to_not_be_null(self, column: str) -> Dict[str, Any]:
        """Expect column to have no null values."""
        expectation = {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": column}
        }
        self.expectations.append(expectation)
        return expectation

    def expect_table_row_count_to_be_between(self, min_value: int, max_value: int) -> Dict[str, Any]:
        """Expect table row count to be between min and max."""
        expectation = {
            "expectation_type": "expect_table_row_count_to_be_between",
            "kwargs": {
                "min_value": min_value,
                "max_value": max_value
            }
        }
        self.expectations.append(expectation)
        return expectation

    def expect_column_values_to_match_regex(self, column: str, regex: str) -> Dict[str, Any]:
        """Expect column values to match a regex pattern."""
        expectation = {
            "expectation_type": "expect_column_values_to_match_regex",
            "kwargs": {
                "column": column,
                "regex": regex
            }
        }
        self.expectations.append(expectation)
        return expectation

    def get_expectations(self) -> List[Dict[str, Any]]:
        """Return list of all expectations."""
        return self.expectations


class ExpectationValidator:
    """Validate data against expectation suite."""

    def __init__(self, suite: ExpectationSuite):
        self.suite = suite
        self.validation_results = {}

    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Validate pandas DataFrame against expectation suite."""
        results = {}

        for expectation in self.suite.get_expectations():
            exp_type = expectation["expectation_type"]
            kwargs = expectation["kwargs"]

            if exp_type == "expect_column_to_exist":
                results[f"{exp_type}_{kwargs['column']}"] = kwargs['column'] in df.columns

            elif exp_type == "expect_column_values_to_not_be_null":
                col = kwargs['column']
                results[f"{exp_type}_{col}"] = df[col].isna().sum() == 0

            elif exp_type == "expect_column_values_to_be_in_set":
                col = kwargs['column']
                value_set = kwargs['value_set']
                results[f"{exp_type}_{col}"] = df[col].isin(value_set).all()

            elif exp_type == "expect_column_values_to_be_between":
                col = kwargs['column']
                min_val = kwargs['min_value']
                max_val = kwargs['max_value']
                results[f"{exp_type}_{col}"] = ((df[col] >= min_val) & (df[col] <= max_val)).all()

            elif exp_type == "expect_table_row_count_to_be_between":
                min_rows = kwargs['min_value']
                max_rows = kwargs['max_value']
                row_count = len(df)
                results["expect_table_row_count_to_be_between"] = (min_rows <= row_count <= max_rows)

            elif exp_type == "expect_column_values_to_match_regex":
                col = kwargs['column']
                regex = kwargs['regex']
                import re
                results[f"{exp_type}_{col}"] = df[col].astype(str).str.match(regex).all()

        self.validation_results = results
        return results

    def all_passed(self) -> bool:
        """Check if all validations passed."""
        return all(self.validation_results.values())

    def get_failed_expectations(self) -> List[str]:
        """Return list of failed expectations."""
        return [key for key, passed in self.validation_results.items() if not passed]


def create_member_data_expectations() -> ExpectationSuite:
    """Create expectation suite for member data ETL."""
    suite = ExpectationSuite("member_data_quality")
    
    # Column existence
    suite.expect_column_to_exist("member_id")
    suite.expect_column_to_exist("status")
    suite.expect_column_to_exist("age")
    suite.expect_column_to_exist("enrollment_date")
    
    # No nulls in key columns
    suite.expect_column_values_to_not_be_null("member_id")
    
    # Valid status values
    suite.expect_column_values_to_be_in_set("status", ["ACTIVE", "TERMINATED", "UNKNOWN"])
    
    # Age range (0-120)
    suite.expect_column_values_to_be_between("age", 0, 120)
    
    # Member ID format (M followed by digits)
    suite.expect_column_values_to_match_regex("member_id", r"^M\d+$")
    
    # Minimum rows
    suite.expect_table_row_count_to_be_between(1, 10000)
    
    return suite
