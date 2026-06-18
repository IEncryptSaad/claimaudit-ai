"""Illustrative Airflow DAG for the ClaimAudit AI claims pipeline.

The module is safe to import when Airflow is not installed, which keeps local
Streamlit and test environments lightweight while documenting a production-style
orchestration path.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except ImportError:  # Airflow is optional for local development and tests.
    DAG = None  # type: ignore[assignment]
    PythonOperator = None  # type: ignore[assignment]

from app.db.database import save_claims
from app.etl.transform import transform_claims as transform_claims_frame
from app.etl.validate import validate_claims as validate_claims_frame
from app.ml.anomaly import score_claim_anomalies

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_CLAIMS_PATH = DATA_DIR / "claims.csv"
VALIDATED_CLAIMS_PATH = DATA_DIR / "claims_validated.csv"
TRANSFORMED_CLAIMS_PATH = DATA_DIR / "claims_transformed.csv"
SCORED_CLAIMS_PATH = DATA_DIR / "claims_scored.csv"
REPORT_PATH = DATA_DIR / "claims_report.csv"


def ingest_claims(**_: Any) -> str:
    """Load raw claims from the shared data directory."""
    if not RAW_CLAIMS_PATH.exists():
        raise FileNotFoundError(f"Claims input file not found: {RAW_CLAIMS_PATH}")

    df = pd.read_csv(RAW_CLAIMS_PATH)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(VALIDATED_CLAIMS_PATH, index=False)
    logger.info("Ingested %s claim row(s)", len(df))
    return str(VALIDATED_CLAIMS_PATH)


def validate_claims(**_: Any) -> str:
    """Validate ingested claims before transformation."""
    df = pd.read_csv(VALIDATED_CLAIMS_PATH)
    validation_result = validate_claims_frame(df)
    if not validation_result.get("is_valid", False):
        errors = validation_result.get("errors", [])
        raise ValueError("Claims validation failed: " + "; ".join(map(str, errors)))

    logger.info("Validated %s claim row(s)", len(df))
    return str(VALIDATED_CLAIMS_PATH)


def transform_claims(**_: Any) -> str:
    """Transform validated claims into analytics-ready records."""
    df = pd.read_csv(VALIDATED_CLAIMS_PATH)
    transformed_df = transform_claims_frame(df)
    transformed_df.to_csv(TRANSFORMED_CLAIMS_PATH, index=False)
    logger.info("Transformed %s claim row(s)", len(transformed_df))
    return str(TRANSFORMED_CLAIMS_PATH)


def score_anomalies(**_: Any) -> str:
    """Score transformed claims and persist results."""
    df = pd.read_csv(TRANSFORMED_CLAIMS_PATH)
    scored_df = score_claim_anomalies(df)
    scored_df.to_csv(SCORED_CLAIMS_PATH, index=False)
    save_claims(scored_df)
    logger.info("Scored and saved %s claim row(s)", len(scored_df))
    return str(SCORED_CLAIMS_PATH)


def generate_report(**_: Any) -> str:
    """Generate a simple scored-claims report artifact."""
    scored_df = pd.read_csv(SCORED_CLAIMS_PATH)
    report_df = scored_df.sort_values(
        by=["risk_label", "anomaly_score"], ascending=[True, False]
    )
    report_df.to_csv(REPORT_PATH, index=False)
    logger.info("Generated claims report at %s", REPORT_PATH)
    return str(REPORT_PATH)


if DAG and PythonOperator:
    with DAG(
        dag_id="claimaudit_claims_pipeline",
        description="Validate, transform, score, and report on healthcare claims.",
        start_date=datetime(2024, 1, 1),
        schedule="@daily",
        catchup=False,
        tags=["claimaudit", "claims", "anomaly-detection"],
    ) as dag:
        ingest_task = PythonOperator(task_id="ingest_claims", python_callable=ingest_claims)
        validate_task = PythonOperator(task_id="validate_claims", python_callable=validate_claims)
        transform_task = PythonOperator(task_id="transform_claims", python_callable=transform_claims)
        score_task = PythonOperator(task_id="score_anomalies", python_callable=score_anomalies)
        report_task = PythonOperator(task_id="generate_report", python_callable=generate_report)

        ingest_task >> validate_task >> transform_task >> score_task >> report_task
else:
    dag = None
