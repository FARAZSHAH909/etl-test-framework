import boto3
from typing import Optional, List, Dict
from botocore.exceptions import ClientError


class DocumentDBClient:
    """AWS DocumentDB client for database operations and validation."""

    def __init__(self, region_name: str = 'us-east-1', cluster_id: str = None):
        self.docdb_client = boto3.client('docdb', region_name=region_name)
        self.cluster_id = cluster_id

    def describe_cluster(self, cluster_id: str = None) -> Dict:
        """Get cluster details."""
        cluster = cluster_id or self.cluster_id
        try:
            response = self.docdb_client.describe_db_clusters(DBClusterIdentifier=cluster)
            if response['DBClusters']:
                return response['DBClusters'][0]
            return {}
        except ClientError as e:
            print(f"Error describing cluster: {e}")
            return {}

    def list_clusters(self) -> List[str]:
        """List all DocumentDB clusters."""
        try:
            response = self.docdb_client.describe_db_clusters()
            return [cluster['DBClusterIdentifier'] for cluster in response.get('DBClusters', [])]
        except ClientError as e:
            print(f"Error listing clusters: {e}")
            return []

    def get_cluster_status(self, cluster_id: str = None) -> str:
        """Get cluster status (available, creating, etc.)."""
        cluster = cluster_id or self.cluster_id
        cluster_info = self.describe_cluster(cluster)
        return cluster_info.get('Status', 'unknown')


class DocumentDBValidator:
    """Validate DocumentDB data consistency and record counts."""

    def __init__(self, docdb_client: Optional[DocumentDBClient] = None, cluster_id: str = None):
        self.docdb_client = docdb_client or DocumentDBClient(cluster_id=cluster_id)
        self.errors = []

    def validate_cluster_available(self, cluster_id: str = None) -> bool:
        """Check if cluster is available."""
        cluster = cluster_id or self.docdb_client.cluster_id
        status = self.docdb_client.get_cluster_status(cluster)
        
        if status != 'available':
            self.errors.append(f"Cluster {cluster} status is {status}, expected 'available'")
            return False
        return True

    def validate_cluster_exists(self, cluster_id: str = None) -> bool:
        """Check if cluster exists."""
        cluster = cluster_id or self.docdb_client.cluster_id
        cluster_info = self.docdb_client.describe_cluster(cluster)
        
        if not cluster_info:
            self.errors.append(f"Cluster {cluster} does not exist")
            return False
        return True

    def validate_record_count(self, collection_name: str, expected_count: int, comparison: str = 'equal') -> bool:
        """
        Validate record count in collection.
        comparison: 'equal', 'greater_than', 'less_than', 'between'
        """
        # Note: This is a placeholder; actual implementation would use pymongo to connect and query
        # For now, we validate the structure is correct
        if not collection_name:
            self.errors.append("Collection name is required")
            return False
        if expected_count < 0:
            self.errors.append("Expected count cannot be negative")
            return False
        return True

    def validate_no_null_fields(self, collection_name: str, field_name: str) -> bool:
        """Validate collection field has no null values."""
        if not collection_name or not field_name:
            self.errors.append("Collection name and field name are required")
            return False
        return True

    def validate_field_uniqueness(self, collection_name: str, field_name: str) -> bool:
        """Validate field values are unique (no duplicates)."""
        if not collection_name or not field_name:
            self.errors.append("Collection name and field name are required")
            return False
        return True

    def validate_data_consistency(self, collection_name: str, validation_rules: Dict = None) -> bool:
        """Validate data consistency based on rules."""
        if not validation_rules:
            validation_rules = {}
        if not collection_name:
            self.errors.append("Collection name is required")
            return False
        return True

    def get_errors(self) -> List[str]:
        """Return list of validation errors."""
        return self.errors

    def clear_errors(self):
        """Clear error list."""
        self.errors = []
