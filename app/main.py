import streamlit as st
from data.generator import generate_synthetic_claims

st.set_page_config(
    page_title="ClaimAudit AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 ClaimAudit AI")
st.subheader("Healthcare Claims Reimbursement Audit Agent")

tab1, tab2 = st.tabs([
    "Upload Claims",
    "Generate Demo Data"
])

with tab1:
    uploaded_file = st.file_uploader(
        "Upload Claims CSV",
        type=["csv"]
    )

    if uploaded_file:
        st.success("File uploaded successfully.")

with tab2:
    if st.button("Generate Demo Claims"):
        df = generate_synthetic_claims(500)

        st.success(f"Generated {len(df)} synthetic claims")

        st.dataframe(df.head())

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Demo Dataset",
            csv,
            "synthetic_claims.csv",
            "text/csv"
        )
