"""
Performance Metrics Module
Captures execution latency, throughput, and failure rates for ETL framework validation.
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path


class TestComponentType(Enum):
    """Enum for ETL pipeline component types."""
    S3_VALIDATOR = "S3 Validator"
    LAMBDA_ORCHESTRATION = "Lambda Orchestration"
    GLUE_ETL = "Glue ETL"
    DOCUMENTDB_CHECK = "DocumentDB Check"


@dataclass
class MetricRecord:
    """Single metric record for a test/validation run."""
    component: str
    component_type: TestComponentType
    test_name: str
    execution_time_ms: float
    status: str  # "PASS", "FAIL", "SKIP"
    timestamp: str
    records_processed: int = 0
    failure_reason: Optional[str] = None
    throughput_records_per_sec: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['component_type'] = self.component_type.value
        return data


@dataclass
class PerformanceSummary:
    """Aggregated performance summary."""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    total_execution_time_ms: float = 0.0
    average_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    total_records_processed: int = 0
    average_throughput_rps: float = 0.0
    failure_rate_percent: float = 0.0
    component_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    

class PerformanceMetricsCollector:
    """
    Collects and aggregates performance metrics for ETL test framework.
    
    Usage:
        collector = PerformanceMetricsCollector()
        
        with collector.track_execution("s3_validator_test", TestComponentType.S3_VALIDATOR):
            # Your test code here
            pass
        
        metrics = collector.get_summary()
        collector.save_to_json("metrics_report.json")
    """
    
    def __init__(self):
        self.metrics: List[MetricRecord] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def add_metric(self, metric: MetricRecord) -> None:
        """Add a metric record."""
        self.metrics.append(metric)
    
    def track_execution(self, test_name: str, component_type: TestComponentType):
        """Context manager for tracking test execution time."""
        return _ExecutionTracker(self, test_name, component_type)
    
    def get_summary(self) -> PerformanceSummary:
        """Generate aggregated performance summary."""
        if not self.metrics:
            return PerformanceSummary()
        
        summary = PerformanceSummary()
        summary.total_tests = len(self.metrics)
        
        # Count by status
        for metric in self.metrics:
            if metric.status == "PASS":
                summary.passed_tests += 1
            elif metric.status == "FAIL":
                summary.failed_tests += 1
            elif metric.status == "SKIP":
                summary.skipped_tests += 1
            
            summary.total_execution_time_ms += metric.execution_time_ms
            summary.min_latency_ms = min(summary.min_latency_ms, metric.execution_time_ms)
            summary.max_latency_ms = max(summary.max_latency_ms, metric.execution_time_ms)
            summary.total_records_processed += metric.records_processed
        
        # Calculate averages
        executable_tests = summary.passed_tests + summary.failed_tests
        if executable_tests > 0:
            summary.average_latency_ms = summary.total_execution_time_ms / executable_tests
            summary.failure_rate_percent = (summary.failed_tests / executable_tests) * 100
        
        if summary.total_execution_time_ms > 0 and summary.total_records_processed > 0:
            total_seconds = summary.total_execution_time_ms / 1000
            summary.average_throughput_rps = summary.total_records_processed / total_seconds
        
        # Component-level summaries
        components = {}
        for metric in self.metrics:
            comp_key = metric.component_type.value
            if comp_key not in components:
                components[comp_key] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "avg_latency_ms": 0.0,
                    "total_latency_ms": 0.0
                }
            
            comp = components[comp_key]
            comp["total"] += 1
            if metric.status == "PASS":
                comp["passed"] += 1
            elif metric.status == "FAIL":
                comp["failed"] += 1
            comp["total_latency_ms"] += metric.execution_time_ms
        
        # Calculate averages for components
        for comp_key, comp in components.items():
            if comp["total"] > 0:
                comp["avg_latency_ms"] = comp["total_latency_ms"] / comp["total"]
        
        summary.component_summaries = components
        return summary
    
    def save_to_json(self, file_path: str) -> None:
        """Save metrics to JSON file."""
        summary = self.get_summary()
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": summary.total_tests,
                "passed": summary.passed_tests,
                "failed": summary.failed_tests,
                "skipped": summary.skipped_tests,
                "total_execution_time_ms": summary.total_execution_time_ms,
                "average_latency_ms": round(summary.average_latency_ms, 2),
                "min_latency_ms": summary.min_latency_ms if summary.min_latency_ms != float('inf') else 0,
                "max_latency_ms": summary.max_latency_ms,
                "failure_rate_percent": round(summary.failure_rate_percent, 2),
                "total_records_processed": summary.total_records_processed,
                "average_throughput_rps": round(summary.average_throughput_rps, 2),
            },
            "component_summaries": summary.component_summaries,
            "detailed_metrics": [m.to_dict() for m in self.metrics]
        }
        
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)
    
    def generate_html_report(self, file_path: str) -> None:
        """Generate HTML report with metrics visualization."""
        summary = self.get_summary()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>ETL Framework Performance Metrics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px; }}
        .metric-card {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ font-size: 12px; color: #7f8c8d; margin-top: 5px; }}
        .pass {{ color: #27ae60; }}
        .fail {{ color: #e74c3c; }}
        .skip {{ color: #f39c12; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }}
        th {{ background-color: #34495e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #f9f9f9; }}
        .component-summary {{ margin-top: 30px; }}
        .component-card {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ETL Framework Performance Metrics Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="metric-card">
            <div class="metric-value">{summary.total_tests}</div>
            <div class="metric-label">Total Tests</div>
        </div>
        <div class="metric-card">
            <div class="metric-value pass">{summary.passed_tests}</div>
            <div class="metric-label">Passed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value fail">{summary.failed_tests}</div>
            <div class="metric-label">Failed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{round(summary.average_latency_ms, 2)} ms</div>
            <div class="metric-label">Avg Latency</div>
        </div>
    </div>
    
    <div class="summary">
        <div class="metric-card">
            <div class="metric-value">{round(summary.failure_rate_percent, 2)}%</div>
            <div class="metric-label">Failure Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{summary.total_records_processed}</div>
            <div class="metric-label">Records Processed</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{round(summary.average_throughput_rps, 2)}</div>
            <div class="metric-label">Throughput (r/s)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{round(summary.total_execution_time_ms / 1000, 2)} s</div>
            <div class="metric-label">Total Time</div>
        </div>
    </div>
    
    <div class="component-summary">
        <h2>Component-Level Performance</h2>
        {self._generate_component_html(summary)}
    </div>
    
    <div>
        <h2>Detailed Test Results</h2>
        <table>
            <tr>
                <th>Component</th>
                <th>Test Name</th>
                <th>Status</th>
                <th>Latency (ms)</th>
                <th>Records</th>
                <th>Throughput (r/s)</th>
            </tr>
            {self._generate_rows_html(summary)}
        </table>
    </div>
</body>
</html>
        """
        
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(html_content)
    
    def _generate_component_html(self, summary: PerformanceSummary) -> str:
        """Generate HTML for component summaries."""
        html = ""
        for comp_name, comp_data in summary.component_summaries.items():
            html += f"""
        <div class="component-card">
            <h3>{comp_name}</h3>
            <p><strong>Total:</strong> {comp_data['total']} | 
               <span class="pass"><strong>Passed:</strong> {comp_data['passed']}</span> | 
               <span class="fail"><strong>Failed:</strong> {comp_data['failed']}</span> | 
               <strong>Avg Latency:</strong> {round(comp_data['avg_latency_ms'], 2)} ms</p>
        </div>
            """
        return html
    
    def _generate_rows_html(self, summary: PerformanceSummary) -> str:
        """Generate HTML table rows for detailed metrics."""
        html = ""
        for metric in self.metrics:
            status_class = "pass" if metric.status == "PASS" else ("fail" if metric.status == "FAIL" else "skip")
            html += f"""
            <tr>
                <td>{metric.component_type.value}</td>
                <td>{metric.test_name}</td>
                <td class="{status_class}"><strong>{metric.status}</strong></td>
                <td>{round(metric.execution_time_ms, 2)}</td>
                <td>{metric.records_processed}</td>
                <td>{round(metric.throughput_records_per_sec, 2)}</td>
            </tr>
            """
        return html


class _ExecutionTracker:
    """Context manager for tracking execution time."""
    
    def __init__(self, collector: PerformanceMetricsCollector, test_name: str, 
                 component_type: TestComponentType):
        self.collector = collector
        self.test_name = test_name
        self.component_type = component_type
        self.start_time = None
        self.records = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = (time.time() - self.start_time) * 1000
        status = "FAIL" if exc_type else "PASS"
        failure_reason = str(exc_val) if exc_val else None
        
        throughput = 0.0
        if self.records > 0 and elapsed_ms > 0:
            throughput = self.records / (elapsed_ms / 1000)
        
        metric = MetricRecord(
            component=self.test_name,
            component_type=self.component_type,
            test_name=self.test_name,
            execution_time_ms=elapsed_ms,
            status=status,
            timestamp=datetime.now().isoformat(),
            records_processed=self.records,
            failure_reason=failure_reason,
            throughput_records_per_sec=throughput
        )
        
        self.collector.add_metric(metric)
        return False  # Don't suppress exceptions
    
    def add_records(self, count: int) -> None:
        """Record number of items processed."""
        self.records += count
