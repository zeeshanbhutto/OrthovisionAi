import streamlit as st


def apply_custom_style():
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top left, #12263f 0%, #07111f 45%, #030712 100%);
            color: #F8FAFC;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1250px;
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(19, 55, 92, 0.95), rgba(6, 17, 31, 0.98));
            border: 1px solid rgba(148, 163, 184, 0.25);
            padding: 35px;
            border-radius: 26px;
            margin-bottom: 25px;
            box-shadow: 0px 18px 45px rgba(0,0,0,0.35);
        }

        .hero-title {
            font-size: 46px;
            font-weight: 900;
            color: #F8FAFC;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            font-size: 18px;
            color: #CBD5E1;
            max-width: 900px;
        }

        .metric-card {
            background: rgba(15, 23, 42, 0.92);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 22px;
            padding: 22px;
            min-height: 140px;
            box-shadow: 0px 12px 35px rgba(0,0,0,0.25);
        }

        .metric-title {
            color: #94A3B8;
            font-size: 13px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .metric-value {
            color: #38BDF8;
            font-size: 25px;
            font-weight: 900;
            margin-top: 8px;
        }

        .metric-caption {
            color: #CBD5E1;
            font-size: 13px;
            margin-top: 8px;
        }

        .section-card {
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 24px;
            padding: 25px;
            box-shadow: 0px 12px 35px rgba(0,0,0,0.25);
            margin-bottom: 18px;
        }

        .result-fractured {
            background: linear-gradient(135deg, #7F1D1D, #DC2626);
            color: white;
            border-radius: 22px;
            padding: 22px;
            font-size: 28px;
            font-weight: 900;
            text-align: center;
            box-shadow: 0px 12px 30px rgba(220,38,38,0.35);
            margin-bottom: 14px;
        }

        .result-normal {
            background: linear-gradient(135deg, #064E3B, #10B981);
            color: white;
            border-radius: 22px;
            padding: 22px;
            font-size: 28px;
            font-weight: 900;
            text-align: center;
            box-shadow: 0px 12px 30px rgba(16,185,129,0.35);
            margin-bottom: 14px;
        }

        .risk-high {
            background: #DC2626;
            color: white;
            padding: 9px 18px;
            border-radius: 999px;
            font-weight: 800;
            display: inline-block;
        }

        .risk-medium {
            background: #F59E0B;
            color: white;
            padding: 9px 18px;
            border-radius: 999px;
            font-weight: 800;
            display: inline-block;
        }

        .risk-low {
            background: #10B981;
            color: white;
            padding: 9px 18px;
            border-radius: 999px;
            font-weight: 800;
            display: inline-block;
        }

        h1, h2, h3 {
            color: #F8FAFC !important;
        }

        p, li, label {
            color: #CBD5E1 !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #0284C7, #06B6D4);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0.7rem 1.3rem;
            font-weight: 800;
        }

        .stDownloadButton > button {
            background: linear-gradient(135deg, #059669, #10B981);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0.7rem 1.3rem;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )