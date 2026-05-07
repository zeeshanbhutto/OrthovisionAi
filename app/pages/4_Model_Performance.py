from pathlib import Path
import sys

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(APP_DIR))

from components.ui_styles import apply_custom_style


st.set_page_config(
    page_title="Model Performance | OrthoVision AI",
    page_icon="📊",
    layout="wide",
)

apply_custom_style()


# =========================
# Paths
# =========================
METRICS_CSV = PROJECT_ROOT / "outputs" / "evaluation_tables" / "model_metrics.csv"
CONFUSION_DIR = PROJECT_ROOT / "outputs" / "confusion_matrices"
TRAINING_DIR = PROJECT_ROOT / "outputs" / "training_plots"
ROC_DIR = PROJECT_ROOT / "outputs" / "roc_curves"
EVAL_DIR = PROJECT_ROOT / "outputs" / "evaluation_tables"


# =========================
# Helper functions
# =========================
def metric_card(title, value, caption):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_start():
    st.markdown('<div class="section-card">', unsafe_allow_html=True)


def section_end():
    st.markdown('</div>', unsafe_allow_html=True)


def load_metrics():
    """
    Expected CSV columns:
    Model,Accuracy,Precision,Recall,F1,Specificity,AUC,AvgConfidence

    Values should be in percentage format, for example:
    Accuracy = 95.30
    Recall = 94.20
    AvgConfidence = 91.70
    """

    if METRICS_CSV.exists():
        df = pd.read_csv(METRICS_CSV)
        using_demo_data = False
    else:
        # Temporary demo values only for UI preview.
        # Replace these with your actual model results by creating model_metrics.csv.
        df = pd.DataFrame([
            {
                "Model": "CNN",
                "Accuracy": 0.00,
                "Precision": 0.00,
                "Recall": 0.00,
                "F1": 0.00,
                "Specificity": 0.00,
                "AUC": 0.00,
                "AvgConfidence": 0.00,
            },
            {
                "Model": "ResNet18",
                "Accuracy": 0.00,
                "Precision": 0.00,
                "Recall": 0.00,
                "F1": 0.00,
                "Specificity": 0.00,
                "AUC": 0.00,
                "AvgConfidence": 0.00,
            },
        ])
        using_demo_data = True

    required_cols = [
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1",
        "Specificity",
        "AUC",
        "AvgConfidence",
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = 0.00

    numeric_cols = [
        "Accuracy",
        "Precision",
        "Recall",
        "F1",
        "Specificity",
        "AUC",
        "AvgConfidence",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.00)

    df["Uncertainty"] = 100 - df["AvgConfidence"]

    return df, using_demo_data


def get_best_model(df):
    if df.empty:
        return None

    if "F1" in df.columns:
        return df.sort_values("F1", ascending=False).iloc[0]

    return df.sort_values("Accuracy", ascending=False).iloc[0]


def find_images(folder, keywords=None):
    if not folder.exists():
        return []

    keywords = keywords or []
    allowed_ext = [".png", ".jpg", ".jpeg"]

    images = []

    for path in folder.rglob("*"):
        if path.suffix.lower() in allowed_ext:
            if not keywords:
                images.append(path)
            else:
                name = path.name.lower()
                if any(keyword in name for keyword in keywords):
                    images.append(path)

    return sorted(images)


def plot_metric_comparison(df):
    metrics = ["Accuracy", "Precision", "Recall", "F1", "Specificity", "AUC"]

    plot_df = df.melt(
        id_vars="Model",
        value_vars=metrics,
        var_name="Metric",
        value_name="Score",
    )

    if PLOTLY_AVAILABLE:
        fig = px.bar(
            plot_df,
            x="Metric",
            y="Score",
            color="Model",
            barmode="group",
            text="Score",
            title="Model Comparison Across Evaluation Metrics",
            template="plotly_dark",
        )

        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig.update_layout(
            yaxis_title="Score (%)",
            xaxis_title="Evaluation Metric",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 105]),
            legend_title="Model",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(plot_df, x="Metric", y="Score", color="Model")


