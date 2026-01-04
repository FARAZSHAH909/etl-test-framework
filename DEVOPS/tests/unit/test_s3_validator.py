import pytest
import tempfile
import os
from src.aws_clients.s3_client import S3Client
from src.validators.s3_validator import S3DataValidator
from moto import mock_aws
import boto3


@mock_aws
def test_s3_client_bucket_exists():
    """Test S3 bucket exists check."""
    s3 = S3Client(bucket_name='test-bucket')
    s3.create_bucket('test-bucket', 'us-east-1')
    assert s3.bucket_exists('test-bucket')


@mock_aws
def test_s3_client_bucket_not_exists():
    """Test S3 bucket not exists check."""
    s3 = S3Client()
    assert not s3.bucket_exists('nonexistent-bucket')


@mock_aws
def test_s3_client_upload_file():
    """Test S3 file upload."""
    s3 = S3Client(bucket_name='test-bucket')
    s3.create_bucket('test-bucket', 'us-east-1')
    
    # Create a test file in temp directory
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('col1,col2\n1,2\n')
        temp_path = f.name
    
    try:
        result = s3.upload_file(temp_path, 'test.csv', 'test-bucket')
        assert result is True
    finally:
        os.unlink(temp_path)


@mock_aws
def test_s3_validator_file_exists():
    """Test S3 validator file existence check."""
    s3 = S3Client(bucket_name='test-bucket')
    s3.create_bucket('test-bucket', 'us-east-1')
    
    # Upload test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('member_id,status,age,enrollment_date\nM001,ACTIVE,45,2025-01-01\n')
        temp_path = f.name
    
    try:
        s3.upload_file(temp_path, 'test.csv', 'test-bucket')
        
        validator = S3DataValidator(s3, 'test-bucket')
        assert validator.validate_file_exists('test.csv')
    finally:
        os.unlink(temp_path)


@mock_aws
def test_s3_validator_schema():
    """Test S3 validator schema check."""
    s3 = S3Client(bucket_name='test-bucket')
    s3.create_bucket('test-bucket', 'us-east-1')
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('member_id,status,age,enrollment_date\nM001,ACTIVE,45,2025-01-01\n')
        temp_path = f.name
    
    try:
        s3.upload_file(temp_path, 'test.csv', 'test-bucket')
        
        validator = S3DataValidator(s3, 'test-bucket')
        required_cols = ['member_id', 'status', 'age', 'enrollment_date']
        assert validator.validate_csv_schema('test.csv', required_cols)
    finally:
        os.unlink(temp_path)


@mock_aws
def test_s3_validator_missing_column():
    """Test S3 validator detects missing columns."""
    s3 = S3Client(bucket_name='test-bucket')
    s3.create_bucket('test-bucket', 'us-east-1')
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('member_id,status\nM001,ACTIVE\n')
        temp_path = f.name
    
    try:
        s3.upload_file(temp_path, 'test.csv', 'test-bucket')
        
        validator = S3DataValidator(s3, 'test-bucket')
        required_cols = ['member_id', 'status', 'age']
        assert not validator.validate_csv_schema('test.csv', required_cols)
        assert len(validator.get_errors()) > 0
    finally:
        os.unlink(temp_path)
