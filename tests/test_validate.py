"""Tests for healthcare claims validation."""

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.etl.validate import validate_claims


def _valid_claims_df() -> pd.DataFrame:
    """Create a minimal valid claims DataFrame for tests."""
    return pd.DataFrame(
        {
            "claim_id": ["CLM-001"],
            "patient_id": ["PAT-001"],
            "provider_id": ["PRV-001"],
            "diagnosis_code": ["E11.9"],
            "procedure_code": ["99213"],
            "claim_amount": [125.50],
            "reimbursed_amount": [100.00],
            "payer_type": ["commercial"],
            "claim_date": ["2026-01-15"],
        }
    )


def test_validate_claims_accepts_valid_dataframe() -> None:
    """A complete, well-formed claims DataFrame should pass validation."""
    result = validate_claims(_valid_claims_df())

    assert result == {"is_valid": True, "errors": []}


def test_validate_claims_reports_missing_required_columns() -> None:
    """Missing required columns should fail validation with an error."""
    df = _valid_claims_df().drop(columns=["provider_id"])

    result = validate_claims(df)

    assert result["is_valid"] is False
    assert any("Missing required columns" in error for error in result["errors"])
    assert any("provider_id" in error for error in result["errors"])


def test_validate_claims_reports_null_required_values() -> None:
    """Null values in required columns should fail validation."""
    df = _valid_claims_df()
    df.loc[0, "patient_id"] = None

    result = validate_claims(df)

    assert result["is_valid"] is False
    assert any("patient_id" in error and "null" in error for error in result["errors"])


def test_validate_claims_reports_invalid_amounts() -> None:
    """Invalid claim and reimbursement amounts should fail validation."""
    df = _valid_claims_df()
    df.loc[0, "claim_amount"] = 0
    df.loc[0, "reimbursed_amount"] = -1

    result = validate_claims(df)

    assert result["is_valid"] is False
    assert any("claim_amount" in error for error in result["errors"])
    assert any("reimbursed_amount" in error for error in result["errors"])


def test_validate_claims_reports_invalid_claim_date() -> None:
    """Claim dates that cannot be parsed should fail validation."""
    df = _valid_claims_df()
    df.loc[0, "claim_date"] = "not-a-date"

    result = validate_claims(df)

    assert result["is_valid"] is False
    assert any("claim_date" in error for error in result["errors"])