def plot_clinical_risk_metrics(df):
    clinical_df = df.copy()
    clinical_df["False Negative Rate"] = 100 - clinical_df["Recall"]
    clinical_df["False Positive Rate"] = 100 - clinical_df["Specificity"]

    plot_df = clinical_df.melt(
        id_vars="Model",
        value_vars=["Recall", "Specificity", "False Negative Rate", "False Positive Rate"],
        var_name="Clinical Metric",
        value_name="Score",
    )

    if PLOTLY_AVAILABLE:
        fig = px.bar(
            plot_df,
            x="Clinical Metric",
            y="Score",
            color="Model",
            barmode="group",
            text="Score",
            title="Clinical Risk-Oriented Metrics",
            template="plotly_dark",
        )

        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig.update_layout(
            yaxis_title="Score (%)",
            xaxis_title="Metric",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 105]),
            legend_title="Model",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(plot_df, x="Clinical Metric", y="Score", color="Model")


def plot_uncertainty(df):
    plot_df = df[["Model", "AvgConfidence", "Uncertainty"]].copy()

    melted = plot_df.melt(
        id_vars="Model",
        value_vars=["AvgConfidence", "Uncertainty"],
        var_name="Measure",
        value_name="Score",
    )

    if PLOTLY_AVAILABLE:
        fig = px.bar(
            melted,
            x="Model",
            y="Score",
            color="Measure",
            barmode="group",
            text="Score",
            title="Confidence and Uncertainty Analysis",
            template="plotly_dark",
        )

        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig.update_layout(
            yaxis_title="Percentage (%)",
            xaxis_title="Model",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 105]),
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(melted, x="Model", y="Score", color="Measure")


# =========================
# Header
# =========================
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">📊 Model Performance Dashboard</div>
        <div class="hero-subtitle">
            Research-focused evaluation of fracture classification models using accuracy, precision, recall,
            F1-score, specificity, AUC, uncertainty analysis, confusion matrices, and training curves.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================
# Load metrics
# =========================
metrics_df, using_demo_data = load_metrics()

if using_demo_data:
    st.warning(
        "model_metrics.csv not found. Dashboard layout is ready, but metrics are currently zero. "
        "Add your actual CNN and ResNet18 results in outputs/evaluation_tables/model_metrics.csv."
    )

best_model = get_best_model(metrics_df)


# =========================
# KPI Cards
# =========================
if best_model is not None:
    st.markdown("## 🧠 Best Model Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Best Model",
            str(best_model["Model"]),
            "Selected based on F1-score",
        )

    with c2:
        metric_card(
            "Accuracy",
            f"{best_model['Accuracy']:.2f}%",
            "Overall correct predictions",
        )

    with c3:
        metric_card(
            "Recall / Sensitivity",
            f"{best_model['Recall']:.2f}%",
            "Important for detecting actual fractures",
        )

    with c4:
        metric_card(
            "F1-Score",
            f"{best_model['F1']:.2f}%",
            "Balance of precision and recall",
        )

    c5, c6, c7, c8 = st.columns(4)

    with c5:
        metric_card(
            "Precision",
            f"{best_model['Precision']:.2f}%",
            "Correctness of fracture predictions",
        )

    with c6:
        metric_card(
            "Specificity",
            f"{best_model['Specificity']:.2f}%",
            "Correct non-fracture detection",
        )

    with c7:
        metric_card(
            "AUC",
            f"{best_model['AUC']:.2f}%",
            "Class separation ability",
        )

    with c8:
        metric_card(
            "Uncertainty",
            f"{best_model['Uncertainty']:.2f}%",
            "Lower is better",
        )


# =========================
# Metrics Table + Explanation
# =========================
st.markdown("## 📋 Evaluation Metrics Table")

section_start()

st.dataframe(
    metrics_df[
        [
            "Model",
            "Accuracy",
            "Precision",
            "Recall",
            "F1",
            "Specificity",
            "AUC",
            "AvgConfidence",
            "Uncertainty",
        ]
    ],
    use_container_width=True,
)

st.info(
    "For medical imaging tasks, recall/sensitivity is very important because a false negative means "
    "the model missed an actual fracture. F1-score is useful when the dataset has class imbalance."
)

section_end()


# =========================
# Metric Comparison Graph
# =========================
st.markdown("## 📈 Model Comparison Graph")

section_start()

plot_metric_comparison(metrics_df)

