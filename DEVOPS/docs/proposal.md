Proposal: A Quality-First ETL Test Framework for Cloud-Native Data Pipelines

Executive Summary
-----------------
This proposal converts the white paper into a working ETL Test Automation Framework for Medicaid/Medicare member data on AWS. The framework delivered in the repository includes:

- S3 ingestion and schema validations
- Great-Expectations-style validators
- AWS clients for S3, Glue, Lambda, DocumentDB
- Unit and integration tests (moto mocks), and CI templates

Scope of Work
-------------
1. Finalize production integration and CI (OIDC) role creation.
2. Run and validate end-to-end tests against staging AWS resources (S3 → Lambda → Glue → DocumentDB).
3. Harden IAM policies and rotate credentials after validation.
4. Optional: deploy Glue jobs / Lambda functions and DocumentDB cluster provisioning (not included by default).

Deliverables
------------
- Fully tested ETL Test Automation Framework in GitHub (code + tests)
- CI workflow for mocked tests and OIDC-based CI for real runs
- IAM trust & policy templates for safe CI integration
- Proposal & cost estimate PDF (this document)

Timeline
--------
- Week 0: Security cleanup and key rotation (customer action, same day)
- Week 1: Create IAM role and attach least-privilege policy; configure CI OIDC (1-2 days)
- Week 2: Run real AWS integration tests, collect results, remediate (2-3 days)
- Week 3: Finalize deliverables, documentation, and handoff (1-2 days)

Assumptions
-----------
- Customer will rotate/revoke any leaked keys before real-AWS tests.
- Customer will provide or approve S3 bucket names and resource names.
- Glue jobs / Lambdas to be validated are available in the target account or created by the customer.

Cost Estimate (example / staging-level estimate)
------------------------------------------------
Estimates assume minimal staging usage for validation runs (not production load).

1) S3 (storage + requests)
- Storage: 10 GB month (staging) ≈ $0.23
- PUT/GET requests (validation) ≈ $0.10

2) AWS Glue
- Glue Developer Endpoint / job runtime: Glue billed per DPU-hour.
- Example: 2 DPU for 30 minutes per run ⇒ 1 DPU-hour per run. Glue price ~ $0.44 / DPU-Hour (varies by region).
- For 10 validation runs: ~10 * $0.44 = $4.40

3) AWS Lambda
- Small invocations for tests: free tier applies. Cost negligible for validation (<< $1)

4) DocumentDB (staging)
- t3.medium equivalent instances (example) ≈ $0.10–0.20/hour (varies), add storage & I/O.
- For short validation runs (few hours): estimate $1–$10 per test cycle.

5) Total staging test cycle estimate (per validation pass):
- S3 + Glue + Lambda + DocumentDB ≈ $6–$20 (heavily dependent on Glue and DocumentDB instance choices).

6) One-time engineering (implementation + support)
- Engineer (2 weeks) to finalize IAM, CI, run tests, fix issues — estimate 80 hours @ $120/hr = $9,600
- Reduced scope or internal delivery may lower cost.

Recommendations
---------------
- Use GitHub OIDC to avoid storing long-lived credentials in CI.
- Run initial validation in a staging account with limited data and smaller instance sizes for DocumentDB and Glue.
- Enable CloudTrail and CloudWatch during validation to capture errors and logs.

Acceptance Criteria
-------------------
- All unit tests (mocked) pass in CI (already passing)
- End-to-end validation against staging S3 → Lambda → Glue → DocumentDB succeeds without data quality violations for provided test dataset
- IAM role exists with least-privilege policy and CI assumes it via OIDC

Next Steps (actionable)
-----------------------
1. Rotate/revoke any leaked keys (done by customer).  
2. Replace placeholders in `DEVOPS/aws/role-trust.json` and `DEVOPS/aws/test-policy.json`.  
3. Create IAM role and attach policy (CLI commands provided in repo README).  
4. Push a test PR to trigger OIDC workflow and collect results.  

Contact
-------
For follow-up and scheduling, reply in this thread and I will execute the CI run and produce final test reports.
