import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
import json


class LambdaClient:
    """AWS Lambda client for function invocation and testing."""

    def __init__(self, region_name: str = 'us-east-1'):
        self.lambda_client = boto3.client('lambda', region_name=region_name)

    def invoke_function(self, function_name: str, payload: Dict = None, invocation_type: str = 'RequestResponse') -> Dict:
        """Invoke a Lambda function."""
        try:
            kwargs = {
                'FunctionName': function_name,
                'InvocationType': invocation_type
            }
            if payload:
                kwargs['Payload'] = json.dumps(payload)
            
            response = self.lambda_client.invoke(**kwargs)
            if 'Payload' in response:
                payload_str = response['Payload'].read().decode('utf-8')
                response['Payload'] = json.loads(payload_str) if payload_str else {}
            return response
        except ClientError as e:
            print(f"Error invoking Lambda: {e}")
            return {'StatusCode': 500, 'Error': str(e)}

    def get_function(self, function_name: str) -> Dict:
        """Get Lambda function details."""
        try:
            response = self.lambda_client.get_function(FunctionName=function_name)
            return response.get('Configuration', {})
        except ClientError as e:
            print(f"Error getting function: {e}")
            return {}

    def list_functions(self) -> list:
        """List all Lambda functions."""
        try:
            paginator = self.lambda_client.get_paginator('list_functions')
            functions = []
            for page in paginator.paginate():
                functions.extend(page.get('Functions', []))
            return functions
        except ClientError as e:
            print(f"Error listing functions: {e}")
            return []


class LambdaValidator:
    """Validate Lambda function execution and errors."""

    def __init__(self, lambda_client: Optional[LambdaClient] = None):
        self.lambda_client = lambda_client or LambdaClient()
        self.errors = []

    def validate_function_exists(self, function_name: str) -> bool:
        """Check if Lambda function exists."""
        func = self.lambda_client.get_function(function_name)
        if not func:
            self.errors.append(f"Lambda function '{function_name}' does not exist")
            return False
        return True

    def validate_invocation_success(self, function_name: str, payload: Dict = None) -> bool:
        """Validate Lambda function execution succeeded."""
        response = self.lambda_client.invoke_function(function_name, payload)
        status_code = response.get('StatusCode')
        
        if status_code != 200:
            self.errors.append(f"Lambda invocation returned status {status_code}")
            return False
        
        # Check for function errors
        if 'FunctionError' in response:
            error_msg = response.get('Payload', {}).get('errorMessage', 'Unknown error')
            self.errors.append(f"Lambda function error: {error_msg}")
            return False
        
        return True

    def validate_invocation_response_structure(self, function_name: str, payload: Dict = None, expected_keys: list = None) -> bool:
        """Validate Lambda response has expected structure."""
        response = self.lambda_client.invoke_function(function_name, payload)
        payload_data = response.get('Payload', {})
        
        if expected_keys:
            missing_keys = set(expected_keys) - set(payload_data.keys())
            if missing_keys:
                self.errors.append(f"Lambda response missing keys: {missing_keys}")
                return False
        
        return True

    def validate_no_errors_in_execution(self, function_name: str, payload: Dict = None) -> bool:
        """Check that Lambda execution has no errors."""
        response = self.lambda_client.invoke_function(function_name, payload)
        
        if response.get('StatusCode') != 200:
            self.errors.append(f"Lambda returned error status {response.get('StatusCode')}")
            return False
        
        if 'FunctionError' in response:
            self.errors.append("Lambda function execution failed")
            return False
        
        return True

    def get_errors(self) -> list:
        """Return list of validation errors."""
        return self.errors

    def clear_errors(self):
        """Clear error list."""
        self.errors = []
