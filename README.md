# NetOps Migration Quality Platform

**Automated Data Migration QA | ETL/ELT Validation | Data Quality | Python | SQL | PostgreSQL | Docker | CI/CD**

NetOps Migration Quality Platform is a portfolio project that simulates an enterprise data migration environment. It demonstrates how automated testing, SQL-based reconciliation, Python validation scripts, and quality reports can help identify data inconsistencies between source and target systems.

The project uses synthetic customer data and combines deterministic validation rules with automated test execution and AI-assisted investigation workflows.

## Project Overview

The platform demonstrates the following data migration and quality assurance capabilities:

- Source-to-target record-count reconciliation
- Data transformation validation
- Missing-record and duplicate detection
- Mandatory-field validation
- Referential-integrity checks
- Large-scale migration validation using synthetic data
- Incremental migration with timestamp watermarks
- Automated JSON quality reports
- pytest-based testing
- CI/CD integration with GitHub Actions
- AI-assisted migration analysis
- A Streamlit dashboard for quality results

## Architecture

```text
                   SOURCE SYSTEM
                         |
                         v
                   ETL / ELT FLOW
                         |
                         v
                   TARGET SYSTEM
                         |
                         v
                QA VALIDATION ENGINE
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
    Transformations  Reconciliation  Data Quality
      Validation       Checks          Checks
          |              |              |
          +--------------+--------------+
                         |
                         v
                MIGRATION QUALITY REPORT
                         |
              +----------+----------+
              |          |          |
              v          v          v
           Dashboard  AI Agents    CI/CD
```

## Validation Strategy

| Validation | Purpose |
|---|---|
| Record-count reconciliation | Compares source and target record counts. |
| Transformation rules | Checks whether mapped target values match expected transformations. |
| Missing records | Identifies source records that are absent from the target. |
| Duplicate detection | Detects repeated business keys in the target dataset. |
| Mandatory fields | Checks required columns for null values. |
| Referential integrity | Identifies target records without a matching source record. |
| Incremental reconciliation | Checks source and target consistency after incremental processing. |
| Watermark management | Tracks the latest processed source timestamp. |
| Automated reporting | Produces structured validation results in JSON format. |

## Large-Scale Migration Validation

The project includes a synthetic migration scenario designed to exercise validation over 1,000,000 customer records.

The workflow includes:

1. Generating synthetic customer data.
2. Loading the data into PostgreSQL.
3. Transforming source records into the target structure.
4. Running migration-quality checks.
5. Producing a validation report.
6. Uploading reports as GitHub Actions artifacts when the configured workflow runs successfully.

### Reported validation results

| Metric | Result |
|---|---:|
| Source records | 1,000,000 |
| Target records | 1,000,000 |
| Transformation errors | 0 |
| Duplicate records | 0 |
| Mandatory-field errors | 0 |
| Referential-integrity errors | 0 |
| Overall status | PASS |

These figures represent the large-scale scenario documented for this project; results depend on the dataset and the execution performed.

## Incremental Migration Validation

The incremental pipeline simulates processing only source records newer than the last successfully processed timestamp, known as the **watermark**.

The workflow:

1. Reads the current watermark from `migration_control`.
2. Identifies the maximum source `updated_at` value newer than the watermark.
3. Processes records in the incremental timestamp window.
4. Inserts new records or updates existing target records when mapped values differ.
5. Advances the watermark within the same database transaction.
6. Runs reconciliation and data-quality checks.
7. Generates a JSON validation report.

If no newer source records exist, the loader returns zero affected records without advancing the watermark.

### Current local validation result

The latest documented local execution completed with the following results:

| Metric | Result |
|---|---:|
| Source records | 9 |
| Target records | 9 |
| Matched records | 9 |
| Transformation errors | 0 |
| Duplicate customer IDs | 0 |
| Orphan records | 0 |
| Records affected in this execution | 0 |
| Overall status | PASS |

The zero affected-record count is expected when the watermark already covers the available source data. It demonstrates that rerunning the loader without a newer delta does not create unnecessary changes.

### Incremental validation report

The generated report is written to:

`reports/incremental_validation_report.json`

It contains the execution timestamp, dataset name, affected-record count, individual validation results, and overall status.

## Defect Injection Testing

The framework is designed to detect migration and data-quality defects such as:

- Incorrect transformation values
- Missing target records
- Duplicate business keys
- Null values in mandatory fields
- Referential-integrity violations

When a defect violates an implemented validation rule, the corresponding check should fail and report the discrepancy.

A useful QA workflow is to introduce a controlled defect, execute the relevant tests, confirm that the defect is detected, correct the data or transformation, and rerun the validation.

Test outcomes depend on the specific scenario and validation rules executed.

## AI-Assisted Validation

The project includes AI-oriented agent modules intended to support analysis and investigation of migration-quality results.

### Migration Validation Agent

Analyzes validation evidence and summarizes migration-quality findings.

### Data Quality Investigation Agent

Organizes detected data-quality issues to support investigation and troubleshooting.

### Migration Readiness Agent

Uses validation evidence to produce a structured readiness assessment.

The intended separation of responsibilities is:

