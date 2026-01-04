import pytest
import json
from src.aws_clients.lambda_client import LambdaClient, LambdaValidator
from unittest.mock import Mock, patch


def test_lambda_client_list_functions():
    """Test Lambda client list functions."""
    with patch('boto3.client') as mock_boto:
        mock_lambda = Mock()
        mock_boto.return_value = mock_lambda
        
        # Mock paginator
        mock_paginator = Mock()
        mock_lambda.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {'Functions': [{'FunctionName': 'func1'}, {'FunctionName': 'func2'}]}
        ]
        
        client = LambdaClient()
        functions = client.list_functions()
        assert len(functions) == 2


def test_lambda_client_get_function():
    """Test Lambda client get function."""
    with patch('boto3.client') as mock_boto:
        mock_lambda = Mock()
        mock_boto.return_value = mock_lambda
        mock_lambda.get_function.return_value = {
            'Configuration': {'FunctionName': 'test-func', 'Runtime': 'python3.9'}
        }
        
        client = LambdaClient()
        func = client.get_function('test-func')
        assert func['FunctionName'] == 'test-func'


def test_lambda_client_invoke_success():
    """Test Lambda client invoke function."""
    with patch('boto3.client') as mock_boto:
        mock_lambda = Mock()
        mock_boto.return_value = mock_lambda
        mock_lambda.invoke.return_value = {
            'StatusCode': 200,
            'Payload': Mock(read=Mock(return_value=json.dumps({'status': 'ok'}).encode()))
        }
        
        client = LambdaClient()
        response = client.invoke_function('test-func', {})
        assert response['StatusCode'] == 200


def test_lambda_validator_function_exists():
    """Test Lambda validator checks function existence."""
    with patch('boto3.client') as mock_boto:
        mock_lambda = Mock()
        mock_boto.return_value = mock_lambda
        mock_lambda.get_function.return_value = {
            'Configuration': {'FunctionName': 'test-func'}
        }
        
        client = LambdaClient()
        validator = LambdaValidator(client)
        assert validator.validate_function_exists('test-func')


def test_lambda_validator_function_not_exists():
    """Test Lambda validator detects missing function."""
    with patch('boto3.client') as mock_boto:
        mock_lambda = Mock()
        mock_boto.return_value = mock_lambda
        mock_lambda.get_function.return_value = {}
        
        client = LambdaClient()
        validator = LambdaValidator(client)
        assert not validator.validate_function_exists('missing-func')


def test_lambda_validator_invocation_succeeds():
    """Test Lambda validator checks successful invocation."""
    with patch('boto3.client') as mock_boto:
        mock_lambda = Mock()
        mock_boto.return_value = mock_lambda
        mock_lambda.invoke.return_value = {
            'StatusCode': 200,
            'Payload': Mock(read=Mock(return_value=json.dumps({'status': 'ok'}).encode()))
        }
        
        client = LambdaClient()
        validator = LambdaValidator(client)
        assert validator.validate_invocation_success('test-func', {})


def test_lambda_validator_invocation_fails():
    """Test Lambda validator detects failed invocation."""
    with patch('boto3.client') as mock_boto:
        mock_lambda = Mock()
        mock_boto.return_value = mock_lambda
        mock_lambda.invoke.return_value = {
            'StatusCode': 500,
            'Payload': Mock(read=Mock(return_value=json.dumps({'status': 'error'}).encode()))
        }
        
        client = LambdaClient()
        validator = LambdaValidator(client)
        assert not validator.validate_invocation_success('test-func', {})


def test_lambda_validator_no_errors_in_response():
    """Test Lambda validator detects errors in execution."""
    with patch('boto3.client') as mock_boto:
        mock_lambda = Mock()
        mock_boto.return_value = mock_lambda
        mock_lambda.invoke.return_value = {
            'StatusCode': 200,
            'Payload': Mock(read=Mock(return_value=json.dumps({'status': 'ok'}).encode()))
        }
        
        client = LambdaClient()
        validator = LambdaValidator(client)
        
        # Test successful execution
        assert validator.validate_no_errors_in_execution('test-func', {})
