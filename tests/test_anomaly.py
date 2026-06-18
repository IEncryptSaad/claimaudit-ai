"""Tests for healthcare claims anomaly detection."""

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ml.anomaly import score_claim_anomalies


def _claims_df() -> pd.DataFrame:
    """Create a claims DataFrame for anomaly scoring tests."""
    return pd.DataFrame(
        {
            "claim_amount": [100.0, 200.0, 150.0, 175.0, 5000.0],
            "reimbursed_amount": [80.0, 195.0, 75.0, 100.0, 5000.0],
            "reimbursement_ratio": [0.8, 0.975, 0.5, 0.57, 1.0],
        }
    )


def test_score_claim_anomalies_copies_input_dataframe() -> None:
    """Anomaly scoring should not mutate the input DataFrame."""
    df = _claims_df()

    scored_df = score_claim_anomalies(df)

    assert scored_df is not df
    assert "anomaly_score" not in df.columns
    assert "is_anomaly" not in df.columns
    assert "risk_label" not in df.columns


def test_score_claim_anomalies_adds_expected_columns() -> None:
    """Anomaly scoring should append score, flag, and risk columns."""
    scored_df = score_claim_anomalies(_claims_df())

    assert "anomaly_score" in scored_df.columns
    assert "is_anomaly" in scored_df.columns
    assert "risk_label" in scored_df.columns
    assert pd.api.types.is_numeric_dtype(scored_df["anomaly_score"])
    assert pd.api.types.is_bool_dtype(scored_df["is_anomaly"])


def test_score_claim_anomalies_assigns_medium_label_for_high_ratio() -> None:
    """Non-anomalous high reimbursement ratios should be labeled Medium."""
    df = pd.DataFrame(
        {
            "claim_amount": [100.0] * 30,
            "reimbursed_amount": [95.0] * 30,
            "reimbursement_ratio": [0.95] * 30,
        }
    )

    scored_df = score_claim_anomalies(df)

    assert set(scored_df["is_anomaly"]) == {False}
    assert set(scored_df["risk_label"]) == {"Medium"}


def test_score_claim_anomalies_handles_missing_numeric_values() -> None:
    """Missing numeric values should be safely filled before model scoring."""
    df = _claims_df()
    df.loc[0, "claim_amount"] = None
    df.loc[1, "reimbursed_amount"] = None
    df.loc[2, "reimbursement_ratio"] = None

    scored_df = score_claim_anomalies(df)

    assert not scored_df["anomaly_score"].isna().any()
    assert len(scored_df) == len(df)


def test_score_claim_anomalies_requires_numeric_feature_columns() -> None:
    """Missing required feature columns should raise a clear error."""
    df = _claims_df().drop(columns=["reimbursement_ratio"])

    with pytest.raises(ValueError, match="reimbursement_ratio"):
        score_claim_anomalies(df)
