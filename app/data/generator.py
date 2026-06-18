import pandas as pd
import numpy as np


def generate_synthetic_claims(rows: int = 500) -> pd.DataFrame:
    np.random.seed(42)

    data = pd.DataFrame({
        "claim_id": [f"CLM-{i:06d}" for i in range(1, rows + 1)],
        "patient_id": [f"PAT-{np.random.randint(1000, 9999)}" for _ in range(rows)],
        "provider_id": [f"PRV-{np.random.randint(100, 999)}" for _ in range(rows)],
        "diagnosis_code": np.random.choice(["E11", "I10", "J45", "M54", "N18"], rows),
        "procedure_code": np.random.choice(["99213", "99214", "93000", "80053", "36415"], rows),
        "claim_amount": np.random.normal(500, 150, rows).clip(50, 5000).round(2),
        "reimbursed_amount": np.random.normal(350, 120, rows).clip(20, 4500).round(2),
        "payer_type": np.random.choice(["Medicare", "Medicaid", "Commercial"], rows),
        "claim_date": pd.date_range("2024-01-01", periods=rows, freq="D")
    })

    anomaly_indices = np.random.choice(data.index, size=max(5, rows // 20), replace=False)
    data.loc[anomaly_indices, "claim_amount"] *= 4
    data.loc[anomaly_indices, "reimbursed_amount"] *= 3

    return data
