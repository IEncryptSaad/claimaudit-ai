"""Transformation utilities for healthcare claims datasets."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def transform_claims(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw healthcare claims data into an analysis-ready DataFrame.

    The transformation copies the input DataFrame, standardizes dates and
    monetary fields, derives reimbursement metrics, normalizes string values,
    and removes duplicate claim records by ``claim_id``.

    Args:
        df: Raw claims data to transform.

    Returns:
        A transformed copy of the claims DataFrame.
    """
    logger.info("Starting claims transformation for %s rows", len(df))

    transformed_df = df.copy()

    transformed_df["claim_date"] = pd.to_datetime(
        transformed_df["claim_date"], errors="coerce"
    )
    transformed_df["claim_amount"] = pd.to_numeric(
        transformed_df["claim_amount"], errors="coerce"
    )
    transformed_df["reimbursed_amount"] = pd.to_numeric(
        transformed_df["reimbursed_amount"], errors="coerce"
    )

    transformed_df["reimbursement_ratio"] = (
        transformed_df["reimbursed_amount"] / transformed_df["claim_amount"]
    )
    transformed_df["claim_month"] = transformed_df["claim_date"].dt.to_period("M")

    string_columns = transformed_df.select_dtypes(include=["object", "string"]).columns
    for column in string_columns:
        transformed_df[column] = transformed_df[column].str.strip()

    duplicate_count = int(transformed_df.duplicated(subset=["claim_id"]).sum())
    if duplicate_count > 0:
        logger.info("Removing %s duplicate claim_id record(s)", duplicate_count)
        transformed_df = transformed_df.drop_duplicates(subset=["claim_id"], keep="first")

    logger.info("Claims transformation completed with %s rows", len(transformed_df))

    return transformed_df