```text
Deterministic SQL / Python Validations
                  |
                  v
             PASS / FAIL
                  |
                  v
               AI Agents
                  |
                  v
       Analysis and Investigation
```

**Design principle:** deterministic SQL and Python checks remain the source of truth for data-quality pass/fail decisions. AI-generated analysis is intended to support investigation and interpretation, not override a failed validation.

## Quality Dashboard

The project includes a Streamlit dashboard for presenting migration-quality results.

Start the dashboard locally with:

```bash
streamlit run dashboard/app.py
```

The displayed sections depend on the reports and data available to the dashboard. The intended coverage includes migration status, large-scale validation, incremental validation, record counts, transformations, duplicates, mandatory fields, and referential integrity.

## CI/CD Pipeline

GitHub Actions is configured to automate the project's validation workflow.

The documented pipeline covers activities such as:

- PostgreSQL service initialization
- Database schema initialization
- Automated migration tests
- Synthetic large-scale data generation and validation
- Incremental migration validation
- AI-agent analysis
- JSON report generation
- Artifact upload

The exact steps executed depend on the current workflow configuration in `.github/workflows/data-validation.yml`.

## Technology Stack

### Programming and testing

- Python
- pytest
- psycopg
- SQL

### Database and infrastructure

- PostgreSQL 16
- Docker
- Docker Compose

### CI/CD and version control

- Git
- GitHub
- GitHub Actions

### Dashboard and data analysis

- Streamlit
- Pandas

### Data quality and AI-assisted analysis

- Source-to-target reconciliation
- Transformation validation
- Incremental processing with watermarks
- JSON reporting
- Migration analysis and investigation agents

## Project Structure

```text
netops-migration-qa/
├── .github/
│   └── workflows/
│       └── data-validation.yml
├── agents/
│   ├── migration_validation_agent.py
│   ├── data_quality_investigation_agent.py
│   ├── migration_readiness_agent.py
│   └── agent_assessment_report.py
├── dashboard/
│   └── app.py
├── data/
├── docker/
├── reports/
├── sql/
│   ├── init_database.sql
│   └── incremental_migration.sql
├── src/
│   ├── run_validation.py
│   ├── generate_test_data.py
│   ├── validate_scale.py
│   └── validate_incremental.py
├── tests/
│   └── test_customer_migration.py
├── docker-compose.yml
├── README.md
└── .gitignore
```

Additional files may exist in the repository.

## How to Run Locally

### Prerequisites

- Python installed
- Docker and Docker Compose
- Git
- A local Python virtual environment with the project dependencies installed

### 1. Start PostgreSQL

```bash
docker compose up -d
```

Check the container status:

```bash
docker compose ps
```

### 2. Activate the virtual environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Run the automated test suite

```bash
pytest -v
```

### 4. Run the standard migration validation

```bash
python src/run_validation.py
```

### 5. Run the large-scale validation scenario

```bash
python src/generate_test_data.py
python src/validate_scale.py
```

Review the output and generated reports after execution.

### 6. Run incremental migration validation

```bash
python src/validate_incremental.py
```

This command processes the current incremental scenario and writes the report to `reports/incremental_validation_report.json`.

**Important:** the incremental script expects the source and target tables and the `migration_control` watermark record to exist already. The helper function `setup_incremental_scenario()` resets the demo tables and data; it is not called automatically by the normal execution path. Do not call that helper against data you need to preserve.

### 7. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

## Example Test Results

### Incremental validation

The latest documented local execution returned:

```text
Source records:            9
Target records:            9
Matched records:           9
Transformation errors:     0
Duplicate customer IDs:    0
Orphan records:            0
Affected records:          0
Overall status:             PASS
```

### Large-scale validation

The documented million-record scenario returned:

```text
Source records:            1,000,000
Target records:            1,000,000
Transformation errors:     0
Duplicate records:         0
Mandatory-field errors:    0
Referential-integrity errors: 0
Overall status:            PASS
```

Results may differ depending on the current database state, test data, and execution scenario.

## Skills Demonstrated

- ETL/ELT testing
- Data migration validation
- SQL-based reconciliation
- Source-to-target testing
- Data transformation testing
- Record-count validation
- Duplicate and missing-record detection
- Mandatory-field validation
- Referential-integrity testing
- Incremental migration and watermark management
- Python test automation
- pytest
- PostgreSQL
- Docker and Docker Compose
- CI/CD quality gates
- Automated JSON reporting
- Dashboard development
- AI-assisted quality investigation

## Future Roadmap

Potential future enhancements include:

- Cloud object storage integration
- Azure Data Factory integration
- Managed PostgreSQL deployment
- Additional batch migration scenarios
- Real-time migration simulation
- Expanded data-quality rules
- Environment-based database configuration
- More extensive automated regression coverage
- Expanded AI-agent workflows
- Cloud deployment of the dashboard

These items are roadmap ideas and should not be considered implemented until they are added and verified.

## Repository

GitHub: https://github.com/mauricio-rama/netops-migration-qa

---

**NetOps Migration Quality Platform** — a practical portfolio project focused on reliable data migration, repeatable QA validation, and data-quality reporting.