st.markdown(
    """
    **Interpretation:**  
    This graph compares CNN and ResNet18 across major evaluation metrics. A stronger model should have
    high accuracy, precision, recall, F1-score, specificity, and AUC. In fracture detection, recall is
    especially important because missing a fracture can be clinically risky.
    """
)

section_end()


# =========================
# Clinical Risk Metrics
# =========================
st.markdown("## 🏥 Clinical Risk Analysis")

section_start()

plot_clinical_risk_metrics(metrics_df)

st.markdown(
    """
    **Research Note:**  
    False Negative Rate is critical in fracture detection. A false negative means the model predicted
    "not fractured" when the X-ray was actually fractured. This type of error is more dangerous than
    a false positive in medical screening.
    """
)

section_end()


# =========================
# Uncertainty Analysis
# =========================
st.markdown("## 🔎 Confidence and Uncertainty Analysis")

section_start()

plot_uncertainty(metrics_df)

st.markdown(
    """
    **Uncertainty Meaning:**  
    Uncertainty is calculated as `100 - Average Confidence`. Higher uncertainty means the model is less
    confident and the case should be reviewed carefully by a medical expert.
    """
)

section_end()


# =========================
# Confusion Matrices
# =========================
st.markdown("## 🧩 Confusion Matrices")

section_start()

confusion_images = find_images(
    CONFUSION_DIR,
    keywords=["confusion", "matrix", "cm"],
)

if confusion_images:
    cols = st.columns(2)

    for index, image_path in enumerate(confusion_images):
        with cols[index % 2]:
            st.image(
                str(image_path),
                caption=image_path.name,
                use_container_width=True,
            )
else:
    st.warning(
        "No confusion matrix image found. Save your confusion matrix PNG files inside "
        "outputs/confusion_matrices/ with names like cnn_confusion_matrix.png or resnet18_confusion_matrix.png."
    )

st.markdown(
    """
    **Interpretation:**  
    The confusion matrix shows how many fractured and non-fractured images were correctly or incorrectly
    classified. It helps identify false positives and false negatives.
    """
)

section_end()


# =========================
# Training Curves
# =========================
st.markdown("## 📉 Training and Validation Curves")

section_start()

training_images = find_images(
    TRAINING_DIR,
    keywords=["accuracy", "loss", "train", "validation", "epoch"],
)

if training_images:
    cols = st.columns(2)

    for index, image_path in enumerate(training_images):
        with cols[index % 2]:
            st.image(
                str(image_path),
                caption=image_path.name,
                use_container_width=True,
            )
else:
    st.warning(
        "No training curve images found. Save accuracy/loss graphs inside outputs/training_plots/."
    )

st.markdown(
    """
    **Interpretation:**  
    Training and validation curves help identify whether the model is learning properly.
    If training accuracy is high but validation accuracy is low, the model may be overfitting.
    """
)

section_end()


# =========================
# ROC / AUC Curves
# =========================
st.markdown("## 📍 ROC / AUC Curves")

section_start()

roc_images = find_images(
    ROC_DIR,
    keywords=["roc", "auc", "curve"],
)

if roc_images:
    cols = st.columns(2)

    for index, image_path in enumerate(roc_images):
        with cols[index % 2]:
            st.image(
                str(image_path),
                caption=image_path.name,
                use_container_width=True,
            )
else:
    st.warning(
        "No ROC/AUC curve image found. Save ROC curve PNG files inside outputs/roc_curves/."
    )

st.markdown(
    """
    **Interpretation:**  
    ROC-AUC measures how well the model separates fractured and non-fractured cases across different
    decision thresholds. A higher AUC indicates better discrimination capability.
    """
)

section_end()


# =========================
# Research Summary
# =========================
st.markdown("## 📝 Research-Focused Summary")

section_start()

st.markdown(
    """
    This dashboard summarizes the experimental evaluation of the fracture classification models.
    The evaluation includes general machine learning metrics such as accuracy, precision, recall,
    F1-score, and AUC, along with medical screening-focused analysis such as specificity,
    false negative rate, and uncertainty.

    In this project, **recall/sensitivity** is treated as one of the most important metrics because
    missing an actual fracture may lead to delayed treatment. Grad-CAM explainability is used in the
    AI Scan Room and Explainability Viewer to visually analyze which regions influenced the model's
    decision.
    """
)

section_end()