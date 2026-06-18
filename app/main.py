import pandas as pd
import streamlit as st

from data.generator import generate_synthetic_claims
from etl.transform import transform_claims
from etl.validate import validate_claims
from ml.anomaly import score_claim_anomalies

st.set_page_config(
    page_title="ClaimAudit AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 ClaimAudit AI")
st.subheader("Healthcare Claims Reimbursement Audit Agent")


def run_claims_pipeline(df: pd.DataFrame) -> tuple[pd.DataFrame | None, list[str]]:
    """Validate, transform, and score a claims DataFrame."""
    validation_result = validate_claims(df)
    errors = validation_result.get("errors", [])

    if not validation_result.get("is_valid", False):
        return None, list(errors)

    transformed_df = transform_claims(df)
    scored_df = score_claim_anomalies(transformed_df)

    return scored_df, []


def show_validation_errors(errors: list[str]) -> None:
    """Render validation errors in a readable format."""
    st.error("Validation failed. Please fix the issues below and try again.")
    for error in errors:
        st.warning(error)


def show_scored_claims(scored_df: pd.DataFrame) -> None:
    """Render scored claims summary metrics and table."""
    risk_counts = scored_df["risk_label"].value_counts()

    total_claims = len(scored_df)
    high_risk_claims = int(risk_counts.get("High", 0))
    medium_risk_claims = int(risk_counts.get("Medium", 0))
    low_risk_claims = int(risk_counts.get("Low", 0))

    st.success("Claims validated, transformed, and scored successfully.")

    metric_columns = st.columns(4)
    metric_columns[0].metric("Total Claims", total_claims)
    metric_columns[1].metric("High Risk", high_risk_claims)
    metric_columns[2].metric("Medium Risk", medium_risk_claims)
    metric_columns[3].metric("Low Risk", low_risk_claims)

    st.markdown("### Scored Claims")
    st.dataframe(scored_df, use_container_width=True)


def process_and_render_claims(df: pd.DataFrame) -> pd.DataFrame | None:
    """Run the claims pipeline and render results or errors."""
    try:
        scored_df, validation_errors = run_claims_pipeline(df)
    except Exception as exc:  # noqa: BLE001
        st.error("An unexpected error occurred while processing claims.")
        st.exception(exc)
        return None

    if validation_errors:
        show_validation_errors(validation_errors)
        return None

    if scored_df is None:
        st.error("Claims could not be scored.")
        return None

    show_scored_claims(scored_df)
    return scored_df


tab1, tab2 = st.tabs([
    "Upload Claims",
    "Generate Demo Data"
])

with tab1:
    st.markdown(
        "Upload a claims CSV to validate, transform, and score it for "
        "reimbursement risk."
    )

    uploaded_file = st.file_uploader(
        "Upload Claims CSV",
        type=["csv"]
    )

    if uploaded_file:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
        except Exception as exc:  # noqa: BLE001
            st.error("Unable to read the uploaded CSV file.")
            st.exception(exc)
        else:
            st.success(
                f"Loaded {len(uploaded_df)} claim row(s) from the uploaded file."
            )
            process_and_render_claims(uploaded_df)

with tab2:
    st.markdown(
        "Generate synthetic claims and run them through the same audit pipeline."
    )

    if st.button("Generate Demo Claims"):
        try:
            df = generate_synthetic_claims(500)
        except Exception as exc:  # noqa: BLE001
            st.error("Unable to generate demo claims.")
            st.exception(exc)
        else:
            st.success(f"Generated {len(df)} synthetic claims.")
            scored_demo_df = process_and_render_claims(df)

            download_df = scored_demo_df if scored_demo_df is not None else df
            csv = download_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download Demo Dataset",
                csv,
                "synthetic_claims.csv",
                "text/csv"
            )
