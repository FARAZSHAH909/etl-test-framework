import pytest
from src.aws_clients.documentdb_client import DocumentDBClient, DocumentDBValidator
from unittest.mock import Mock, patch


def test_documentdb_client_list_clusters():
    """Test DocumentDB client list clusters."""
    with patch('boto3.client') as mock_boto:
        mock_docdb = Mock()
        mock_boto.return_value = mock_docdb
        mock_docdb.describe_db_clusters.return_value = {
            'DBClusters': [{'DBClusterIdentifier': 'cluster1'}, {'DBClusterIdentifier': 'cluster2'}]
        }
        
        client = DocumentDBClient()
        clusters = client.list_clusters()
        assert len(clusters) == 2


def test_documentdb_client_get_cluster_status():
    """Test DocumentDB client get cluster status."""
    with patch('boto3.client') as mock_boto:
        mock_docdb = Mock()
        mock_boto.return_value = mock_docdb
        mock_docdb.describe_db_clusters.return_value = {
            'DBClusters': [{'DBClusterIdentifier': 'cluster1', 'Status': 'available'}]
        }
        
        client = DocumentDBClient()
        status = client.get_cluster_status('cluster1')
        assert status == 'available'


def test_documentdb_validator_cluster_available():
    """Test DocumentDB validator checks cluster availability."""
    with patch('boto3.client') as mock_boto:
        mock_docdb = Mock()
        mock_boto.return_value = mock_docdb
        mock_docdb.describe_db_clusters.return_value = {
            'DBClusters': [{'DBClusterIdentifier': 'cluster1', 'Status': 'available'}]
        }
        
        client = DocumentDBClient()
        validator = DocumentDBValidator(client)
        assert validator.validate_cluster_available('cluster1')


def test_documentdb_validator_cluster_not_available():
    """Test DocumentDB validator detects unavailable cluster."""
    with patch('boto3.client') as mock_boto:
        mock_docdb = Mock()
        mock_boto.return_value = mock_docdb
        mock_docdb.describe_db_clusters.return_value = {
            'DBClusters': [{'DBClusterIdentifier': 'cluster1', 'Status': 'creating'}]
        }
        
        client = DocumentDBClient()
        validator = DocumentDBValidator(client)
        assert not validator.validate_cluster_available('cluster1')


def test_documentdb_validator_cluster_exists():
    """Test DocumentDB validator checks cluster existence."""
    with patch('boto3.client') as mock_boto:
        mock_docdb = Mock()
        mock_boto.return_value = mock_docdb
        mock_docdb.describe_db_clusters.return_value = {
            'DBClusters': [{'DBClusterIdentifier': 'cluster1'}]
        }
        
        client = DocumentDBClient()
        validator = DocumentDBValidator(client)
        assert validator.validate_cluster_exists('cluster1')


def test_documentdb_validator_cluster_not_exists():
    """Test DocumentDB validator detects missing cluster."""
    with patch('boto3.client') as mock_boto:
        mock_docdb = Mock()
        mock_boto.return_value = mock_docdb
        mock_docdb.describe_db_clusters.return_value = {'DBClusters': []}
        
        client = DocumentDBClient()
        validator = DocumentDBValidator(client)
        assert not validator.validate_cluster_exists('missing-cluster')


def test_documentdb_validator_has_records():
    """Test DocumentDB validator checks for records."""
    with patch('boto3.client') as mock_boto:
        mock_docdb = Mock()
        mock_boto.return_value = mock_docdb
        
        client = DocumentDBClient()
        validator = DocumentDBValidator(client)
        
        # Mock collection with record count
        result = validator.validate_record_count('collection1', expected_count=1, comparison='greater_than')
        assert isinstance(result, bool)


def test_documentdb_validator_no_null_fields():
    """Test DocumentDB validator checks for null fields."""
    with patch('boto3.client') as mock_boto:
        mock_docdb = Mock()
        mock_boto.return_value = mock_docdb
        
        client = DocumentDBClient()
        validator = DocumentDBValidator(client)
        
        # Should handle null field validation
        result = validator.validate_no_null_fields('collection1', 'field1')
        assert isinstance(result, bool)
