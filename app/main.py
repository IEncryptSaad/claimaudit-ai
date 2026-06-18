import pandas as pd
import streamlit as st

from ui.dashboard import (
    render_analytics_charts,
    render_kpi_cards,
    render_scored_claims_download,
)

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
    """Render the scored claims analytics dashboard."""
    st.success("Claims validated, transformed, and scored successfully.")

    try:
        render_kpi_cards(scored_df)
        render_analytics_charts(scored_df)

        st.markdown("### Scored Claims Report")
        render_scored_claims_download(scored_df)
        st.dataframe(scored_df, use_container_width=True)
    except Exception as exc:  # noqa: BLE001
        st.error("Unable to render the analytics dashboard for these claims.")
        st.exception(exc)


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
            process_and_render_claims(df)
