"""Validation utilities for healthcare claims datasets."""

from __future__ import annotations

import logging
from typing import Final

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "claim_id",
    "patient_id",
    "provider_id",
    "diagnosis_code",
    "procedure_code",
    "claim_amount",
    "reimbursed_amount",
    "payer_type",
    "claim_date",
)


def validate_claims(df: pd.DataFrame) -> dict[str, bool | list[str]]:
    """Validate a healthcare claims DataFrame against required schema rules.

    The validation checks that required columns exist, required fields are not
    null, monetary amounts are within allowed ranges, and claim dates can be
    parsed by pandas as datetimes.

    Args:
        df: Claims data to validate.

    Returns:
        A dictionary with an ``is_valid`` boolean and an ``errors`` list of
        human-readable validation failures.
    """
    errors: list[str] = []

    logger.info("Starting claims validation for %s rows", len(df))

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        errors.append(
            "Missing required columns: " + ", ".join(sorted(missing_columns))
        )
        logger.warning("Claims validation found missing columns: %s", missing_columns)

    present_required_columns = [
        column for column in REQUIRED_COLUMNS if column in df.columns
    ]

    for column in present_required_columns:
        null_count = int(df[column].isna().sum())
        if null_count > 0:
            errors.append(
                f"Column '{column}' contains {null_count} null value(s)."
            )

    if "claim_amount" in df.columns:
        claim_amount = pd.to_numeric(df["claim_amount"], errors="coerce")
        invalid_claim_amount_count = int(
            (claim_amount.isna() | (claim_amount <= 0)).sum()
        )
        if invalid_claim_amount_count > 0:
            errors.append(
                "Column 'claim_amount' must contain numeric values greater than 0; "
                f"found {invalid_claim_amount_count} invalid value(s)."
            )

    if "reimbursed_amount" in df.columns:
        reimbursed_amount = pd.to_numeric(df["reimbursed_amount"], errors="coerce")
        invalid_reimbursed_amount_count = int(
            (reimbursed_amount.isna() | (reimbursed_amount < 0)).sum()
        )
        if invalid_reimbursed_amount_count > 0:
            errors.append(
                "Column 'reimbursed_amount' must contain numeric values greater "
                "than or equal to 0; "
                f"found {invalid_reimbursed_amount_count} invalid value(s)."
            )

    if "claim_date" in df.columns:
        parsed_claim_dates = pd.to_datetime(df["claim_date"], errors="coerce")
        invalid_claim_date_count = int(parsed_claim_dates.isna().sum())
        if invalid_claim_date_count > 0:
            errors.append(
                "Column 'claim_date' must contain values convertible to datetime; "
                f"found {invalid_claim_date_count} invalid value(s)."
            )

    is_valid = not errors
    if is_valid:
        logger.info("Claims validation completed successfully")
    else:
        logger.warning("Claims validation completed with %s error(s)", len(errors))

    return {"is_valid": is_valid, "errors": errors}
