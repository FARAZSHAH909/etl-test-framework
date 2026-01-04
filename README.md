# etl-test-framework
# Healthcare ETL Test Framework (AWS Glue + PySpark)

Quality-first testing for cloud-native member data pipelines (S3 → Lambda → Glue → DocumentDB).

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
# ETL Test Framework

Healthcare ETL Test Framework (PySpark + Glue-inspired orchestration)

Quality-first testing for cloud-native member data pipelines (S3 → Lambda → Glue → DocumentDB).

This repo contains a minimal ETL test harness that demonstrates data cleaning, validation, reconciliation, and unit tests for member data (Medicaid/Medicare style).

## Getting Started (step-by-step)

1. Create and activate a virtual environment:

```powershell
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# or Command Prompt
.\venv\Scripts\activate.bat
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the unit tests locally:

```powershell
# from repository root
pytest DEVOPS/tests/unit/ -v
```

4. Run the demo pipeline interactively:

```python
from src.orchestrator.etl_pipeline import run_etl_pipeline
report, df = run_etl_pipeline()
print(report)
df.show()
```

## AWS Integration (safe guidance)

- CI and local tests in this repo are designed to run without real AWS credentials by mocking S3. This prevents accidental billing and keeps secrets out of the repo.
- If you want CI to run against AWS resources, use GitHub Secrets to store `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` and only grant minimal IAM permissions (S3 read/write for the bucket used, etc.).

### Recommended: Mocked S3 in CI (no real AWS creds)

We provide a sample GitHub Actions workflow that uses `moto` to mock S3 during the test run. Add the workflow file `.github/workflows/ci-mocked-s3.yml` (the repository may contain this file). This creates an in-process mocked S3 and runs the test suite.

### If you must use real AWS in CI (NOT recommended without careful permissions)

1. Store credentials in GitHub Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.
2. Use `aws-actions/configure-aws-credentials@v2` in your workflow and scope permissions to the specific bucket and actions required.

### Local AWS commands (you run these with your own credentials)

Configure AWS CLI:
```powershell
aws configure
# enter Access Key, Secret, region
```

Create S3 bucket (example):
```powershell
aws s3api create-bucket --bucket my-etl-bucket-test1 --region us-east-1 --create-bucket-configuration LocationConstraint=us-east-1
```

Upload a file:
```powershell
aws s3 cp DEVOPS/tests/test_data/sample.csv s3://my-etl-bucket-test1/
```

### Security Reminder
- Never commit credentials to source control. If you accidentally published keys, revoke them immediately from the AWS Console.

---

If you want, I can add the CI workflow and commit the README changes for you — tell me to proceed and I'll create the workflow `.github/workflows/ci-mocked-s3.yml`, run the test suite, and push the changes.