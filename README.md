
# NetOps Migration Quality Platform

**Automated Data Migration QA | ETL/ELT Validation | Data Quality | Python | SQL | PostgreSQL | Docker | CI/CD | Great Expectations**

NetOps Migration Quality Platform is a portfolio project that simulates an enterprise data migration environment. It demonstrates how automated testing, SQL-based reconciliation, Python validation scripts, data-quality expectations, and interactive dashboards can help identify inconsistencies between source and target systems.

The project uses synthetic customer data and combines deterministic validation rules, automated test execution, incremental migration scenarios, large-scale validation, and AI-assisted investigation workflows.

## Project Overview

The platform demonstrates:

- Source-to-target record-count reconciliation
- Data transformation validation
- Missing-record and duplicate detection
- Mandatory-field validation
- Referential-integrity checks
- Large-scale migration validation using 1,000,000 synthetic customer records
- Incremental migration with timestamp watermarks
- Data-quality expectations with Great Expectations
- Automated JSON quality reports and HTML Data Docs
- pytest-based automated testing
- CI/CD integration with GitHub Actions
- Streamlit dashboard for migration and quality results
- AI-assisted migration analysis modules

## Architecture

```text
                  SOURCE SYSTEM
                       |
                       v
                   ETL / ELT
                       |
                       v
                  TARGET SYSTEM
                       |
                       v
                QA VALIDATION ENGINE
                       |
          +------------+-------------+
          |            |             |
          v            v             v
    Reconciliation  Migration    Data Quality
       Checks       Validation    Expectations
          |            |             |
          +------------+-------------+
                       |
                       v
              QUALITY REPORTS
                JSON + HTML
                       |
           +-----------+-----------+
           |           |           |
           v           v           v
       Streamlit    CI/CD       AI Agents
       Dashboard    Pipeline    (analysis)
```

## Validation Strategy

| Validation | Purpose |
|---|---|
| Record-count reconciliation | Compares source and target record counts. |
| Transformation rules | Checks whether mapped target values match expected transformations. |
| Missing-record detection | Identifies source records absent from the target. |
| Duplicate detection | Detects repeated business keys. |
| Mandatory fields | Checks required columns for null values. |
| Referential integrity | Identifies records without matching references. |
| Incremental reconciliation | Checks source and target consistency after incremental processing. |
| Watermark management | Tracks the latest processed source timestamp. |
| Great Expectations | Evaluates configured data-quality expectations. |
| Automated reporting | Produces structured JSON results and native HTML Data Docs. |

## Large-Scale Migration Validation

The project includes a synthetic migration scenario designed to exercise validation over 1,000,000 customer records.

The workflow includes:

1. Generating synthetic customer data.
2. Loading the data into PostgreSQL.
3. Transforming source records into the target structure.
4. Running migration-quality checks.
5. Generating validation reports.
6. Uploading reports as GitHub Actions artifacts when configured workflow steps complete successfully.

### Documented scale-validation results

| Metric | Result |
|---|---:|
| Source records | 1,000,000 |
| Target records | 1,000,000 |
| Transformation errors | 0 |
| Duplicate customer IDs | 0 |
| Mandatory-field errors | 0 |
| Referential-integrity errors | 0 |
| Overall status | PASS |

These results describe the documented synthetic scenario. Results depend on the dataset and execution performed.

## Incremental Migration Validation

The incremental pipeline simulates processing source records newer than the last successfully processed timestamp, known as the **watermark**.

The workflow:

1. Reads the current watermark from `migration_control`.
2. Identifies eligible source records newer than the watermark.
3. Processes records within the incremental timestamp window.
4. Inserts new records or updates existing target records when mapped values differ.
5. Advances the watermark within the same database transaction.
6. Executes reconciliation and quality checks.
7. Generates a JSON validation report.

If no newer source records exist, the loader can return zero affected records without advancing the watermark.

### Documented local validation results

| Metric | Result |
|---|---:|
| Source records | 9 |
| Target records | 9 |
| Matched records | 9 |
| Duplicate customer IDs | 0 |
| Orphan records | 0 |
| Records affected in the execution | 0 |
| Overall status | PASS |

