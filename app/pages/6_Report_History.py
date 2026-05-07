from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(APP_DIR))

from components.ui_styles import apply_custom_style


st.set_page_config(
    page_title="Report History | OrthoVision AI",
    page_icon="📄",
    layout="wide",
)

apply_custom_style()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">📄 Report History</div>
        <div class="hero-subtitle">
            View and download previously generated AI-assisted PDF reports.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

reports_dir = APP_DIR / "generated_reports"
reports_dir.mkdir(parents=True, exist_ok=True)

pdf_files = sorted(
    reports_dir.glob("*.pdf"),
    key=lambda x: x.stat().st_mtime,
    reverse=True,
)

if not pdf_files:
    st.info("No PDF reports generated yet. Generate a report from the AI Scan Room.")
else:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.subheader("Generated Reports")

    for pdf_path in pdf_files:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"📄 **{pdf_path.name}**")

        with col2:
            with open(pdf_path, "rb") as file:
                st.download_button(
                    label="Download",
                    data=file,
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    key=pdf_path.name,
                )

    st.markdown('</div>', unsafe_allow_html=True)