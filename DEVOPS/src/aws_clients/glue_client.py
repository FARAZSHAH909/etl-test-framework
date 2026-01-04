import boto3
from typing import Optional, Dict, List
from botocore.exceptions import ClientError


class GlueClient:
    """AWS Glue client for job monitoring and execution."""

    def __init__(self, region_name: str = 'us-east-1'):
        self.glue_client = boto3.client('glue', region_name=region_name)

    def get_job_run(self, job_name: str, run_id: str) -> Dict:
        """Get details of a Glue job run."""
        try:
            response = self.glue_client.get_job_run(JobName=job_name, RunId=run_id)
            return response['JobRun']
        except ClientError as e:
            print(f"Error getting job run: {e}")
            return {}

    def get_job_runs(self, job_name: str) -> List[Dict]:
        """Get list of job runs for a job."""
        try:
            response = self.glue_client.get_job_runs(JobName=job_name)
            return response.get('JobRuns', [])
        except ClientError as e:
            print(f"Error getting job runs: {e}")
            return []

    def start_job_run(self, job_name: str, arguments: Optional[Dict] = None) -> Optional[str]:
        """Start a Glue job run."""
        try:
            kwargs = {'JobName': job_name}
            if arguments:
                kwargs['Arguments'] = arguments
            response = self.glue_client.start_job_run(**kwargs)
            return response.get('JobRunId')
        except ClientError as e:
            print(f"Error starting job run: {e}")
            return None

    def get_job(self, job_name: str) -> Dict:
        """Get job details."""
        try:
            response = self.glue_client.get_job(Name=job_name)
            return response.get('Job', {})
        except ClientError as e:
            print(f"Error getting job: {e}")
            return {}

    def list_jobs(self) -> List[str]:
        """List all Glue jobs."""
        try:
            response = self.glue_client.list_jobs()
            return response.get('JobNames', [])
        except ClientError as e:
            print(f"Error listing jobs: {e}")
            return []


class GlueJobValidator:
    """Validate Glue job execution and results."""

    def __init__(self, glue_client: Optional[GlueClient] = None):
        self.glue_client = glue_client or GlueClient()
        self.errors = []

    def validate_job_exists(self, job_name: str) -> bool:
        """Check if Glue job exists."""
        job = self.glue_client.get_job(job_name)
        if not job:
            self.errors.append(f"Glue job '{job_name}' does not exist")
            return False
        return True

    def validate_job_run_succeeded(self, job_name: str, run_id: str) -> bool:
        """Check if job run succeeded."""
        job_run = self.glue_client.get_job_run(job_name, run_id)
        if not job_run:
            self.errors.append(f"Job run {run_id} not found")
            return False
        
        state = job_run.get('JobRunState')
        if state != 'SUCCEEDED':
            self.errors.append(f"Job run {run_id} state is {state}, expected SUCCEEDED")
            return False
        return True

    def validate_job_run_output_records(self, job_name: str, run_id: str, expected_count: int = None) -> bool:
        """Validate job run output record count."""
        job_run = self.glue_client.get_job_run(job_name, run_id)
        if not job_run:
            self.errors.append(f"Job run {run_id} not found")
            return False
        
        # Note: Glue job runs don't directly return output record counts; 
        # this would typically be tracked in your job script or output files
        output_records = job_run.get('ExecutionTime', 0)  # placeholder
        if expected_count and output_records < expected_count:
            self.errors.append(f"Output records {output_records} less than expected {expected_count}")
            return False
        return True

    def validate_no_failed_tasks(self, job_name: str, run_id: str) -> bool:
        """Check that job run has no failed tasks."""
        job_run = self.glue_client.get_job_run(job_name, run_id)
        if not job_run:
            self.errors.append(f"Job run {run_id} not found")
            return False
        
        state = job_run.get('JobRunState')
        if state == 'FAILED':
            error = job_run.get('ErrorMessage', 'Unknown error')
            self.errors.append(f"Job run failed: {error}")
            return False
        return True

    def get_errors(self) -> List[str]:
        """Return list of validation errors."""
        return self.errors

    def clear_errors(self):
        """Clear error list."""
        self.errors = []
