import boto3
from botocore.exceptions import ClientError
from typing import Optional, List


class S3Client:
    """S3 client wrapper for file operations and validation."""

    def __init__(self, region_name: str = 'us-east-1', bucket_name: Optional[str] = None):
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.s3_resource = boto3.resource('s3', region_name=region_name)
        self.bucket_name = bucket_name

    def bucket_exists(self, bucket_name: Optional[str] = None) -> bool:
        """Check if S3 bucket exists."""
        bucket = bucket_name or self.bucket_name
        try:
            self.s3_client.head_bucket(Bucket=bucket)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def file_exists(self, key: str, bucket_name: Optional[str] = None) -> bool:
        """Check if file exists in S3."""
        bucket = bucket_name or self.bucket_name
        try:
            self.s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def get_file_size(self, key: str, bucket_name: Optional[str] = None) -> int:
        """Get file size in bytes."""
        bucket = bucket_name or self.bucket_name
        response = self.s3_client.head_object(Bucket=bucket, Key=key)
        return response['ContentLength']

    def list_files(self, prefix: str = '', bucket_name: Optional[str] = None) -> List[str]:
        """List files in bucket with optional prefix."""
        bucket = bucket_name or self.bucket_name
        paginator = self.s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        files = []
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    files.append(obj['Key'])
        return files

    def read_file(self, key: str, bucket_name: Optional[str] = None) -> str:
        """Read file content from S3."""
        bucket = bucket_name or self.bucket_name
        response = self.s3_client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read().decode('utf-8')

    def upload_file(self, local_path: str, key: str, bucket_name: Optional[str] = None) -> bool:
        """Upload file to S3."""
        bucket = bucket_name or self.bucket_name
        try:
            self.s3_client.upload_file(local_path, bucket, key)
            return True
        except ClientError as e:
            print(f"Upload failed: {e}")
            return False

    def delete_file(self, key: str, bucket_name: Optional[str] = None) -> bool:
        """Delete file from S3."""
        bucket = bucket_name or self.bucket_name
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            print(f"Delete failed: {e}")
            return False

    def create_bucket(self, bucket_name: str, region_name: str = 'us-east-1') -> bool:
        """Create S3 bucket."""
        try:
            if region_name == 'us-east-1':
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region_name}
                )
            self.bucket_name = bucket_name
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                print(f"Bucket {bucket_name} already exists.")
                self.bucket_name = bucket_name
                return True
            print(f"Bucket creation failed: {e}")
            return False
