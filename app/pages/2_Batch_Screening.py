from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from PIL import Image

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(APP_DIR))

from components.ui_styles import apply_custom_style
from src.predict import FracturePredictor


st.set_page_config(
    page_title="Batch Screening | OrthoVision AI",
    page_icon="📂",
    layout="wide",
)

apply_custom_style()


@st.cache_resource
def load_predictor():
    return FracturePredictor()


predictor = load_predictor()

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">📂 Batch X-ray Screening</div>
        <div class="hero-subtitle">
            Upload multiple X-ray images and generate AI predictions in one table.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Upload multiple X-ray images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if uploaded_files:
    if st.button("Run Batch Screening"):
        rows = []

        progress = st.progress(0)

        for index, uploaded_file in enumerate(uploaded_files):
            image = Image.open(uploaded_file).convert("RGB")
            result = predictor.predict(image, generate_gradcam=False)

            rows.append({
                "Image Name": uploaded_file.name,
                "Prediction": result["prediction"],
                "Confidence (%)": round(result["confidence"], 2),
                "Risk Level": result["risk_level"],
            })

            progress.progress((index + 1) / len(uploaded_files))

        df = pd.DataFrame(rows)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Batch Screening Results")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Batch Results CSV",
            data=csv_data,
            file_name="orthovision_batch_results.csv",
            mime="text/csv",
        )
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Upload multiple X-ray images to start batch screening.")