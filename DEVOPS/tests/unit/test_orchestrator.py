from src.orchestrator.etl_pipeline import run_etl_pipeline

def test_etl_pipeline_full(spark):
    report, cleaned_df = run_etl_pipeline(spark=spark)

    assert report["status"] == "PASS"
    assert report["reconciliation"]["rows_dropped"] == 5   # based on sample data
    assert report["reconciliation"]["drop_percentage"] == 71.43
    assert cleaned_df.count() == 2