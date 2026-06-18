"""SQLite persistence helpers for ClaimAudit AI claims data."""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Hashable
from pathlib import Path
from typing import Final

import pandas as pd

logger = logging.getLogger(__name__)

DATABASE_PATH: Final[Path] = Path(__file__).resolve().parents[2] / "data" / "claimaudit.db"
CLAIMS_TABLE: Final[str] = "claims"

CLAIMS_SCHEMA: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {CLAIMS_TABLE} (
    claim_id TEXT PRIMARY KEY,
    patient_id TEXT,
    provider_id TEXT,
    diagnosis_code TEXT,
    procedure_code TEXT,
    claim_amount REAL,
    reimbursed_amount REAL,
    payer_type TEXT,
    claim_date TEXT,
    reimbursement_ratio REAL,
    anomaly_score REAL,
    is_anomaly INTEGER,
    risk_label TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def _connect(database_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Create a SQLite connection, ensuring the parent directory exists."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(database_path)


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    """Initialize the ClaimAudit AI SQLite database schema.

    Args:
        database_path: SQLite database file path. Defaults to the repository-level
            ``data/claimaudit.db`` file.

    Raises:
        sqlite3.Error: If the schema cannot be created.
    """
    try:
        with _connect(database_path) as connection:
            connection.execute(CLAIMS_SCHEMA)
            connection.commit()
        logger.info("Initialized ClaimAudit database at %s", database_path)
    except sqlite3.Error:
        logger.exception("Failed to initialize ClaimAudit database at %s", database_path)
        raise


def _normalize_is_anomaly(value: Hashable) -> int | None:
    """Convert anomaly flags to SQLite-safe Python integer values."""
    if pd.isna(value):
        return None
    return int(value)


def save_claims(df: pd.DataFrame, database_path: Path = DATABASE_PATH) -> int:
    """Persist claims to SQLite using ``claim_id`` as the upsert key.

    The helper accepts raw, transformed, or scored claims DataFrames. Missing
    optional columns are stored as ``NULL`` so callers can save incremental
    pipeline outputs without requiring anomaly scores.

    Args:
        df: Claims DataFrame to save.
        database_path: SQLite database file path.

    Returns:
        Number of claim rows saved.

    Raises:
        ValueError: If the DataFrame does not include ``claim_id``.
        sqlite3.Error: If SQLite persistence fails.
    """
    if "claim_id" not in df.columns:
        raise ValueError("Cannot save claims without a 'claim_id' column.")

    initialize_database(database_path)

    columns = [
        "claim_id",
        "patient_id",
        "provider_id",
        "diagnosis_code",
        "procedure_code",
        "claim_amount",
        "reimbursed_amount",
        "payer_type",
        "claim_date",
        "reimbursement_ratio",
        "anomaly_score",
        "is_anomaly",
        "risk_label",
    ]
    claims_df = df.copy()
    for column in columns:
        if column not in claims_df.columns:
            claims_df[column] = None

    claims_df = claims_df[columns]
    if "claim_date" in claims_df:
        claims_df["claim_date"] = claims_df["claim_date"].astype(str)
    if "is_anomaly" in claims_df:
        claims_df["is_anomaly"] = claims_df["is_anomaly"].map(_normalize_is_anomaly)

    placeholders = ", ".join("?" for _ in columns)
    update_assignments = ", ".join(
        f"{column}=excluded.{column}" for column in columns if column != "claim_id"
    )
    upsert_sql = f"""
        INSERT INTO {CLAIMS_TABLE} ({", ".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT(claim_id) DO UPDATE SET
            {update_assignments},
            updated_at=CURRENT_TIMESTAMP;
    """

    records = [tuple(None if pd.isna(value) else value for value in row) for row in claims_df.itertuples(index=False, name=None)]

    try:
        with _connect(database_path) as connection:
            connection.executemany(upsert_sql, records)
            connection.commit()
        logger.info("Saved %s claim row(s) to %s", len(records), database_path)
    except sqlite3.Error:
        logger.exception("Failed to save claims to %s", database_path)
        raise

    return len(records)
