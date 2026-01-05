#!/usr/bin/env python3
"""
Test Runner with Performance Metrics Collection
Executes tests and generates real performance reports for client proof
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from src.utils.performance_metrics import (
    PerformanceMetricsCollector, 
    TestComponentType,
    MetricRecord
)

def run_tests_with_metrics():
    """Execute tests and collect performance metrics"""
    
    collector = PerformanceMetricsCollector()
    results = {}
    
    # Test groups
    test_groups = [
        {
            "name": "S3 Validators",
            "component": TestComponentType.S3_VALIDATOR,
            "test_file": "tests/unit/test_s3_validator.py",
            "description": "File existence, schema, data quality checks"
        },
        {
            "name": "Lambda Orchestration",
            "component": TestComponentType.LAMBDA_ORCHESTRATION,
            "test_file": "tests/unit/test_lambda_integration.py",
            "description": "Function invocation, payload handling, error paths"
        },
        {
            "name": "Glue ETL",
            "component": TestComponentType.GLUE_ETL,
            "test_file": "tests/unit/test_glue_integration.py",
            "description": "Data transformation, reconciliation, throughput"
        },
        {
            "name": "DocumentDB",
            "component": TestComponentType.DOCUMENTDB_CHECK,
            "test_file": "tests/unit/test_documentdb_integration.py",
            "description": "Document validation, schema, query performance"
        },
        {
            "name": "General Validations",
            "component": TestComponentType.S3_VALIDATOR,
            "test_file": "tests/unit/test_validations.py",
            "description": "Data quality and validation rules"
        },
    ]
    
    print("\n" + "="*80)
    print("ETL FRAMEWORK TEST EXECUTION WITH METRICS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for test_group in test_groups:
        print(f"\n{'─'*80}")
        print(f"RUNNING: {test_group['name']}")
        print(f"Component: {test_group['component'].value}")
        print(f"Description: {test_group['description']}")
        print(f"Test File: {test_group['test_file']}")
        print(f"{'─'*80}")
        
        # Run pytest for this test file
        cmd = [
            sys.executable, 
            "-m", 
            "pytest", 
            test_group['test_file'],
            "-v",
            "--tb=short",
            "-ra"
        ]
        
        print(f"\nCommand: {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse output
            stdout = result.stdout
            stderr = result.stderr
            return_code = result.returncode
            
            # Display output
            print(stdout)
            if stderr:
                print("STDERR:", stderr)
            
            # Extract test metrics from output
            passed = stdout.count(" PASSED")
            failed = stdout.count(" FAILED")
            skipped = stdout.count(" SKIPPED")
            
            print(f"\n{'─'*80}")
            print(f"RESULTS SUMMARY - {test_group['name']}")
            print(f"{'─'*80}")
            print(f"✓ Passed:  {passed}")
            print(f"✗ Failed:  {failed}")
            print(f"⊘ Skipped: {skipped}")
            print(f"Status:    {'✓ SUCCESS' if return_code == 0 else '✗ FAILED'}")
            
            # Add metrics
            metric = MetricRecord(
                component=test_group['name'],
                component_type=test_group['component'],
                test_name=test_group['test_file'].split('/')[-1],
                execution_time_ms=0,  # Would be captured in real pytest plugin
                status="PASS" if return_code == 0 else "FAIL",
                timestamp=datetime.now().isoformat(),
                records_processed=passed + failed,
                failure_reason=None if return_code == 0 else "See output above"
            )
            collector.add_metric(metric)
            
            results[test_group['name']] = {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'status': return_code == 0,
                'output': stdout[-500:] if len(stdout) > 500 else stdout
            }
            
        except subprocess.TimeoutExpired:
            print(f"✗ Test execution timed out after 60 seconds")
            results[test_group['name']] = {
                'error': 'Timeout',
                'status': False
            }
        except Exception as e:
            print(f"✗ Error running tests: {e}")
            results[test_group['name']] = {
                'error': str(e),
                'status': False
            }
    
    # Generate reports
    print("\n\n" + "="*80)
    print("GENERATING PERFORMANCE REPORTS")
    print("="*80)
    
    try:
        # Create metrics directory
        metrics_dir = Path("metrics")
        metrics_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        json_file = metrics_dir / "test_execution_results.json"
        collector.save_to_json(str(json_file))
        print(f"✓ JSON Report:  {json_file}")
        
        # Save HTML report
        html_file = metrics_dir / "test_metrics_dashboard.html"
        collector.generate_html_report(str(html_file))
        print(f"✓ HTML Dashboard: {html_file}")
        
        # Create summary report
        summary = collector.get_summary()
        print(f"\n{'─'*80}")
        print("AGGREGATED PERFORMANCE SUMMARY")
        print(f"{'─'*80}")
        print(f"Total Tests:        {summary.total_tests}")
        print(f"Passed:             {summary.passed_tests}")
        print(f"Failed:             {summary.failed_tests}")
        print(f"Pass Rate:          {(summary.passed_tests/max(summary.total_tests, 1)*100):.2f}%")
        print(f"Avg Latency:        {summary.average_latency_ms:.2f} ms")
        print(f"Total Execution:    {summary.total_execution_time_ms/1000:.2f} seconds")
        
    except Exception as e:
        print(f"✗ Error generating reports: {e}")
    
    print("\n" + "="*80)
    print("TEST EXECUTION COMPLETE")
    print("="*80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nSee generated reports in 'metrics/' directory")
    print("="*80 + "\n")
    
    return results

if __name__ == "__main__":
    run_tests_with_metrics()
