"""Streamlit dashboard components for scored claims analytics."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

RISK_ORDER: list[str] = ["High", "Medium", "Low"]
RISK_COLORS: dict[str, str] = {
    "High": "#dc2626",
    "Medium": "#f59e0b",
    "Low": "#16a34a",
}


def _currency(value: float) -> str:
    """Format a numeric value as whole-dollar currency."""
    return f"${value:,.0f}"


def _risk_counts(scored_df: pd.DataFrame) -> pd.Series:
    """Return risk counts with all expected labels represented."""
    return scored_df["risk_label"].value_counts().reindex(RISK_ORDER, fill_value=0)


def render_kpi_cards(scored_df: pd.DataFrame) -> None:
    """Render top-level KPI cards for the scored claims dataset."""
    risk_counts = _risk_counts(scored_df)
    total_claim_amount = pd.to_numeric(
        scored_df["claim_amount"], errors="coerce"
    ).fillna(0).sum()
    total_reimbursed_amount = pd.to_numeric(
        scored_df["reimbursed_amount"], errors="coerce"
    ).fillna(0).sum()

    st.markdown("### Executive KPI Summary")
    first_row = st.columns(4)
    first_row[0].metric("Total Claims", f"{len(scored_df):,}")
    first_row[1].metric("High-Risk Claims", f"{int(risk_counts['High']):,}")
    first_row[2].metric("Medium-Risk Claims", f"{int(risk_counts['Medium']):,}")
    first_row[3].metric("Low-Risk Claims", f"{int(risk_counts['Low']):,}")

    second_row = st.columns(2)
    second_row[0].metric("Total Claim Amount", _currency(float(total_claim_amount)))
    second_row[1].metric(
        "Total Reimbursed Amount", _currency(float(total_reimbursed_amount))
    )


def render_risk_distribution(scored_df: pd.DataFrame) -> None:
    """Render a bar chart showing claim count by risk label."""
    chart_df = _risk_counts(scored_df).rename_axis("risk_label").reset_index(name="count")
    fig = px.bar(
        chart_df,
        x="risk_label",
        y="count",
        color="risk_label",
        color_discrete_map=RISK_COLORS,
        category_orders={"risk_label": RISK_ORDER},
        labels={"risk_label": "Risk Label", "count": "Claim Count"},
        title="Risk Label Distribution",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_claim_amount_by_risk(scored_df: pd.DataFrame) -> None:
    """Render total claim amount grouped by risk label."""
    chart_df = (
        scored_df.assign(
            claim_amount=pd.to_numeric(scored_df["claim_amount"], errors="coerce")
        )
        .groupby("risk_label", as_index=False)["claim_amount"]
        .sum()
    )
    fig = px.bar(
        chart_df,
        x="risk_label",
        y="claim_amount",
        color="risk_label",
        color_discrete_map=RISK_COLORS,
        category_orders={"risk_label": RISK_ORDER},
        labels={"risk_label": "Risk Label", "claim_amount": "Total Claim Amount"},
        title="Claim Amount by Risk Label",
    )
    fig.update_layout(showlegend=False, yaxis_tickprefix="$", yaxis_tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)


def render_top_high_risk_providers(scored_df: pd.DataFrame) -> None:
    """Render top providers ranked by high-risk claim volume."""
    high_risk_df = scored_df[scored_df["risk_label"] == "High"]
    if high_risk_df.empty:
        st.info("No high-risk claims were found for provider ranking.")
        return

    chart_df = (
        high_risk_df.groupby("provider_id", as_index=False)
        .size()
        .rename(columns={"size": "high_risk_claims"})
        .sort_values("high_risk_claims", ascending=False)
        .head(10)
    )
    fig = px.bar(
        chart_df,
        x="high_risk_claims",
        y="provider_id",
        orientation="h",
        labels={
            "provider_id": "Provider",
            "high_risk_claims": "High-Risk Claim Count",
        },
        title="Top 10 Providers by High-Risk Claim Count",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


def render_reimbursement_ratio_distribution(scored_df: pd.DataFrame) -> None:
    """Render reimbursement ratio histogram colored by risk label."""
    chart_df = scored_df.assign(
        reimbursement_ratio=pd.to_numeric(
            scored_df["reimbursement_ratio"], errors="coerce"
        )
    ).dropna(subset=["reimbursement_ratio"])
    if chart_df.empty:
        st.info("No valid reimbursement ratios are available to chart.")
        return

    fig = px.histogram(
        chart_df,
        x="reimbursement_ratio",
        color="risk_label",
        color_discrete_map=RISK_COLORS,
        category_orders={"risk_label": RISK_ORDER},
        nbins=30,
        labels={"reimbursement_ratio": "Reimbursement Ratio", "risk_label": "Risk"},
        title="Reimbursement Ratio Distribution",
    )
    fig.update_layout(barmode="overlay")
    fig.update_traces(opacity=0.75)
    st.plotly_chart(fig, use_container_width=True)


def render_analytics_charts(scored_df: pd.DataFrame) -> None:
    """Render all analytics charts for scored claims."""
    st.markdown("### Risk & Reimbursement Analytics")
    left_column, right_column = st.columns(2)
    with left_column:
        render_risk_distribution(scored_df)
        render_top_high_risk_providers(scored_df)
    with right_column:
        render_claim_amount_by_risk(scored_df)
        render_reimbursement_ratio_distribution(scored_df)


def render_scored_claims_download(scored_df: pd.DataFrame) -> None:
    """Render a CSV download button for the scored claims report."""
    csv = scored_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Scored Claims CSV Report",
        csv,
        "scored_claims_report.csv",
        "text/csv",
        help="Download the validated, transformed, and risk-scored claims dataset.",
    )
