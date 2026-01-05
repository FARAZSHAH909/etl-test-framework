# ETL Framework Architecture & Test Mapping Diagrams

## 1. Framework Interaction Diagram

This diagram shows how test layers interact within the ETL test framework:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ETL TEST AUTOMATION FRAMEWORK                     │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Layer 1: DATA INGESTION VALIDATION                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ S3 VALIDATORS                                               │   │
│  │ • File existence check                                      │   │
│  │ • Schema validation (CSV headers)                           │   │
│  │ • Data type validation                                      │   │
│  │ • Null/completeness checks                                  │   │
│  │                                                             │   │
│  │ Test Output: ✓ PASS / ✗ FAIL                               │   │
│  │ Metrics: Latency (ms), Records Validated                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ▼                                          │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Layer 2: ORCHESTRATION & EXECUTION                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ LAMBDA ORCHESTRATION TESTS                                  │   │
│  │ • Validate orchestration logic                              │   │
│  │ • Test trigger mechanisms                                   │   │
│  │ • Validate payload handling                                 │   │
│  │ • Error path testing                                        │   │
│  │                                                             │   │
│  │ Test Output: ✓ PASS / ✗ FAIL                               │   │
│  │ Metrics: Execution Time (ms), Invocations                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ▼                                          │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Layer 3: DATA TRANSFORMATION                                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ GLUE ETL VALIDATION                                         │   │
│  │ • Validate transformation logic                             │   │
│  │ • Test data mapping (member_id, status, etc.)               │   │
│  │ • Reconcile record counts (input vs output)                 │   │
│  │ • Test partition logic                                      │   │
│  │                                                             │   │
│  │ Test Output: ✓ PASS / ✗ FAIL + Reconciliation Metrics      │   │
│  │ Metrics: Throughput (r/s), Processing Time, Match Rate      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ▼                                          │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  Layer 4: DATA QUALITY & PERSISTENCE                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ DOCUMENTDB CHECKS                                           │   │
│  │ • Validate document structure                               │   │
│  │ • Check field presence (required: member_id, status, etc.)  │   │
│  │ • Validate data type constraints                            │   │
│  │ • Test indexing & query performance                         │   │
│  │                                                             │   │
│  │ Test Output: ✓ PASS / ✗ FAIL                               │   │
│  │ Metrics: Query Latency (ms), Document Count                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                           ▼                                          │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  FRAMEWORK OUTPUT                                                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ✓ Pass/Fail Status for all layers                                   │
│  ✓ Performance Metrics (latency, throughput)                         │
│  ✓ Data Reconciliation Results                                       │
│  ✓ Failure Analysis & Root Causes                                    │
│  ✓ Before/After Quality Improvement Statistics                       │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture-to-Test Mapping Diagram

This consolidated diagram visually links each AWS pipeline component to its corresponding test/validation logic:

