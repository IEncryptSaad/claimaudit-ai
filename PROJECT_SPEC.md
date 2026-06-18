# ClaimAudit AI MVP

## Project Objective

Build a production-style Healthcare Claims Reimbursement Audit Agent that can be developed and deployed using AI-assisted coding while demonstrating ETL, machine learning, anomaly detection, reimbursement analytics, and scalable architecture.

---

## Core Features

### Claims Processing

* Upload healthcare claims CSV
* Generate synthetic healthcare claims data
* Validate claim schema
* Clean and normalize claims
* Store processed claims

### ETL Pipeline

* Ingest claims
* Validate records
* Transform data
* Engineer features
* Score claims
* Generate reports

### Machine Learning

* Isolation Forest anomaly detection
* Reimbursement risk scoring
* Provider risk aggregation
* Claim-level anomaly explanations

### Dashboard

* Claims overview
* Anomaly summary
* Provider risk summary
* Reimbursement analytics
* Downloadable CSV reports

---

## Technical Requirements

### Backend

* Python 3.13+
* Modular architecture
* API-first design

### Frontend

* Streamlit

### Database

* SQLite for MVP
* PostgreSQL-compatible schema
* Easy migration to Supabase PostgreSQL

### Machine Learning

* pandas
* numpy
* scikit-learn
* Isolation Forest
* XGBoost (optional)

### ETL / Orchestration

* Python ETL pipeline
* Airflow-compatible DAG
* Future Apache Airflow deployment support

### Visualization

* Plotly

### Deployment

* Docker
* Streamlit Community Cloud
* Hugging Face Spaces compatible

### CI/CD

* GitHub Actions

---

## Repository Structure

```text
claimaudit-ai/

app/
│
├── main.py
├── config.py
│
├── etl/
│   ├── ingest.py
│   ├── validate.py
│   └── transform.py
│
├── ml/
│   ├── anomaly.py
│   └── scoring.py
│
├── reports/
│   └── exporter.py
│
├── db/
│   └── database.py
│
├── ui/
│   └── dashboard.py
│
└── data/
    └── generator.py

dags/
└── claims_pipeline.py

tests/

requirements.txt

Dockerfile

docker-compose.yml

README.md
```

---

## Deliverables

* Working web application
* CSV upload
* Claims validation
* ETL pipeline
* Airflow-compatible DAG
* Anomaly detection
* Risk scoring
* Dashboard
* CSV export
* Docker support
* GitHub repository
* Deployment-ready code

---

## Success Criteria

A user can:

1. Upload claims data
2. Run ETL processing
3. Detect anomalous claims
4. View risk scores
5. Analyze providers
6. Download audit reports

within a single deployable web application.
