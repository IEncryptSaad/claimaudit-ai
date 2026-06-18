import streamlit as st

st.set_page_config(
    page_title="ClaimAudit AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 ClaimAudit AI")

st.subheader("Healthcare Claims Reimbursement Audit Agent")

st.write(
    "Upload healthcare claims data, detect anomalies, "
    "analyze reimbursement risk, and generate audit reports."
)

uploaded_file = st.file_uploader(
    "Upload Claims CSV",
    type=["csv"]
)

if uploaded_file:
    st.success("File uploaded successfully.")
