import csv
import pandas as pd
from typing import List, Dict, Optional
from pyspark.sql import DataFrame
from src.aws_clients.s3_client import S3Client


class S3DataValidator:
    """S3 data ingestion validator for file schema, size, required columns."""

    def __init__(self, s3_client: Optional[S3Client] = None, bucket_name: str = 'my-etl-bucket-test1'):
        self.s3_client = s3_client or S3Client(bucket_name=bucket_name)
        self.bucket_name = bucket_name
        self.errors = []

    def validate_file_exists(self, key: str) -> bool:
        """Check if file exists in S3."""
        exists = self.s3_client.file_exists(key, self.bucket_name)
        if not exists:
            self.errors.append(f"File does not exist: s3://{self.bucket_name}/{key}")
        return exists

    def validate_file_size(self, key: str, min_size_bytes: int = 1, max_size_bytes: Optional[int] = None) -> bool:
        """Validate file size is within bounds."""
        try:
            size = self.s3_client.get_file_size(key, self.bucket_name)
            if size < min_size_bytes:
                self.errors.append(f"File size ({size} bytes) is below minimum ({min_size_bytes} bytes)")
                return False
            if max_size_bytes and size > max_size_bytes:
                self.errors.append(f"File size ({size} bytes) exceeds maximum ({max_size_bytes} bytes)")
                return False
            return True
        except Exception as e:
            self.errors.append(f"Error checking file size: {str(e)}")
            return False

    def validate_csv_schema(self, key: str, required_columns: List[str]) -> bool:
        """Validate CSV has required columns."""
        try:
            content = self.s3_client.read_file(key, self.bucket_name)
            reader = csv.DictReader(content.strip().split('\n'))
            if reader.fieldnames is None:
                self.errors.append("CSV has no headers")
                return False
            
            missing = set(required_columns) - set(reader.fieldnames)
            if missing:
                self.errors.append(f"Missing required columns: {missing}")
                return False
            return True
        except Exception as e:
            self.errors.append(f"Error validating schema: {str(e)}")
            return False

    def validate_csv_has_rows(self, key: str, min_rows: int = 1) -> bool:
        """Validate CSV has minimum row count."""
        try:
            content = self.s3_client.read_file(key, self.bucket_name)
            lines = content.strip().split('\n')
            row_count = len(lines) - 1  # subtract header
            if row_count < min_rows:
                self.errors.append(f"CSV has {row_count} rows, minimum required: {min_rows}")
                return False
            return True
        except Exception as e:
            self.errors.append(f"Error counting rows: {str(e)}")
            return False

    def validate_no_nulls_in_column(self, key: str, column_name: str) -> bool:
        """Validate column has no null/empty values."""
        try:
            content = self.s3_client.read_file(key, self.bucket_name)
            reader = csv.DictReader(content.strip().split('\n'))
            null_count = 0
            for row in reader:
                if not row.get(column_name) or row.get(column_name).strip() == '':
                    null_count += 1
            if null_count > 0:
                self.errors.append(f"Column '{column_name}' has {null_count} null/empty values")
                return False
            return True
        except Exception as e:
            self.errors.append(f"Error validating column nulls: {str(e)}")
            return False

    def validate_column_values(self, key: str, column_name: str, allowed_values: List[str]) -> bool:
        """Validate column values are in allowed list."""
        try:
            content = self.s3_client.read_file(key, self.bucket_name)
            reader = csv.DictReader(content.strip().split('\n'))
            invalid_count = 0
            for row in reader:
                value = row.get(column_name, '').strip()
                if value and value not in allowed_values:
                    invalid_count += 1
            if invalid_count > 0:
                self.errors.append(f"Column '{column_name}' has {invalid_count} values not in {allowed_values}")
                return False
            return True
        except Exception as e:
            self.errors.append(f"Error validating column values: {str(e)}")
            return False

    def get_errors(self) -> List[str]:
        """Return list of validation errors."""
        return self.errors

    def clear_errors(self):
        """Clear error list."""
        self.errors = []

    def validate_all(self, key: str, required_columns: List[str], min_rows: int = 1) -> Dict[str, bool]:
        """Run all validations and return summary."""
        self.clear_errors()
        results = {
            'file_exists': self.validate_file_exists(key),
            'file_size': self.validate_file_size(key),
            'schema': self.validate_csv_schema(key, required_columns),
            'has_rows': self.validate_csv_has_rows(key, min_rows)
        }
        return results
