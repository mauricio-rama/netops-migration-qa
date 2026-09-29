# NetOps Migration Quality Platform

Automated data migration and data quality validation framework built with Python, pytest, SQL, and PostgreSQL.

## Project Overview

This project simulates an enterprise data migration scenario where data is extracted from a source system, transformed through an ETL process, loaded into a target system, and automatically validated.

The main objective is to demonstrate automated testing strategies for data migration, transformation validation, reconciliation, and data quality engineering.

## Architecture

Source System
     │
     ▼
    ETL
     │
     ▼
Target System
     │
     ▼
QA Validation Engine
     │
     ├── Transformation Validation
     ├── Record Count Reconciliation
     ├── Missing Records Detection
     ├── Duplicate Detection
     ├── Mandatory Field Validation
     └── Referential Integrity
     │
     ▼
Migration Quality Report

## Validation Strategy

The automated validation framework currently performs:

Validation	                Description
Transformation Rules	        Validates source-to-target transformation logic
Record Count Reconciliation	Compares source and target record counts
Missing Records	                Identifies source records missing from target
Duplicate Records	        Detects duplicated business keys
Mandatory Fields	        Detects NULL values in required fields
Referential Integrity	        Detects orphan records between related tables

## Technology Stack

Python 
Pytest
Psycopg
PostgreSQL 
Docker
Docker Compose
SQL
Git
GitHub

## How to Run

1. Start PostgreSQL
docker compose up -d
2. Activate the Python environment
source .venv/bin/activate
3. Run the automated validations
pytest -v
4. Generate the migration quality report
python src/run_validation.py

## Migration Quality Report

The validation framework generates automated JSON reports containing:

Total validations
Passed validations
Failed validations
Overall migration status
Individual validation results

Example:

Total validations: 6
Passed: 6
Failed: 0
Overall status: PASS

## Defect Injection Testing

The framework has been tested by intentionally introducing data quality defects, including:

Incorrect transformation values
Missing target records
Duplicate records
NULL mandatory fields
Referential integrity violations

The automated tests successfully detected each injected defect and returned the expected FAIL status.

After correcting each defect, the complete validation suite returned:

6 passed

## Future Roadmap

Planned improvements include:

GitHub Actions CI/CD pipeline
Automated migration quality dashboards
Large-scale synthetic datasets
Incremental migration validation
Batch and real-time migration scenarios
Data reconciliation reports
Azure cloud deployment
AI-assisted data quality investigation
Migration validation AI agents

## Project Focus

This project demonstrates practical experience in:

Data Migration Testing
ETL / ELT Validation
Data Quality Engineering
SQL Testing
Automated Testing
Python Test Automation
Database Testing
Reconciliation Testing
CI/CD
Quality Engineering

## CI/CD Validation Evidence

The project includes a GitHub Actions CI/CD pipeline that automatically initializes the PostgreSQL database and executes the data migration validation suite on every push and pull request.

The pipeline was intentionally tested with a migration defect:

- 🟢 Initial validation: all tests passed
- 🔴 Intentional transformation defect: CI detected the incorrect migrated value and failed the pipeline
- 🟢 Defect correction: CI passed again after the transformation was fixed

This demonstrates automated defect detection, migration validation, and CI/CD quality gates.