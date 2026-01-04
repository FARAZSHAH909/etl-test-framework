import pytest
from src.validators.expectations import ExpectationSuite, ExpectationValidator, create_member_data_expectations
import pandas as pd


def test_expectation_suite_creation():
    """Test creating expectation suite."""
    suite = ExpectationSuite("test_suite")
    assert suite.suite_name == "test_suite"
    assert len(suite.get_expectations()) == 0


def test_expectation_column_exists():
    """Test column existence expectation."""
    suite = ExpectationSuite("test")
    suite.expect_column_to_exist("member_id")
    expectations = suite.get_expectations()
    assert len(expectations) == 1
    assert expectations[0]["expectation_type"] == "expect_column_to_exist"


def test_expectation_values_in_set():
    """Test column values in set expectation."""
    suite = ExpectationSuite("test")
    suite.expect_column_values_to_be_in_set("status", ["ACTIVE", "TERMINATED"])
    expectations = suite.get_expectations()
    assert len(expectations) == 1
    assert expectations[0]["kwargs"]["value_set"] == ["ACTIVE", "TERMINATED"]


def test_validator_column_exists():
    """Test validator checks column existence."""
    suite = ExpectationSuite("test")
    suite.expect_column_to_exist("member_id")
    
    df = pd.DataFrame({'member_id': [1, 2], 'name': ['A', 'B']})
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert results['expect_column_to_exist_member_id'] is True


def test_validator_column_not_exists():
    """Test validator detects missing column."""
    suite = ExpectationSuite("test")
    suite.expect_column_to_exist("missing_col")
    
    df = pd.DataFrame({'member_id': [1, 2]})
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert results['expect_column_to_exist_missing_col'] is False


def test_validator_no_nulls():
    """Test validator checks for null values."""
    suite = ExpectationSuite("test")
    suite.expect_column_values_to_not_be_null("member_id")
    
    df = pd.DataFrame({'member_id': ['M001', 'M002']})
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert results['expect_column_values_to_not_be_null_member_id'] == True


def test_validator_with_nulls():
    """Test validator detects null values."""
    suite = ExpectationSuite("test")
    suite.expect_column_values_to_not_be_null("member_id")
    
    df = pd.DataFrame({'member_id': ['M001', None]})
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert results['expect_column_values_to_not_be_null_member_id'] == False


def test_validator_values_in_set():
    """Test validator checks value membership."""
    suite = ExpectationSuite("test")
    suite.expect_column_values_to_be_in_set("status", ["ACTIVE", "TERMINATED"])
    
    df = pd.DataFrame({'status': ['ACTIVE', 'TERMINATED']})
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert results['expect_column_values_to_be_in_set_status'] == True


def test_validator_values_not_in_set():
    """Test validator detects invalid values."""
    suite = ExpectationSuite("test")
    suite.expect_column_values_to_be_in_set("status", ["ACTIVE", "TERMINATED"])
    
    df = pd.DataFrame({'status': ['ACTIVE', 'INVALID']})
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert results['expect_column_values_to_be_in_set_status'] == False


def test_validator_values_between():
    """Test validator checks numeric ranges."""
    suite = ExpectationSuite("test")
    suite.expect_column_values_to_be_between("age", 0, 120)
    
    df = pd.DataFrame({'age': [45, 80]})
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert results['expect_column_values_to_be_between_age'] == True


def test_validator_values_outside_range():
    """Test validator detects out-of-range values."""
    suite = ExpectationSuite("test")
    suite.expect_column_values_to_be_between("age", 0, 120)
    
    df = pd.DataFrame({'age': [45, 130]})
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert results['expect_column_values_to_be_between_age'] == False


def test_member_data_expectations():
    """Test member data expectation suite."""
    suite = create_member_data_expectations()
    assert len(suite.get_expectations()) > 0
    
    df = pd.DataFrame({
        'member_id': ['M001', 'M002'],
        'status': ['ACTIVE', 'TERMINATED'],
        'age': [45, 80],
        'enrollment_date': ['2025-01-01', '2025-01-02']
    })
    
    validator = ExpectationValidator(suite)
    results = validator.validate_dataframe(df)
    
    assert validator.all_passed()
