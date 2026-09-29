# NetOps Migration Quality Platform

Automated data migration, data quality, and validation framework built with Python, pytest, SQL, PostgreSQL, Docker, GitHub Actions, and AI-assisted validation agents.

## Project Overview

This project simulates an enterprise data migration and transformation validation scenario.

The platform demonstrates how a QA/Data Testing engineer can validate data across migration pipelines, including:

- Source-to-target reconciliation
- Transformation rule validation
- Missing record detection
- Duplicate detection
- Mandatory field validation
- Referential integrity
- Large-scale migration validation
- Incremental migration using watermarks
- Automated quality reporting
- CI/CD quality gates
- AI-assisted migration analysis

The project uses synthetic data and is designed to demonstrate practical Data QA and Data Migration Engineering capabilities.

## Architecture

```text
                    SOURCE SYSTEM
                         │
                         ▼
                   ETL / ELT PROCESS
                         │
                         ▼
                    TARGET SYSTEM
                         │
                         ▼
                QA VALIDATION ENGINE
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
 Transformation     Reconciliation    Data Quality
   Validation          Checks            Checks
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
              MIGRATION QUALITY REPORT
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
        Dashboard    AI Agents     CI/CD

## Validation Strategy

The framework validates the following migration quality dimensions:

Validation	Description
Transformation Rules	Validates source-to-target transformation logic
Record Count Reconciliation	Compares source and target record counts
Missing Records	Identifies records missing from the target
Duplicate Detection	Detects duplicated business keys
Mandatory Fields	Detects NULL values in required fields
Referential Integrity	Detects orphan records
Incremental Delta Reconciliation	Validates records processed during incremental loads

## Large-Scale Migration Validation

The project includes a synthetic 1 million record migration scenario.

The pipeline automatically:

Generates 1,000,000 synthetic customer records
Loads the source dataset into PostgreSQL
Transforms the records into the target structure
Executes automated validation queries
Generates a scale validation report
Uploads the report as a GitHub Actions artifact

Current validation results:

Source Records:              1,000,000
Target Records:              1,000,000
Transformation Errors:       0
Duplicate Records:           0
Mandatory Field Errors:      0
Referential Integrity Errors: 0
Overall Status:              PASS

## Incremental Migration Validation

The platform also simulates an incremental migration process using a migration watermark.

The scenario validates:

Previously processed records
New delta records
Incremental record reconciliation
Transformation rules
Duplicate detection
Record counts
Referential integrity

Example validation:

Expected Delta:       3
Inserted Records:     3
Source / Target:      8 / 8
Overall Status:       PASS

The incremental validation generates:

reports/incremental_validation_report.json

The report is automatically uploaded as a GitHub Actions artifact.

## Defect Injection Testing

The framework has been intentionally tested by introducing migration and data quality defects.

Examples include:

Incorrect transformation values
Missing target records
Duplicate records
NULL mandatory fields
Referential integrity violations

The automated validation framework successfully detected the injected defects and returned a FAIL result.

After correcting the defects, the validation suite returned:

6 passed
0 failed
Overall Status: PASS

This demonstrates that the validation framework is capable of detecting real migration-quality problems rather than only validating successful scenarios.

## AI-Assisted Validation

The project includes three AI-oriented validation agents:

Migration Validation Agent

Analyzes migration validation results and provides structured migration-quality findings.

Data Quality Investigation Agent

Analyzes detected data-quality issues and organizes investigation findings.

Migration Readiness Agent

Evaluates migration validation evidence and produces a structured readiness assessment.

The AI agents are intentionally designed as an analysis and investigation layer.

Deterministic SQL and Python validations remain the source of truth for PASS/FAIL decisions.

Deterministic Validation
        │
        ▼
   PASS / FAIL
        │
        ▼
     AI Agents
        │
        ▼
 Analysis / Investigation / Readiness

This prevents an AI-generated interpretation from overriding a deterministic data-quality failure.

## Quality Dashboard

A Streamlit dashboard provides a visual representation of migration quality results.

The dashboard currently displays:

Migration validation results
1M record scale validation
Incremental migration validation
Source/target reconciliation
Transformation validation
Duplicate detection
Mandatory field validation
Referential integrity
Overall migration status

Run the dashboard locally with:

streamlit run dashboard/app.py

## CI/CD Pipeline

GitHub Actions automatically executes the migration validation pipeline.

The pipeline includes:

PostgreSQL service initialization
Database schema initialization
Automated migration validations
1M synthetic record generation
1M record migration
Large-scale validation
Incremental migration validation
Migration validation AI agent
Data quality investigation agent
Migration readiness agent
Consolidated agent assessment
JSON report generation
Artifact upload

## CI/CD Evidence

The pipeline has been intentionally tested with migration defects.

Example workflow:

🟢 Validation passes
        │
        ▼
🔴 Intentional migration defect
        │
        ▼
🔴 Automated validation detects defect
        │
        ▼
🟢 Defect corrected
        │
        ▼
🟢 Pipeline passes

This demonstrates automated testing, defect detection, migration quality gates, reporting, and CI/CD integration.

## Technology Stack

## Testing & Automation

Python 3.13
pytest
psycopg
SQL
Automated validation scripts

## Database

PostgreSQL 16
Source and target schemas
Relational data validation
Reconciliation queries

## Infrastructure

Docker
Docker Compose

## CI/CD

Git
GitHub
GitHub Actions

## Dashboard

Streamlit
Pandas

## AI

Migration Validation Agent
Data Quality Investigation Agent
Migration Readiness Agent

## Project Structure

netops-migration-qa/
│
├── agents/
│   ├── migration_validation_agent.py
│   ├── data_quality_investigation_agent.py
│   ├── migration_readiness_agent.py
│   └── agent_assessment_report.py
│
├── dashboard/
│   └── app.py
│
├── data/
│
├── docker/
│
├── reports/
│
├── sql/
│   ├── init_database.sql
│   └── incremental_migration.sql
│
├── src/
│   ├── run_validation.py
│   ├── generate_test_data.py
│   ├── validate_scale.py
│   └── validate_incremental.py
│
├── tests/
│   └── test_customer_migration.py
│
├── .github/
│   └── workflows/
│       └── data-validation.yml
│
├── docker-compose.yml
├── README.md
└── .gitignore

## How to Run Locally

1. Start PostgreSQL
docker compose up -d

2. Activate the Python environment
source .venv/bin/activate

3. Run the automated tests
pytest -v

4. Generate the migration quality report
python src/run_validation.py

5. Run the 1M record validation
python src/generate_test_data.py
python src/validate_scale.py

6. Run incremental migration validation
python src/validate_incremental.py

7. Launch the dashboard
streamlit run dashboard/app.py

## Example Test Results

Current local validation suite:

6 passed
0 failed

Large-scale validation:

1,000,000 source records
1,000,000 target records
0 transformation errors
0 duplicates
0 mandatory-field errors
0 orphan records
PASS

Incremental validation:

Expected delta: 3
Inserted records: 3
Source / Target: 8 / 8
PASS

## Skills Demonstrated

This project demonstrates practical experience in:

Data Migration Testing
ETL / ELT Validation
Data Quality Engineering
SQL Testing
Database Testing
Python Test Automation
Reconciliation Testing
Large-Scale Data Validation
Incremental Migration Testing
Data Transformation Validation
Defect Injection Testing
CI/CD Quality Gates
Automated Reporting
Dashboard Development
AI-Assisted Data Quality Investigation
Migration Readiness Assessment

## Future Roadmap

Potential future extensions include:

Azure Blob Storage integration
Azure Data Factory pipeline
Azure PostgreSQL deployment
Batch migration scenarios
Real-time migration simulation
Additional data-quality rules
Production-style configuration management
Environment-based database configuration
Expanded AI-agent workflows
Cloud-based dashboard deployment
