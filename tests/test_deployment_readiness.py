"""Deployment readiness checks for the ClaimAudit AI data pipeline."""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.data.generator import generate_synthetic_claims
from app.etl.transform import transform_claims
from app.etl.validate import REQUIRED_COLUMNS, validate_claims
from app.ml.anomaly import score_claim_anomalies


def test_synthetic_data_generation_produces_required_claim_schema() -> None:
    """Synthetic data generation should produce deployable claims input."""
    claims_df = generate_synthetic_claims(rows=50)

    assert len(claims_df) == 50
    assert set(REQUIRED_COLUMNS).issubset(claims_df.columns)
    assert claims_df["claim_id"].is_unique
    assert (claims_df["claim_amount"] > 0).all()
    assert (claims_df["reimbursed_amount"] >= 0).all()


def test_validation_pipeline_accepts_generated_claims() -> None:
    """Generated claims should pass the production validation rules."""
    claims_df = generate_synthetic_claims(rows=50)

    validation_result = validate_claims(claims_df)

    assert validation_result == {"is_valid": True, "errors": []}


def test_transformation_pipeline_prepares_generated_claims() -> None:
    """Generated claims should transform into analytics-ready records."""
    claims_df = generate_synthetic_claims(rows=50)

    transformed_df = transform_claims(claims_df)

    assert len(transformed_df) == len(claims_df)
    assert pd.api.types.is_datetime64_any_dtype(transformed_df["claim_date"])
    assert pd.api.types.is_numeric_dtype(transformed_df["claim_amount"])
    assert pd.api.types.is_numeric_dtype(transformed_df["reimbursed_amount"])
    assert "reimbursement_ratio" in transformed_df.columns
    assert "claim_month" in transformed_df.columns
    assert transformed_df["reimbursement_ratio"].notna().all()


def test_anomaly_detection_pipeline_scores_transformed_claims() -> None:
    """Transformed generated claims should receive anomaly and risk outputs."""
    claims_df = generate_synthetic_claims(rows=100)
    transformed_df = transform_claims(claims_df)

    scored_df = score_claim_anomalies(transformed_df)

    assert len(scored_df) == len(transformed_df)
    assert "anomaly_score" in scored_df.columns
    assert "is_anomaly" in scored_df.columns
    assert "risk_label" in scored_df.columns
    assert pd.api.types.is_numeric_dtype(scored_df["anomaly_score"])
    assert pd.api.types.is_bool_dtype(scored_df["is_anomaly"])
    assert set(scored_df["risk_label"]).issubset({"High", "Medium", "Low"})
    assert scored_df["risk_label"].notna().all()