Zero affected records is expected when the watermark already covers the available source data and no new changes require processing.

Report location:

`reports/incremental_validation_report.json`

The report contains execution information, affected-record counts, individual validation results, and the overall status.

## Great Expectations — Data Quality

The project integrates **Great Expectations 1.24.0** to validate the target customer table:

`target_system.customers_1m`

The current suite contains eight configured expectations.

| # | Expectation | Column or comparison |
|---:|---|---|
| 1 | Values must not be null | `customer_id` |
| 2 | Values must be unique | `customer_id` |
| 3 | Values must not be null | `full_name` |
| 4 | Values must not be null | `customer_status` |
| 5 | Values must belong to an approved set | `customer_status` |
| 6 | Values must not be null | `created_at` |
| 7 | Values must not be null | `migration_timestamp` |
| 8 | Column A must be greater than or equal to column B | `migration_timestamp >= created_at` |

The permitted customer-status values in the current synthetic scenario are `ACTIVE` and `INACTIVE`.

The timestamp expectation checks that the migration timestamp is not earlier than the creation timestamp.

### Latest documented execution

| Metric | Result |
|---|---:|
| Evaluated expectations | 8 |
| Successful expectations | 8 |
| Unsuccessful expectations | 0 |
| Expectation success percentage | 100% |
| Rows evaluated per expectation | 1,000,000 |
| Unexpected values reported | 0 |
| Overall status | PASS |

These figures reflect the execution performed against the current synthetic dataset. The 100% score means all eight configured expectations passed; it does not imply that every possible data-quality rule has been tested.

### Generated reports

The validation script produces:

- **JSON report:** `reports/great_expectations_report.json`
- **HTML Data Docs:** `reports/great_expectations/index.html`

The JSON report provides structured results for downstream integrations and the dashboard. HTML Data Docs provide the native Great Expectations report.

## Quality Dashboard

The project includes an interactive Streamlit dashboard for presenting validation results.

Launch it with:

```bash
streamlit run dashboard/app.py
```

The dashboard includes:

- General migration-quality metrics
- Large-scale validation results
- Incremental migration validation
- Great Expectations status and expectation results
- Quality scores and execution details
- Download access to the Great Expectations HTML report

The dashboard reads generated JSON reports. Run the relevant validation scripts to refresh their results.

## Defect Injection Testing

The framework is designed to detect migration and data-quality defects such as:

- Incorrect transformation values
- Missing target records
- Duplicate business keys
- Null values in mandatory fields
- Referential-integrity violations
- Unsupported customer-status values
- Invalid timestamp relationships

A useful QA workflow is to introduce a controlled defect, execute the relevant validation, confirm that the defect is detected, correct the data or transformation, and rerun the checks.

Actual detection depends on the validation rules configured for each scenario.

## AI-Assisted Validation

The project contains AI-oriented agent modules intended to support analysis and investigation of migration-quality results.

### Migration Validation Agent

Analyzes validation evidence and summarizes migration-quality findings.

### Data Quality Investigation Agent

Organizes detected data-quality issues to support investigation and troubleshooting.

### Migration Readiness Agent

Uses validation evidence to produce a structured readiness assessment.

The intended separation of responsibilities is:

