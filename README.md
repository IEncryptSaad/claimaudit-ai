# ClaimAudit AI

ClaimAudit AI is a healthcare claims reimbursement audit application that validates claim records, prepares them for analysis, identifies reimbursement anomalies, and presents risk-focused insights through an interactive Streamlit dashboard. The project is designed as a deployable analytics service for teams that need repeatable claim quality checks and early detection of unusual reimbursement patterns.

## Business Problem Solved

Healthcare payers, providers, and audit teams often review large claim files for incomplete records, inconsistent reimbursement behavior, and potentially high-risk payments. Manual review is time-consuming, difficult to standardize, and prone to missed anomalies.

ClaimAudit AI addresses this problem by providing a consistent audit workflow that:

- Validates incoming claims against required schema and data quality rules.
- Transforms claim fields into analysis-ready formats.
- Scores reimbursement patterns for anomalies.
- Labels claims by risk level for review prioritization.
- Produces dashboard analytics and downloadable scored claim reports.
- Provides an orchestration-ready pipeline for scheduled processing.

## Features

- **CSV claim upload:** Upload healthcare claims files directly in the Streamlit application.
- **Synthetic demo data:** Generate representative claim data for demonstrations and deployment checks.
- **Data validation:** Confirm required fields, valid dates, and valid reimbursement amounts before processing.
- **Transformation pipeline:** Standardize dates, monetary fields, reimbursement ratios, claim periods, and duplicate claim IDs.
- **Anomaly detection:** Use an Isolation Forest model to score claims for unusual reimbursement patterns.
- **Risk labeling:** Categorize claims into High, Medium, and Low risk tiers.
- **Dashboard analytics:** View KPI cards, risk distributions, reimbursement patterns, and provider-level high-risk summaries.
- **Report export:** Download scored claims as a CSV report.
- **SQLite persistence:** Persist scored claim records for downstream reporting or auditing workflows in the Airflow-compatible DAG path.
- **Airflow-ready orchestration:** Run the claim audit workflow as a scheduled DAG when Airflow is available.
- **Docker deployment:** Build and run the Streamlit application in a containerized environment.

## Architecture Overview

ClaimAudit AI uses a modular pipeline architecture:

1. **Data ingestion** accepts uploaded CSV files, generated demo claims, or Airflow-managed claim files.
2. **Validation** checks schema completeness, null required values, amount validity, and claim date parseability.
3. **Transformation** converts fields to analytics-ready types, derives reimbursement ratios and claim months, normalizes string fields, and removes duplicate claim IDs.
4. **Anomaly scoring** applies an Isolation Forest model to numeric reimbursement features and assigns risk labels.
5. **Presentation and reporting** render dashboard insights and produce downloadable scored claim reports.
6. **Persistence and orchestration** support SQLite storage and optional Airflow scheduling for production-style workflows.

## Technology Stack

- **Python 3.11** for application and data pipeline logic.
- **Streamlit** for the interactive web application.
- **Pandas** and **NumPy** for data generation, validation, transformation, and analysis.
- **Scikit-learn** for anomaly detection with Isolation Forest.
- **Plotly** for dashboard visualizations.
- **SQLite** for local claim persistence.
- **Apache Airflow** integration pattern for scheduled orchestration.
- **Docker** for containerized deployment.
- **Pytest** for automated validation and deployment readiness checks.

## Repository Structure

```text
.
├── app/
│   ├── data/
│   │   └── generator.py          # Synthetic claims data generation
│   ├── db/
│   │   └── database.py           # SQLite persistence helpers
│   ├── etl/
│   │   ├── transform.py          # Claims transformation pipeline
│   │   └── validate.py           # Claims validation rules
│   ├── ml/
│   │   └── anomaly.py            # Anomaly scoring and risk labeling
│   ├── ui/
│   │   └── dashboard.py          # Streamlit dashboard components
│   └── main.py                   # Streamlit application entry point
├── dags/
│   └── claims_pipeline.py        # Airflow orchestration DAG
├── tests/                        # Unit and deployment readiness tests
├── Dockerfile                    # Container image definition
├── requirements.txt              # Python runtime dependencies
└── README.md                     # Project documentation
```

## Local Installation

### Prerequisites

- Python 3.11 or newer
- `pip`
- Git

### Set Up a Virtual Environment

```bash
git clone <repository-url>
cd claimaudit-ai
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Running the Streamlit Application

Start the web application from the repository root:

```bash
streamlit run app/main.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

From the application, you can either upload a claims CSV or generate synthetic demo data. Both options run the same validation, transformation, anomaly scoring, dashboard, and report export workflow.

## Running Tests

Install test dependencies if they are not already available:

```bash
pip install pytest
```

Run the full test suite:

```bash
pytest
```

The tests cover validation rules, transformation behavior, anomaly scoring, SQLite persistence, and deployment readiness checks for the end-to-end data pipeline.

## Airflow Orchestration Overview

The Airflow DAG in `dags/claims_pipeline.py` documents a scheduled production-style claims workflow. When Airflow is installed, the DAG runs these tasks in sequence:

1. **Ingest claims** from `data/claims.csv`.
2. **Validate claims** using the same validation rules as the Streamlit application.
3. **Transform claims** into analysis-ready records.
4. **Score anomalies** and persist scored claims to SQLite.
5. **Generate report** as a scored claims CSV artifact.

The DAG is safe to import in local environments where Airflow is not installed. This keeps local development lightweight while preserving a clear path for scheduled orchestration in managed Airflow deployments.

## Docker Deployment

Build the container image from the repository root:

```bash
docker build -t claimaudit-ai .
```

Run the application container:

```bash
docker run --rm -p 8501:8501 claimaudit-ai
```

Open the application in a browser:

```text
http://localhost:8501
```

The Docker command starts the Streamlit UI. The UI currently processes uploaded or generated claims for interactive review and CSV export, but it does not write those claims to SQLite. SQLite persistence is currently used by the Airflow-compatible DAG path, which calls the database persistence helpers after scoring claims. If SQLite persistence is wired into the Streamlit UI in the future, mount a host directory to `/app/data` so the database file survives container removal.

## Future Roadmap

- Add authenticated user access for audit teams.
- Support configurable validation rules by payer or line of business.
- Add explainability views for anomaly drivers and claim-level audit notes.
- Expand persistence options to managed relational databases.
- Add batch ingestion from cloud object storage.
- Publish production deployment templates for managed container platforms.
- Add monitoring metrics for claim volume, validation failure rates, and anomaly trends.
- Support model calibration and threshold configuration by organization.