```
AWS PIPELINE ARCHITECTURE          ◄─────────►     TEST FRAMEWORK MAPPING
═══════════════════════════════════════════════════════════════════════════


┌─────────────────────────────┐
│  DATA SOURCE                │
│  (Member Records CSV)       │
└────────────┬────────────────┘
             │ Upload
             ▼
┌──────────────────────────────────────┐              ┌─────────────────────┐
│ AWS S3 (Data Lake)                   │◄─────────────│ S3 VALIDATORS       │
│  • Bucket: member-data-staging       │              │                     │
│  • Path: /member-etl/YYYY-MM/data    │   Tests:    │ ✓ File Exists       │
│  • Format: CSV (UTF-8)               │              │ ✓ Schema Valid      │
└──────────────────────────────────────┘              │ ✓ Data Complete     │
             │                                         │ ✓ Type Validation   │
             │ Trigger on new file                    └─────────────────────┘
             ▼
┌──────────────────────────────────────┐              ┌─────────────────────┐
│ AWS LAMBDA (Orchestrator)            │◄─────────────│ LAMBDA TESTS        │
│  • Function: member-etl-orchestrator │              │                     │
│  • Runtime: Python 3.11              │   Tests:    │ ✓ Function Invoke   │
│  • Timeout: 300s                     │              │ ✓ Event Processing  │
│  • Payload: S3 event + metadata      │              │ ✓ Error Handling    │
└──────────────────────────────────────┘              │ ✓ Glue Job Trigger  │
             │                                         └─────────────────────┘
             │ Invoke Glue Job
             ▼
┌──────────────────────────────────────┐              ┌─────────────────────┐
│ AWS GLUE (ETL Engine)                │◄─────────────│ GLUE TESTS          │
│  • Job: member-data-etl              │              │                     │
│  • Workers: 2 G.2X nodes             │   Tests:    │ ✓ Transformation    │
│  • Max Capacity: 10 DPU              │              │ ✓ Record Mapping    │
│  • Input: S3 CSV                     │              │ ✓ Reconciliation    │
│  • Output: DocumentDB collection     │              │ ✓ Partitioning      │
└──────────────────────────────────────┘              │ ✓ Throughput        │
             │                                         └─────────────────────┘
             │ Write transformed data
             ▼
┌──────────────────────────────────────┐              ┌─────────────────────┐
│ AWS DocumentDB (NoSQL DB)            │◄─────────────│ DOCUMENTDB TESTS     │
│  • Cluster: member-analytics         │              │                     │
│  • Instance: db.r5.large (2)         │   Tests:    │ ✓ Document Schema   │
│  • Collection: member_records        │              │ ✓ Required Fields   │
│  • Index: member_id (unique)         │              │ ✓ Data Types        │
│  • Records: ~500K per run            │              │ ✓ Query Performance │
└──────────────────────────────────────┘              │ ✓ Indexing          │
                                                       └─────────────────────┘


COVERAGE MATRIX
═══════════════════════════════════════════════════════════════════════════

Component       │ S3 Validators │ Lambda Tests │ Glue Tests │ DocumentDB Tests
────────────────┼───────────────┼──────────────┼────────────┼─────────────────
Data Input      │       ✓       │      ✓       │     ✓      │        ✓
Processing      │       ✓       │      ✓       │     ✓      │        ✓
Validation      │       ✓       │      ✓       │     ✓      │        ✓
Performance     │       ✓       │      ✓       │     ✓      │        ✓
Error Handling  │       ✓       │      ✓       │     ✓      │        ✓
────────────────┼───────────────┼──────────────┼────────────┼─────────────────
100% COVERAGE   │ Ingestion     │ Orchestration│ Transform  │ Persistence
```

---

## 3. Data Flow with Quality Gates

```
INGESTION PIPELINE WITH QUALITY GATES
═════════════════════════════════════════════════════════════════════════

Step 1: Data Arrival at S3
┌─────────────────────────┐
│ New CSV file uploaded   │
│ to S3 bucket            │
└──────────┬──────────────┘
           │
           ▼
    ┌─────────────┐
    │ QUALITY     │
    │ GATE 1      │  S3 Schema Validation
    │ ✓ Headers   │  (S3 Validators)
    │ ✓ Encoding  │  
    │ ✓ Size      │
    └─────────────┘
           │
      PASS │ FAIL → Alert & Stop
           │
           ▼
Step 2: Orchestration Trigger
┌─────────────────────────┐
│ Lambda invokes Glue job │
└──────────┬──────────────┘
           │
           ▼
    ┌─────────────┐
    │ QUALITY     │
    │ GATE 2      │  Lambda Orchestration Test
    │ ✓ Payload   │  (Lambda Tests)
    │ ✓ Trigger   │
    │ ✓ Logging   │
    └─────────────┘
           │
      PASS │ FAIL → Alert & Stop
           │
           ▼
Step 3: Data Transformation
┌─────────────────────────┐
│ Glue job transforms     │
│ data to target schema   │
└──────────┬──────────────┘
           │
           ▼
    ┌─────────────┐
    │ QUALITY     │
    │ GATE 3      │  Glue ETL & Reconciliation
    │ ✓ Counts    │  (Glue Tests)
    │ ✓ Schema    │
    │ ✓ Rules     │
    └─────────────┘
           │
      PASS │ FAIL → Alert & Stop
           │
           ▼
Step 4: Data Persistence
┌─────────────────────────┐
│ Write to DocumentDB     │
│ collection              │
└──────────┬──────────────┘
           │
           ▼
    ┌─────────────┐
    │ QUALITY     │
    │ GATE 4      │  DocumentDB Validation
    │ ✓ Fields    │  (DocumentDB Tests)
    │ ✓ Types     │
    │ ✓ Indexing  │
    └─────────────┘
           │
      PASS │ FAIL → Alert & Remediate
           │
           ▼
    ┌─────────────┐
    │ SUCCESS     │
    │ Pipeline    │
    │ Complete    │
    └─────────────┘
```

