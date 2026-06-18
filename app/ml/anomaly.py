"""Anomaly detection utilities for healthcare claims datasets."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

NUMERIC_FEATURES: list[str] = [
    "claim_amount",
    "reimbursed_amount",
    "reimbursement_ratio",
]


def _prepare_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return numeric anomaly-detection features with safe missing-value fills.

    Feature values are coerced to numeric, infinite values are treated as
    missing, and missing values are filled with each column's median. Columns
    that are entirely missing are filled with ``0.0``.

    Args:
        df: Claims DataFrame containing the required numeric feature columns.

    Returns:
        A numeric feature DataFrame suitable for IsolationForest.
    """
    missing_features = [feature for feature in NUMERIC_FEATURES if feature not in df]
    if missing_features:
        raise ValueError(
            "Missing required anomaly feature column(s): "
            + ", ".join(missing_features)
        )

    features = df[NUMERIC_FEATURES].apply(pd.to_numeric, errors="coerce")
    features = features.replace([np.inf, -np.inf], np.nan)

    medians = features.median(numeric_only=True).fillna(0.0)
    return features.fillna(medians).fillna(0.0)


def score_claim_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Score healthcare claims for anomalous reimbursement patterns.

    The model uses ``claim_amount``, ``reimbursed_amount``, and
    ``reimbursement_ratio`` as numeric features for an IsolationForest. The
    returned DataFrame includes an anomaly score, a boolean anomaly flag, and a
    simple risk label where model anomalies are ``High``, non-anomalous claims
    with reimbursement ratios above ``0.9`` are ``Medium``, and all remaining
    claims are ``Low``.

    Args:
        df: Claims data to score. The DataFrame must contain the required
            numeric feature columns.

    Returns:
        A scored copy of the input DataFrame with ``anomaly_score``,
        ``is_anomaly``, and ``risk_label`` columns.
    """
    logger.info("Starting anomaly scoring for %s rows", len(df))

    scored_df = df.copy()
    features = _prepare_numeric_features(scored_df)

    if scored_df.empty:
        logger.info("No claims to score; returning empty scored DataFrame")
        scored_df["anomaly_score"] = pd.Series(dtype="float64")
        scored_df["is_anomaly"] = pd.Series(dtype="bool")
        scored_df["risk_label"] = pd.Series(dtype="object")
        return scored_df

    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(features)

    predictions = model.predict(features)
    scored_df["anomaly_score"] = -model.decision_function(features)
    scored_df["is_anomaly"] = predictions == -1

    reimbursement_ratio = pd.to_numeric(
        scored_df["reimbursement_ratio"], errors="coerce"
    ).replace([np.inf, -np.inf], np.nan)
    scored_df["risk_label"] = np.select(
        [scored_df["is_anomaly"], reimbursement_ratio > 0.9],
        ["High", "Medium"],
        default="Low",
    )

    anomaly_count = int(scored_df["is_anomaly"].sum())
    logger.info(
        "Anomaly scoring completed for %s rows with %s anomaly/anomalies",
        len(scored_df),
        anomaly_count,
    )

    return scored_df
