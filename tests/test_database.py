"""Tests for SQLite claim persistence."""

import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.database import CLAIMS_TABLE, save_claims


def test_save_claims_stores_is_anomaly_as_integer_or_null(tmp_path: Path) -> None:
    """Pandas and NumPy anomaly flags should be saved as SQLite integers."""
    database_path = tmp_path / "claims.db"
    df = pd.DataFrame(
        {
            "claim_id": ["CLM-001", "CLM-002", "CLM-003"],
            "is_anomaly": pd.Series([np.bool_(True), np.int64(0), pd.NA], dtype="object"),
        }
    )

    assert save_claims(df, database_path=database_path) == 3

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            f"""
            SELECT claim_id, is_anomaly, typeof(is_anomaly)
            FROM {CLAIMS_TABLE}
            ORDER BY claim_id
            """
        ).fetchall()

    assert rows == [
        ("CLM-001", 1, "integer"),
        ("CLM-002", 0, "integer"),
        ("CLM-003", None, "null"),
    ]