---

## 4. Test Execution Flow & Metrics Collection

```
TEST EXECUTION WITH PERFORMANCE METRICS
═════════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│  Test Framework Initialization                               │
│  └─ PerformanceMetricsCollector() started                    │
└────────────────────┬─────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────────┐          ┌──────────────────┐
    │ Unit Tests  │          │ Integration Tests│
    │ (mocked)    │          │ (AWS staging)    │
    └──────┬──────┘          └────────┬─────────┘
           │                          │
           │◄─ Metrics Tracking ─────►│
           │   • Execution time      │
           │   • Pass/fail status    │
           │   • Records processed   │
           │   • Throughput (r/s)    │
           │
           ▼
    ┌──────────────────────────────────────┐
    │ METRICS OUTPUT FOR EACH TEST         │
    │                                      │
    │ {                                    │
    │   "component": "test_s3_validator",  │
    │   "status": "PASS",                  │
    │   "execution_time_ms": 245.67,       │
    │   "records_processed": 5000,         │
    │   "throughput_rps": 20358.65,        │
    │   "timestamp": "2025-01-05T14:30:00" │
    │ }                                    │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────────┐
    │ AGGREGATED PERFORMANCE SUMMARY       │
    │                                      │
    │ • Total Tests: 24                    │
    │ • Passed: 23  Failed: 1  Skipped: 0 │
    │ • Avg Latency: 312.45 ms            │
    │ • Total Time: 7.5 seconds           │
    │ • Failure Rate: 4.17%                │
    │ • Throughput: 18,456 records/sec    │
    │ • Before Framework Failures: 45%    │
    │ • After Framework Failures: 4.17%   │
    └────────────┬───────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
    JSON Report      HTML Report
    metrics.json     metrics.html
```

---

## Key Metrics Definitions

| Metric | Definition | Unit | Use Case |
|--------|-----------|------|----------|
| **Execution Latency** | Time from test start to completion | ms | Shows efficiency of individual tests |
| **Throughput** | Records processed per second | r/s | Measures data processing speed |
| **Failure Rate** | Percentage of failed tests | % | Tracks framework effectiveness (lower is better) |
| **Total Records Processed** | Cumulative data validated | count | Demonstrates scale of validation |
| **Before/After Comparison** | Failure rate improvement | % | Proves business value (e.g., 45% → 4.17% = 90.7% improvement) |
| **Component Latency** | Avg execution time per AWS component | ms | Identifies bottlenecks |

---

## Client Value Proposition

✓ **Traceability**: Each AWS component has explicit test coverage  
✓ **Performance Evidence**: Quantitative metrics show framework effectiveness  
✓ **Compliance Ready**: Clear audit trail of validations  
✓ **Cost Transparency**: Data on throughput and resource utilization  
✓ **Quality Improvement**: Measurable before/after failure rate reduction  
