# NetOps Migration Quality Platform

**Automated Data Migration QA | ETL/ELT Validation | Data Quality | Python | SQL | PostgreSQL | Great Expectations | MCP | Gemini AI | Streamlit | CI/CD**

NetOps Migration Quality Platform is a data migration quality assurance project that simulates an enterprise migration environment. It combines deterministic data validation, SQL-based reconciliation, Python automation, incremental migration testing, large-scale data validation, data-quality expectations, CI/CD workflows, and AI-assisted analysis.

The platform uses synthetic customer data to demonstrate how QA engineers can validate source-to-target consistency, identify migration defects, generate evidence-based reports, and use an AI agent to interpret validation results through controlled tools exposed by the Model Context Protocol (MCP).

The project is designed around a key principle: **deterministic validation remains the source of truth for data-quality and migration pass/fail decisions; AI supports analysis and investigation without replacing those results.**

## Project Highlights

- Source-to-target data reconciliation.
- Transformation-rule validation.
- Missing-record and duplicate detection.
- Mandatory-field and referential-integrity checks.
- Large-scale migration validation using 1,000,000 synthetic customer records.
- Incremental migration simulation with timestamp watermarks.
- Great Expectations data-quality validation.
- Automated JSON reports and HTML Data Docs.
- pytest-based automated testing.
- GitHub Actions CI/CD workflow.
- Interactive Streamlit dashboard.
- Gemini-powered migration analysis.
- MCP server exposing read-only migration and data-quality reporting tools.
- AI-assisted interpretation of actual validation evidence.

## Architecture

```text
                  SYNTHETIC SOURCE DATA
                           |
                           v
                     ETL / ELT FLOW
                           |
                           v
                    POSTGRESQL TARGET
                           |
                           v
                 DETERMINISTIC QA ENGINE
                           |
              +------------+------------+
              |            |            |
              v            v            v
        Reconciliation  Migration   Great Expectations
           Checks      Validation    Data Quality
              |            |            |
              +------------+------------+
                           |
                           v
                 VALIDATION REPORTS
                     JSON + HTML
                           |
              +------------+------------+
              |            |            |
              v            v            v
          Streamlit     GitHub       MCP Server
          Dashboard     Actions          |
                                         v
                                    Gemini AI
                                         |
                                         v
                              Evidence-Based Analysis
```

### AI-assisted analysis flow

```text
Streamlit Dashboard
        |
        | Analyze with AI
        v
Gemini AI Agent
        |
        | MCP tool calls
        v
Local MCP Server (stdio)
        |
        +--> get_migration_quality
        |
        +--> get_data_quality
        |
        +--> get_project_status
        |
        v
Current Project Reports and Status
        |
        v
Gemini Analysis
        |
        v
Results Displayed in Streamlit
```

The AI agent retrieves project information through MCP tools before generating its assessment. The deterministic reports remain authoritative for validation outcomes.

## Validation Strategy

| Validation | Purpose |
|---|---|
| Record-count reconciliation | Compares source and target record counts. |
| Transformation validation | Verifies that mapped values follow expected transformation rules. |
| Missing-record detection | Identifies records missing from the target. |
| Duplicate detection | Detects duplicate business keys. |
| Mandatory-field validation | Checks required fields for null values. |
| Referential integrity | Identifies records with missing references. |
| Incremental reconciliation | Checks consistency after incremental processing. |
| Watermark management | Tracks the latest successfully processed source timestamp. |
| Great Expectations | Evaluates configured data-quality expectations. |
| Automated reporting | Produces structured JSON results and HTML Data Docs. |
| AI-assisted analysis | Summarizes current migration and data-quality evidence retrieved through MCP. |

## Large-Scale Migration Validation

The project includes a synthetic migration scenario that exercises validation against 1,000,000 customer records.

### Workflow

1. Generate synthetic customer data.
2. Load source and target datasets into PostgreSQL.
3. Execute the migration or transformation scenario.
4. Run deterministic validation checks.
5. Generate JSON reports.
6. Execute the configured CI/CD workflow and publish eligible artifacts.

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

These figures represent a documented synthetic test execution. Results may change depending on the dataset, database state, and validation run.

Report location:

`reports/scale_validation_report.json`

## Incremental Migration Validation

The incremental pipeline simulates processing source records newer than the last successfully processed timestamp, known as the **watermark**.

### Workflow

1. Read the current watermark from `migration_control`.
2. Identify eligible source records newer than the watermark.
3. Process records within the incremental timestamp window.
4. Insert new records or update existing target records when mapped values differ.
5. Advance the watermark within the same database transaction.
6. Execute reconciliation and quality checks.
7. Generate a JSON validation report.

If no eligible changes exist, the pipeline can process zero affected records without advancing the watermark.

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

The configured suite contains eight expectations.

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