```text
Deterministic SQL / Python / GX Validations
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

**Design principle:** deterministic validation results remain the source of truth for pass/fail decisions. AI-generated analysis supports investigation and interpretation; it should not override a failed validation.

An MCP integration for exposing validation capabilities to an AI agent is a planned enhancement, not a claim that the MCP server is already implemented.

## CI/CD Pipeline

GitHub Actions is configured to automate validation workflows.

The project workflow includes activities such as:

- PostgreSQL service initialization
- Database schema initialization
- Automated migration tests
- Synthetic large-scale data generation and validation
- Incremental migration validation
- AI-agent analysis
- JSON report generation
- Artifact upload

The exact steps executed depend on the workflow configuration in `.github/workflows/data-validation.yml`.

## Technology Stack

### Programming and testing

- Python
- SQL
- pytest
- psycopg

### Database and infrastructure

- PostgreSQL 16
- Docker
- Docker Compose

### Data quality and reporting

- Great Expectations 1.24.0
- JSON reporting
- Great Expectations HTML Data Docs

### Dashboard and data analysis

- Streamlit
- pandas

### CI/CD and version control

- Git
- GitHub
- GitHub Actions

### AI-assisted analysis

- Python-based migration and data-quality agent modules
- MCP integration planned for a future iteration

**Dependency note:** SQLAlchemy is used by Great Expectations' PostgreSQL datasource integration through its SQL connection layer. The project uses pandas in the Streamlit dashboard to structure and display validation reports.

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
│   ├── evidence/
│   ├── great_expectations/
│   ├── great_expectations_report.json
│   ├── incremental_validation_report.json
│   ├── migration_quality_report.json
│   └── scale_validation_report.json
├── sql/
│   ├── init_database.sql
│   └── incremental_migration.sql
├── src/
│   ├── run_validation.py
│   ├── generate_test_data.py
│   ├── validate_scale.py
│   ├── validate_incremental.py
│   ├── validate_with_gx.py
│   └── setup_incremental_ci.py
├── tests/
│   └── test_customer_migration.py
├── docker-compose.yml
├── README.md
└── .gitignore
```

Additional files may exist in the repository.

## How to Run Locally

### Prerequisites

- Python
- Docker and Docker Compose
- Git
- Project dependencies installed in a Python virtual environment

### 1. Start PostgreSQL

```bash
docker compose up -d
```

Verify the container:

```bash
docker compose ps
```

### 2. Activate the virtual environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Run automated tests

```bash
pytest -v
```

### 4. Run standard migration validation

```bash
python src/run_validation.py
```

### 5. Run large-scale validation

```bash
python src/generate_test_data.py
python src/validate_scale.py
```

Review the generated output and reports.

### 6. Run incremental migration validation

```bash
python src/validate_incremental.py
```

This command runs the incremental scenario and writes its report to `reports/incremental_validation_report.json`.

**Important:** the incremental script expects the source and target tables and the `migration_control` watermark record to exist already. The helper `setup_incremental_scenario()` resets demo tables and data; it is not called automatically by the normal execution path. Do not call that helper against data you need to preserve.

### 7. Run Great Expectations data-quality validation

```bash
python src/validate_with_gx.py
```

This runs the configured expectations against `target_system.customers_1m` and generates the JSON report and HTML Data Docs.

### 8. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

## Example Test Results

### Incremental validation

```text
Source records:             9
Target records:             9
Matched records:            9
Duplicate customer IDs:     0
Orphan records:             0
Affected records:           0
Overall status:             PASS
```

### Large-scale validation

```text
Source records:             1,000,000
Target records:             1,000,000
Transformation errors:      0
Duplicate records:          0
Mandatory-field errors:     0
Referential-integrity errors: 0
Overall status:             PASS
```

### Great Expectations

```text
Evaluated expectations:     8
Successful expectations:    8
Unsuccessful expectations:  0
Success percentage:         100%
Rows evaluated per rule:    1,000,000
Unexpected values:          0
Overall status:             PASS
```

Results can differ depending on the database state, test data, and execution scenario.

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
- Great Expectations
- Python test automation
- pytest
- PostgreSQL
- Docker and Docker Compose
- CI/CD quality gates
- JSON and HTML reporting
- Streamlit dashboard development
- pandas-based report presentation
- AI-assisted quality investigation

## Future Roadmap

Potential enhancements include:

- MCP server exposing migration-validation tools
- AI agent that queries validation results and explains failures
- Controlled defect injection and recovery demonstrations
- Additional business-rule and data-quality expectations
- Environment-based database configuration
- More extensive automated regression coverage
- Cloud object storage integration
- Azure Data Factory integration
- Managed PostgreSQL deployment
- Real-time migration simulation
- Cloud deployment of the dashboard

These items are roadmap ideas and should not be considered implemented until they are added and verified.

## Repository

GitHub: https://github.com/mauricio-rama/netops-migration-qa

---

**NetOps Migration Quality Platform** — a practical portfolio project focused on reliable data migration, repeatable QA validation, and data-quality reporting.
