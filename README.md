# etl-test-framework
# Healthcare ETL Test Framework (AWS Glue + PySpark)

Quality-first testing for cloud-native member data pipelines (S3 → Lambda → Glue → DocumentDB).

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/