The permitted status values in the current synthetic scenario are `ACTIVE` and `INACTIVE`.

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

The 100% score means all eight configured expectations passed in that execution. It does not imply that every possible data-quality rule has been tested.

### Generated reports

- JSON report: `reports/great_expectations_report.json`
- HTML Data Docs: `reports/great_expectations/index.html`

The JSON report supports downstream integrations and dashboard rendering. HTML Data Docs provide the native Great Expectations report.

## Quality Dashboard

The project includes an interactive Streamlit dashboard that presents migration and data-quality results.

### Dashboard sections

1. **General Migration Quality** — validation counts, pass/fail totals, quality score, and individual results.
2. **Scale Validation** — source and target counts, execution time, and large-scale validation outcomes.
3. **Incremental Migration Validation** — processed and inserted records, reconciliation results, and report details.
4. **Great Expectations — Data Quality** — expectation results, quality metrics, and access to the HTML report.
5. **AI-Powered Migration Analysis** — Gemini analysis based on information retrieved through MCP.

### Launch the dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard reads generated JSON reports. Run the corresponding validation scripts to refresh the underlying results before interpreting the dashboard.

## AI-Powered Migration Analysis

The project integrates a Gemini AI agent with a local MCP server to support evidence-based analysis of migration and data-quality results.

### Components

**Gemini AI agent — `agents/gemini_agent.py`**

- Connects to the Gemini API using an environment-configured API key.
- Retrieves available MCP tools.
- Requests project status and detailed migration and data-quality reports.
- Preserves conversation history across tool calls.
- Generates a natural-language assessment from returned evidence.
- Returns the analysis to the calling application.

**MCP server — `agents/mcp_server.py`**

The local server exposes three reporting tools:

| Tool | Purpose |
|---|---|
| `get_migration_quality` | Retrieves migration-quality report information. |
| `get_data_quality` | Retrieves data-quality report information. |
| `get_project_status` | Retrieves the overall project validation status. |

These tools are intended to provide reporting and status information rather than modify validation outcomes.

**Streamlit integration — `dashboard/app.py`**

The dashboard provides an **Analyze with AI** button. When selected, it invokes the Gemini agent, which communicates with the MCP server and returns its analysis to the dashboard.

### Analysis principles

- Use current report evidence obtained through MCP tools.
- Do not invent missing metrics or validation results.
- Identify missing information explicitly.
- Keep deterministic PASS/FAIL outcomes authoritative.
- Use AI-generated findings as supporting analysis, not as a replacement for validation.

### Configure the Gemini API

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
```

Replace the placeholder with your own API key. Do not commit `.env` or publish API credentials in source code, screenshots, reports, or documentation.

The project uses `python-dotenv` to load the environment variable and `google-genai` to communicate with Gemini.

AI analysis requires valid API credentials, network access to the Gemini API, and the installed project dependencies. API usage may incur charges depending on your provider account and terms.

## Defect Injection Testing

The framework is designed to support testing of migration and data-quality defects, including:

- Incorrect transformation values.
- Missing target records.
- Duplicate business keys.
- Null values in mandatory fields.
- Referential-integrity violations.
- Unsupported customer-status values.
- Invalid timestamp relationships.

A useful QA workflow is to introduce a controlled defect, execute the relevant validation, confirm detection, correct the data or transformation, and rerun the checks.

Actual detection depends on the validation rules configured for each scenario.

## CI/CD Pipeline

GitHub Actions is configured to automate validation workflows.

Depending on the current workflow configuration, the pipeline includes activities such as:

- PostgreSQL service initialization.
- Database schema initialization.
- Automated migration tests.
- Synthetic large-scale data generation and validation.
- Incremental migration validation.
- JSON report generation.
- Artifact upload.

The exact steps executed are defined in:

`.github/workflows/data-validation.yml`

Local Gemini analysis requires the appropriate API configuration. Do not assume that a CI workflow can call Gemini unless the required secret and corresponding workflow steps are configured.

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
- SQLAlchemy, used by the PostgreSQL connection layer of the Great Expectations datasource integration

### AI and tool integration

- Google Gen AI SDK (`google-genai`)
- Gemini API
- Model Context Protocol (`mcp`)
- python-dotenv
- Python-based AI agent
- MCP tools for migration quality, data quality, and project status

### CI/CD and version control

- Git
- GitHub
- GitHub Actions

Exact dependency versions are maintained in `requirements.txt` where pinned.

## Project Structure

```text
netops-migration-qa/
├── .github/
│   └── workflows/
│       └── data-validation.yml
├── agents/
│   ├── context/
│   ├── agent_assessment_report.py
│   ├── data_quality_investigation_agent.py
│   ├── gemini_agent.py
│   ├── mcp_server.py
│   ├── migration_readiness_agent.py
│   └── migration_validation_agent.py
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
├── requirements.txt
├── README.md
└── .gitignore
```

Additional files may exist in the repository. This tree highlights the main project components.

## How to Run Locally

### Prerequisites

- Git
- Python compatible with the installed project dependencies
- Docker and Docker Compose
- A Gemini API key for AI-assisted analysis
- Internet access for Gemini API calls

### 1. Clone the repository

```bash
git clone https://github.com/mauricio-rama/netops-migration-qa.git
cd netops-migration-qa
```

### 2. Create and activate a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API

Create a `.env` file in the repository root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
```

