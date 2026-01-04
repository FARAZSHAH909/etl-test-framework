import pytest
from src.aws_clients.glue_client import GlueClient, GlueJobValidator
from unittest.mock import Mock, patch


def test_glue_client_list_jobs():
    """Test Glue client list jobs."""
    with patch('boto3.client') as mock_boto:
        mock_glue = Mock()
        mock_boto.return_value = mock_glue
        mock_glue.list_jobs.return_value = {'JobNames': ['job1', 'job2']}
        
        client = GlueClient()
        jobs = client.list_jobs()
        assert jobs == ['job1', 'job2']


def test_glue_client_get_job():
    """Test Glue client get job."""
    with patch('boto3.client') as mock_boto:
        mock_glue = Mock()
        mock_boto.return_value = mock_glue
        mock_glue.get_job.return_value = {'Job': {'Name': 'test-job', 'Role': 'role-arn'}}
        
        client = GlueClient()
        job = client.get_job('test-job')
        assert job['Name'] == 'test-job'


def test_glue_validator_job_exists():
    """Test Glue validator checks job existence."""
    with patch('boto3.client') as mock_boto:
        mock_glue = Mock()
        mock_boto.return_value = mock_glue
        mock_glue.get_job.return_value = {'Job': {'Name': 'test-job'}}
        
        client = GlueClient()
        validator = GlueJobValidator(client)
        assert validator.validate_job_exists('test-job')


def test_glue_validator_job_not_exists():
    """Test Glue validator detects missing job."""
    with patch('boto3.client') as mock_boto:
        mock_glue = Mock()
        mock_boto.return_value = mock_glue
        mock_glue.get_job.return_value = {}
        
        client = GlueClient()
        validator = GlueJobValidator(client)
        assert not validator.validate_job_exists('missing-job')
        assert len(validator.get_errors()) > 0


def test_glue_validator_job_succeeded():
    """Test Glue validator checks job run success."""
    with patch('boto3.client') as mock_boto:
        mock_glue = Mock()
        mock_boto.return_value = mock_glue
        mock_glue.get_job_run.return_value = {'JobRun': {'JobRunState': 'SUCCEEDED'}}
        
        client = GlueClient()
        validator = GlueJobValidator(client)
        assert validator.validate_job_run_succeeded('test-job', 'run-id')


def test_glue_validator_job_failed():
    """Test Glue validator detects failed job run."""
    with patch('boto3.client') as mock_boto:
        mock_glue = Mock()
        mock_boto.return_value = mock_glue
        mock_glue.get_job_run.return_value = {'JobRun': {'JobRunState': 'FAILED'}}
        
        client = GlueClient()
        validator = GlueJobValidator(client)
        assert not validator.validate_job_run_succeeded('test-job', 'run-id')
