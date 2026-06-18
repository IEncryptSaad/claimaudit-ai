"""Tests for healthcare claims transformation."""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.etl.transform import transform_claims


def _raw_claims_df() -> pd.DataFrame:
    """Create a minimal raw claims DataFrame for transform tests."""
    return pd.DataFrame(
        {
            "claim_id": [" CLM-001 ", " CLM-001 ", "CLM-002"],
            "patient_id": [" PAT-001 ", " PAT-001 ", "PAT-002"],
            "provider_id": [" PRV-001", " PRV-001", "PRV-002"],
            "diagnosis_code": [" E11.9 ", " E11.9 ", "I10"],
            "procedure_code": [" 99213 ", " 99213 ", "99214"],
            "claim_amount": ["100.00", "100.00", "200.00"],
            "reimbursed_amount": ["80.00", "80.00", "50.00"],
            "payer_type": [" commercial ", " commercial ", "medicare"],
            "claim_date": ["2026-01-15", "2026-01-15", "2026-02-20"],
        }
    )


def test_transform_claims_copies_input_dataframe() -> None:
    """Transforming claims should not mutate the original DataFrame."""
    df = _raw_claims_df()

    transformed_df = transform_claims(df)

    assert transformed_df is not df
    assert df.loc[0, "claim_id"] == " CLM-001 "
    assert not pd.api.types.is_datetime64_any_dtype(df["claim_date"])


def test_transform_claims_converts_dates_and_amounts() -> None:
    """Claim dates and amount columns should use analysis-friendly dtypes."""
    transformed_df = transform_claims(_raw_claims_df())

    assert pd.api.types.is_datetime64_any_dtype(transformed_df["claim_date"])
    assert pd.api.types.is_numeric_dtype(transformed_df["claim_amount"])
    assert pd.api.types.is_numeric_dtype(transformed_df["reimbursed_amount"])


def test_transform_claims_adds_reimbursement_ratio_and_claim_month() -> None:
    """Derived reimbursement ratio and claim month columns should be added."""
    transformed_df = transform_claims(_raw_claims_df())

    clm_001 = transformed_df[transformed_df["claim_id"] == "CLM-001"].iloc[0]
    clm_002 = transformed_df[transformed_df["claim_id"] == "CLM-002"].iloc[0]

    assert clm_001["reimbursement_ratio"] == 0.8
    assert clm_002["reimbursement_ratio"] == 0.25
    assert clm_001["claim_month"] == pd.Period("2026-01", freq="M")


def test_transform_claims_strips_strings_and_removes_duplicate_claims() -> None:
    """String values should be trimmed before duplicate claim IDs are removed."""
    transformed_df = transform_claims(_raw_claims_df())

    assert transformed_df["claim_id"].tolist() == ["CLM-001", "CLM-002"]
    assert transformed_df["patient_id"].tolist() == ["PAT-001", "PAT-002"]
    assert len(transformed_df) == 2