Keep the actual API key private and out of version control.

### 5. Start PostgreSQL

```bash
docker compose up -d
```

Verify the container:

```bash
docker compose ps
```

Use the repository's configured database settings. Do not assume local credentials are suitable for other environments.

### 6. Run automated tests

```bash
pytest -v
```

### 7. Run standard migration validation

```bash
python src/run_validation.py
```

### 8. Run large-scale validation

```bash
python src/generate_test_data.py
python src/validate_scale.py
```

Review the generated reports and console output.

### 9. Run incremental migration validation

```bash
python src/validate_incremental.py
```

The script writes its report to:

`reports/incremental_validation_report.json`

**Important:** the incremental script expects the source and target tables and the `migration_control` watermark record to exist. The helper `setup_incremental_scenario()` resets demo tables and data; it is not called automatically by the normal execution path. Do not call that helper against data you need to preserve.

### 10. Run Great Expectations validation

```bash
python src/validate_with_gx.py
```

This runs the configured expectations against `target_system.customers_1m` and generates the JSON report and HTML Data Docs.

### 11. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Open the local URL displayed by Streamlit.

### 12. Run the AI agent independently (optional)

With dependencies installed and `.env` configured:

```bash
python agents/gemini_agent.py
```

This invokes the Gemini agent, which connects to the local MCP server and retrieves report information through its tools.

The AI-assisted dashboard section can also initiate the analysis through **Analyze with AI**.

## Example Test Results

The following examples reflect documented synthetic test executions, not guaranteed outcomes for every run.

### Incremental validation

```text
Source records:                9
Target records:                9
Matched records:               9
Duplicate customer IDs:        0
Orphan records:                 0
Affected records:               0
Overall status:                PASS
```

### Large-scale validation

```text
Source records:                1,000,000
Target records:                1,000,000
Transformation errors:         0
Duplicate records:             0
Mandatory-field errors:        0
Referential-integrity errors:  0
Overall status:                PASS
```

### Great Expectations

```text
Evaluated expectations:        8
Successful expectations:       8
Unsuccessful expectations:     0
Success percentage:            100%
Rows evaluated per rule:       1,000,000
Unexpected values:             0
Overall status:                PASS
```

The AI agent can summarize available reports, but its generated narrative should always be checked against the underlying deterministic evidence.

## Skills Demonstrated

- ETL/ELT testing.
- Data migration validation.
- SQL-based reconciliation.
- Source-to-target testing.
- Data transformation testing.
- Record-count validation.
- Duplicate and missing-record detection.
- Mandatory-field validation.
- Referential-integrity testing.
- Incremental migration and watermark management.
- Great Expectations.
- Python test automation.
- pytest.
- PostgreSQL.
- Docker and Docker Compose.
- CI/CD quality gates.
- JSON and HTML reporting.
- Streamlit dashboard development.
- pandas-based report presentation.
- MCP server and tool integration.
- Gemini API integration.
- Evidence-based AI-assisted quality investigation.

## Future Roadmap

Potential enhancements include:

- Expand MCP tools with additional read-only reconciliation evidence.
- Add more detailed failure-level analysis and investigation workflows.
- Increase business-rule and data-quality expectation coverage.
- Improve automated regression coverage.
- Add controlled defect-injection demonstrations.
- Improve environment-based database configuration.
- Integrate cloud object storage.
- Explore Azure Data Factory integration.
- Evaluate managed PostgreSQL deployment.
- Add more realistic real-time migration simulations.
- Explore secure cloud deployment of the dashboard.

Roadmap items are proposals and should not be considered implemented until they have been developed and verified.

## Repository

GitHub: https://github.com/mauricio-rama/netops-migration-qa

## Author and Copyright

**Created and maintained by Mauricio Antonio Ramirez Macias.**

Copyright © 2026 Mauricio Antonio Ramirez Macias. All rights reserved.

The original project code, custom validation workflows, project architecture, integration logic, documentation, and other original materials authored for this repository are attributed to the author, subject to the licenses and rights applicable to third-party libraries, services, tools, and components used by the project.

Third-party technologies retain their respective names, trademarks, and licensing terms. No ownership of third-party software or services is claimed by this notice.

---

**NetOps Migration Quality Platform** — an engineering portfolio project demonstrating data migration reliability, automated QA validation, data-quality reporting, and AI-assisted analysis.