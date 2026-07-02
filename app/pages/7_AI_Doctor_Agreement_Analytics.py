from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(APP_DIR))

try:
    from components.ui_styles import apply_custom_style
except Exception:
    def apply_custom_style():
        return None


st.set_page_config(
    page_title="AI-Doctor Agreement | OrthoVision AI",
    page_icon="🤝",
    layout="wide",
)

apply_custom_style()


st.markdown(
    """
    <style>
        .ov-hero {
            padding: 28px 30px;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(8, 47, 73, 0.82));
            border: 1px solid rgba(56, 189, 248, 0.24);
            box-shadow: 0 18px 45px rgba(0,0,0,0.30);
            margin-bottom: 22px;
        }
        .ov-title {
            font-size: 34px;
            font-weight: 800;
            color: #F8FAFC;
            margin-bottom: 8px;
        }
        .ov-subtitle {
            color: #CBD5E1;
            font-size: 16px;
            line-height: 1.65;
            max-width: 1050px;
        }
        .ov-summary {
            padding: 18px 22px;
            border-radius: 18px;
            background: rgba(14, 165, 233, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #E0F2FE;
            font-size: 17px;
            font-weight: 600;
            margin-bottom: 18px;
        }
        .ov-card {
            padding: 20px 18px;
            border-radius: 20px;
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 0 12px 28px rgba(0,0,0,0.22);
            min-height: 142px;
        }
        .ov-card-title {
            color: #94A3B8;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .ov-card-value {
            color: #FFFFFF;
            font-size: 30px;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .ov-card-caption {
            color: #CBD5E1;
            font-size: 13px;
            line-height: 1.45;
        }
        .ov-section {
            padding: 22px;
            border-radius: 22px;
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.16);
            box-shadow: 0 16px 36px rgba(0,0,0,0.20);
            margin-bottom: 20px;
        }
        .ov-section h3 {
            color: #F8FAFC;
            margin-top: 0px;
        }
        .ov-help {
            color: #CBD5E1;
            font-size: 14px;
            line-height: 1.55;
            margin-top: -4px;
            margin-bottom: 12px;
        }
        .ov-insight {
            padding: 20px 22px;
            border-radius: 20px;
            background: rgba(2, 6, 23, 0.74);
            border-left: 5px solid #22C55E;
            border-top: 1px solid rgba(34, 197, 94, 0.22);
            border-right: 1px solid rgba(34, 197, 94, 0.14);
            border-bottom: 1px solid rgba(34, 197, 94, 0.14);
            color: #DCFCE7;
            line-height: 1.62;
            margin-bottom: 20px;
        }
        .ov-warning {
            border-left-color: #F59E0B;
            color: #FEF3C7;
            border-top-color: rgba(245, 158, 11, 0.22);
            border-right-color: rgba(245, 158, 11, 0.14);
            border-bottom-color: rgba(245, 158, 11, 0.14);
        }
        .ov-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            font-weight: 800;
            font-size: 12px;
        }
        .ov-badge-agree {
            color: #DCFCE7;
            background: rgba(34, 197, 94, 0.18);
            border: 1px solid rgba(34, 197, 94, 0.42);
        }
        .ov-badge-disagree {
            color: #FEE2E2;
            background: rgba(239, 68, 68, 0.18);
            border: 1px solid rgba(239, 68, 68, 0.42);
        }
        .ov-badge-review {
            color: #FEF3C7;
            background: rgba(245, 158, 11, 0.18);
            border: 1px solid rgba(245, 158, 11, 0.42);
        }
        .ov-badge-other {
            color: #E0E7FF;
            background: rgba(99, 102, 241, 0.18);
            border: 1px solid rgba(99, 102, 241, 0.42);
        }
        .ov-small {
            color: #94A3B8;
            font-size: 13px;
            line-height: 1.5;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


REQUIRED_COLUMNS = [
    "timestamp",
    "report_id",
    "patient_id",
    "body_region",
    "model_name",
    "ai_prediction",
    "confidence",
    "risk_level",
    "doctor_name",
    "doctor_specialization",
    "doctor_shift",
    "doctor_review_time",
    "doctor_feedback",
    "doctor_notes",
]


def find_feedback_file():
    """
    Priority:
    1. Real runtime feedback CSV generated by Doctor Review Mode.
    2. Demo sample CSV kept in assets for deployed showcase.
    """
    real_feedback = APP_DIR / "feedback" / "doctor_feedback.csv"
    sample_feedback = APP_DIR / "assets" / "sample_doctor_feedback.csv"

    if real_feedback.exists() and real_feedback.stat().st_size > 0:
        return real_feedback, "Live doctor feedback data"

    if sample_feedback.exists() and sample_feedback.stat().st_size > 0:
        return sample_feedback, "Demo sample feedback data"

    return None, None


def normalize_feedback(value):
    value = str(value).strip().lower()

    if value in ["agree", "agreed", "doctor agreed", "match", "matched"]:
        return "Agreed"

    if value in ["disagree", "disagreed", "doctor disagreed", "mismatch", "not matched"]:
        return "Disagreed"

    if value in ["needs review", "need review", "review", "needs expert review", "uncertain"]:
        return "Needs Review"

    return "Other"


def normalize_prediction(value):
    value = str(value).strip().lower()

    if value in ["fractured", "fracture", "positive", "yes"]:
        return "Fractured"

    if value in ["not fractured", "non fractured", "non-fractured", "normal", "negative", "no"]:
        return "Not Fractured"

    return str(value).strip().title() if str(value).strip() else "Not provided"


def confidence_to_numeric(series):
    return (
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
    )


@st.cache_data(show_spinner=False)
def load_feedback_data(file_path, modified_time):
    df = pd.read_csv(file_path)

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[REQUIRED_COLUMNS].copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["confidence"] = confidence_to_numeric(df["confidence"])

    text_cols = [
        "report_id",
        "patient_id",
        "body_region",
        "model_name",
        "ai_prediction",
        "risk_level",
        "doctor_name",
        "doctor_specialization",
        "doctor_shift",
        "doctor_review_time",
        "doctor_feedback",
        "doctor_notes",
    ]

    for col in text_cols:
        df[col] = df[col].fillna("Not provided").astype(str)

    df["agreement_bucket"] = df["doctor_feedback"].apply(normalize_feedback)
    df["ai_prediction_display"] = df["ai_prediction"].apply(normalize_prediction)

    return df


def apply_filters(df):
    with st.sidebar:
        st.markdown("### 🤝 Agreement Filters")

        view_mode = st.radio(
            "Counting Mode",
            ["Latest review per Report ID", "All feedback rows"],
            index=0,
            help="Latest review avoids double counting the same report if multiple reviews exist.",
        )

        body_regions = sorted([x for x in df["body_region"].dropna().unique() if x and x != "Not provided"])
        selected_regions = st.multiselect(
            "Body Region",
            body_regions,
            default=body_regions,
        )

        feedback_options = ["Agreed", "Disagreed", "Needs Review", "Other"]
        available_feedback = [x for x in feedback_options if x in df["agreement_bucket"].unique()]
        selected_feedback = st.multiselect(
            "Doctor Feedback",
            available_feedback,
            default=available_feedback,
        )

        prediction_options = sorted([x for x in df["ai_prediction_display"].dropna().unique() if x])
        selected_predictions = st.multiselect(
            "AI Prediction",
            prediction_options,
            default=prediction_options,
        )

        min_conf, max_conf = st.slider(
            "AI Confidence Range",
            min_value=0,
            max_value=100,
            value=(0, 100),
        )

    filtered = df.copy()

    if selected_regions:
        filtered = filtered[filtered["body_region"].isin(selected_regions)]

    if selected_feedback:
        filtered = filtered[filtered["agreement_bucket"].isin(selected_feedback)]

    if selected_predictions:
        filtered = filtered[filtered["ai_prediction_display"].isin(selected_predictions)]

    filtered = filtered[
        (filtered["confidence"] >= min_conf) &
        (filtered["confidence"] <= max_conf)
    ]

    if view_mode == "Latest review per Report ID":
        filtered = (
            filtered.sort_values("timestamp")
            .drop_duplicates(subset=["report_id"], keep="last")
            .copy()
        )

    return filtered, view_mode


def percentage(part, total):
    if total <= 0:
        return 0.0
    return round((part / total) * 100, 2)


def build_kpis(df):
    total = len(df)
    agreed = int((df["agreement_bucket"] == "Agreed").sum())
    disagreed = int((df["agreement_bucket"] == "Disagreed").sum())
    needs_review = int((df["agreement_bucket"] == "Needs Review").sum())
    agreement_rate = percentage(agreed, total)
    avg_confidence = round(df["confidence"].mean(), 2) if total else 0
    difficult_cases = disagreed + needs_review
    difficult_rate = percentage(difficult_cases, total)

    return {
        "total": total,
        "agreed": agreed,
        "disagreed": disagreed,
        "needs_review": needs_review,
        "agreement_rate": agreement_rate,
        "avg_confidence": avg_confidence,
        "difficult_cases": difficult_cases,
        "difficult_rate": difficult_rate,
    }


def metric_card(label, value, caption):
    st.markdown(
        f"""
        <div class="ov-card">
            <div class="ov-card-title">{label}</div>
            <div class="ov-card-value">{value}</div>
            <div class="ov-card-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_html(value):
    if value == "Agreed":
        cls = "ov-badge ov-badge-agree"
    elif value == "Disagreed":
        cls = "ov-badge ov-badge-disagree"
    elif value == "Needs Review":
        cls = "ov-badge ov-badge-review"
    else:
        cls = "ov-badge ov-badge-other"

    return f'<span class="{cls}">{value}</span>'


def render_empty_state():
    st.warning(
        "No doctor feedback data found. Add feedback from AI Scan Room or place "
        "`sample_doctor_feedback.csv` inside `app/assets/`."
    )


st.markdown(
    """
    <div class="ov-hero">
        <div class="ov-title">🤝 AI-Doctor Agreement Analytics</div>
        <div class="ov-subtitle">
            Human-in-the-loop analytics for OrthoVision AI. This dashboard compares AI fracture
            predictions with doctor feedback to measure agreement, disagreement, uncertain cases,
            confidence patterns, and clinically useful review trends.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

feedback_file, data_label = find_feedback_file()

if feedback_file is None:
    render_empty_state()
    st.stop()

df = load_feedback_data(str(feedback_file), feedback_file.stat().st_mtime)

if df.empty:
    render_empty_state()
    st.stop()

filtered_df, view_mode = apply_filters(df)

if filtered_df.empty:
    st.warning("No records matched the selected filters.")
    st.stop()

kpis = build_kpis(filtered_df)

summary_class = "ov-insight" if kpis["agreement_rate"] >= 70 else "ov-insight ov-warning"
st.markdown(
    f"""
    <div class="ov-summary">
        AI agreed with doctor feedback in {kpis["agreement_rate"]}% of reviewed cases.
        {kpis["difficult_cases"]} case(s) were marked as Disagreed or Needs Review for further analysis.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(f"Data source: {data_label} | File: {feedback_file.name} | Mode: {view_mode}")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    metric_card(
        "Total Reviewed Cases",
        kpis["total"],
        "Doctor feedback records analyzed after filters.",
    )

with k2:
    metric_card(
        "Doctor Agreed",
        f'{kpis["agreed"]} ({percentage(kpis["agreed"], kpis["total"])}%)',
        "AI prediction matched expert review.",
    )

with k3:
    metric_card(
        "Doctor Disagreed",
        f'{kpis["disagreed"]} ({percentage(kpis["disagreed"], kpis["total"])}%)',
        "Cases useful for model error analysis.",
    )

with k4:
    metric_card(
        "Needs Review",
        f'{kpis["needs_review"]} ({percentage(kpis["needs_review"], kpis["total"])}%)',
        "Uncertain cases needing expert confirmation.",
    )

with k5:
    metric_card(
        "Average Confidence",
        f'{kpis["avg_confidence"]}%',
        f'Agreement rate: {kpis["agreement_rate"]}%.',
    )

st.markdown("")

st.markdown(
    f"""
    <div class="{summary_class}">
        <b>Clinical Reliability Snapshot:</b>
        The agreement rate indicates how often the AI output aligns with doctor review.
        Disagreement and Needs Review cases should not be ignored; they are valuable cases for
        improving the dataset, identifying model limitations, and strengthening future validation.
    </div>
    """,
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns([1, 1])

with chart_col1:
    st.markdown('<div class="ov-section">', unsafe_allow_html=True)
    st.subheader("Agreement Distribution")
    st.markdown(
        '<div class="ov-help">Shows how doctor feedback is distributed across Agreed, Disagreed, and Needs Review cases.</div>',
        unsafe_allow_html=True,
    )

    distribution = (
        filtered_df["agreement_bucket"]
        .value_counts()
        .rename_axis("Doctor Feedback")
        .reset_index(name="Cases")
    )

    fig_distribution = px.pie(
        distribution,
        names="Doctor Feedback",
        values="Cases",
        hole=0.58,
    )
    fig_distribution.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        legend_title_text="Feedback",
    )
    st.plotly_chart(fig_distribution, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col2:
    st.markdown('<div class="ov-section">', unsafe_allow_html=True)
    st.subheader("AI Prediction vs Doctor Feedback")
    st.markdown(
        '<div class="ov-help">Compares AI prediction categories with doctor review outcomes to reveal where disagreement happens.</div>',
        unsafe_allow_html=True,
    )

    pred_feedback = (
        filtered_df.groupby(["ai_prediction_display", "agreement_bucket"])
        .size()
        .reset_index(name="Cases")
    )

    fig_pred_feedback = px.bar(
        pred_feedback,
        x="ai_prediction_display",
        y="Cases",
        color="agreement_bucket",
        barmode="group",
        labels={
            "ai_prediction_display": "AI Prediction",
            "agreement_bucket": "Doctor Feedback",
        },
    )
    fig_pred_feedback.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        legend_title_text="Feedback",
    )
    st.plotly_chart(fig_pred_feedback, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

chart_col3, chart_col4 = st.columns([1, 1])

with chart_col3:
    st.markdown('<div class="ov-section">', unsafe_allow_html=True)
    st.subheader("Average AI Confidence by Doctor Decision")
    st.markdown(
        '<div class="ov-help">Helps identify whether the model is overconfident in cases where doctors disagree or request review.</div>',
        unsafe_allow_html=True,
    )

    confidence_feedback = (
        filtered_df.groupby("agreement_bucket")["confidence"]
        .mean()
        .reset_index(name="Average Confidence")
    )

    fig_conf = px.bar(
        confidence_feedback,
        x="agreement_bucket",
        y="Average Confidence",
        text="Average Confidence",
        labels={
            "agreement_bucket": "Doctor Feedback",
            "Average Confidence": "Average AI Confidence (%)",
        },
    )
    fig_conf.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig_conf.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_range=[0, 100],
    )
    st.plotly_chart(fig_conf, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with chart_col4:
    st.markdown('<div class="ov-section">', unsafe_allow_html=True)
    st.subheader("Region-wise Reviewed Cases")
    st.markdown(
        '<div class="ov-help">Shows which body regions have the most reviewed, disagreed, or uncertain cases.</div>',
        unsafe_allow_html=True,
    )

    region_summary = (
        filtered_df.groupby(["body_region", "agreement_bucket"])
        .size()
        .reset_index(name="Cases")
    )

    fig_region = px.bar(
        region_summary,
        x="body_region",
        y="Cases",
        color="agreement_bucket",
        barmode="stack",
        labels={
            "body_region": "Body Region",
            "agreement_bucket": "Doctor Feedback",
        },
    )
    fig_region.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        legend_title_text="Feedback",
    )
    st.plotly_chart(fig_region, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="ov-section">', unsafe_allow_html=True)
st.subheader("Agreement Summary by Category")
st.markdown(
    '<div class="ov-help">Color-coded doctor feedback categories for quick demo explanation.</div>',
    unsafe_allow_html=True,
)

summary_table = (
    filtered_df.groupby("agreement_bucket")
    .agg(
        Cases=("report_id", "count"),
        Average_Confidence=("confidence", "mean"),
    )
    .reset_index()
)

summary_table["Percentage"] = summary_table["Cases"].apply(lambda x: f"{percentage(x, kpis['total'])}%")
summary_table["Average Confidence"] = summary_table["Average_Confidence"].apply(lambda x: f"{x:.2f}%")
summary_table["Doctor Feedback"] = summary_table["agreement_bucket"].apply(badge_html)

display_summary = summary_table[["Doctor Feedback", "Cases", "Percentage", "Average Confidence"]]

st.markdown(
    display_summary.to_html(escape=False, index=False),
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="ov-section">', unsafe_allow_html=True)
st.subheader("Recent Reviewed Cases")
st.markdown(
    '<div class="ov-help">Latest feedback records used for agreement analytics. These cases help demonstrate traceability and review workflow.</div>',
    unsafe_allow_html=True,
)

recent_cols = [
    "timestamp",
    "report_id",
    "patient_id",
    "body_region",
    "ai_prediction_display",
    "confidence",
    "risk_level",
    "doctor_name",
    "doctor_specialization",
    "agreement_bucket",
    "doctor_notes",
]

recent_df = filtered_df.sort_values("timestamp", ascending=False)[recent_cols].copy()
recent_df["timestamp"] = recent_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
recent_df["confidence"] = recent_df["confidence"].map(lambda x: f"{x:.2f}%")
recent_df = recent_df.rename(
    columns={
        "timestamp": "Timestamp",
        "report_id": "Report ID",
        "patient_id": "Patient / Case ID",
        "body_region": "Body Region",
        "ai_prediction_display": "AI Prediction",
        "confidence": "Confidence",
        "risk_level": "Risk Level",
        "doctor_name": "Doctor Name",
        "doctor_specialization": "Specialization",
        "agreement_bucket": "Doctor Feedback",
        "doctor_notes": "Doctor Notes",
    }
)

st.dataframe(
    recent_df,
    use_container_width=True,
    hide_index=True,
)

csv_data = recent_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Analytics CSV",
    data=csv_data,
    file_name="ai_doctor_agreement_analytics.csv",
    mime="text/csv",
)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="ov-insight">
        <b>Research Interpretation:</b>
        This dashboard converts doctor feedback into measurable validation evidence.
        A higher agreement rate supports clinical consistency, while disagreement and needs-review
        cases highlight difficult X-rays that can be used for future dataset refinement, model
        improvement, and supervisor evaluation.
    </div>
    """,
    unsafe_allow_html=True,
)
