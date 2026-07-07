from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from model import get_resnet_model
from dataset import test_loader


# -----------------------------
# Project paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_PATH = PROJECT_ROOT / "resnet_fracture.pth"

CONFUSION_MATRIX_PATH = PROJECT_ROOT / "confusion_matrix.png"
ROC_CURVE_PATH = PROJECT_ROOT / "roc_curve_ud_resnet18.png"
ROOT_METRICS_PATH = PROJECT_ROOT / "model_metrics.csv"
OUTPUT_METRICS_PATH = OUTPUT_DIR / "resnet18_model_metrics.csv"


# -----------------------------
# Class convention
# -----------------------------
# ImageFolder sorts classes alphabetically.
# Current OrthoVision convention:
# class index 0 = fractured
# class index 1 = not fractured
CLASS_NAMES = ["fractured", "not fractured"]
FRACTURED_CLASS_INDEX = 0
NOT_FRACTURED_CLASS_INDEX = 1


# -----------------------------
# Device
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


# -----------------------------
# Load model
# -----------------------------
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

# pretrained=False avoids unnecessary ImageNet download during evaluation.
# Our trained checkpoint is loaded below.
model = get_resnet_model(
    num_classes=2,
    pretrained=False,
    freeze_backbone=False
)

state_dict = torch.load(MODEL_PATH, map_location=device)

if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
    state_dict = state_dict["model_state_dict"]

model.load_state_dict(state_dict)
model.to(device)
model.eval()


# -----------------------------
# Collect predictions
# -----------------------------
all_labels = []
all_preds = []
all_probs = []
all_confidences = []

with torch.no_grad():
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)
        probabilities = torch.softmax(outputs, dim=1)
        confidences, preds = torch.max(probabilities, dim=1)

        all_labels.extend(labels.cpu().numpy())
        all_preds.extend(preds.cpu().numpy())
        all_probs.extend(probabilities.cpu().numpy())
        all_confidences.extend(confidences.cpu().numpy())


all_labels = np.array(all_labels)
all_preds = np.array(all_preds)
all_probs = np.array(all_probs)
all_confidences = np.array(all_confidences)


# -----------------------------
# Classification report
# -----------------------------
print("\nClassification Report:\n")
print(
    classification_report(
        all_labels,
        all_preds,
        labels=[FRACTURED_CLASS_INDEX, NOT_FRACTURED_CLASS_INDEX],
        target_names=CLASS_NAMES,
        zero_division=0,
    )
)


# -----------------------------
# Confusion matrix
# -----------------------------
# Matrix order:
# row 0 = actual fractured
# row 1 = actual not fractured
# col 0 = predicted fractured
# col 1 = predicted not fractured
cm = confusion_matrix(
    all_labels,
    all_preds,
    labels=[FRACTURED_CLASS_INDEX, NOT_FRACTURED_CLASS_INDEX]
)

tp = int(cm[0, 0])
fn = int(cm[0, 1])
fp = int(cm[1, 0])
tn = int(cm[1, 1])

accuracy = accuracy_score(all_labels, all_preds)

# Positive class is fractured, because missing a fracture is clinically important.
precision_fractured = precision_score(
    all_labels,
    all_preds,
    pos_label=FRACTURED_CLASS_INDEX,
    zero_division=0,
)

recall_fractured = recall_score(
    all_labels,
    all_preds,
    pos_label=FRACTURED_CLASS_INDEX,
    zero_division=0,
)

f1_fractured = f1_score(
    all_labels,
    all_preds,
    pos_label=FRACTURED_CLASS_INDEX,
    zero_division=0,
)

specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
false_negative_rate = fn / (tp + fn) if (tp + fn) > 0 else 0
average_confidence = float(np.mean(all_confidences)) if len(all_confidences) else 0


# -----------------------------
# ROC-AUC for fracture class
# -----------------------------
# Since fractured class index is 0, probability column 0 is used as positive score.
try:
    y_true_fractured = (all_labels == FRACTURED_CLASS_INDEX).astype(int)
    y_score_fractured = all_probs[:, FRACTURED_CLASS_INDEX]

    roc_auc = roc_auc_score(y_true_fractured, y_score_fractured)
    fpr, tpr, thresholds = roc_curve(y_true_fractured, y_score_fractured)

except ValueError:
    roc_auc = np.nan
    fpr, tpr, thresholds = None, None, None


# -----------------------------
# Save confusion matrix image
# -----------------------------
plt.figure(figsize=(6, 5))
plt.imshow(cm, interpolation="nearest")
plt.title("Confusion Matrix - ResNet18")
plt.colorbar()

tick_marks = np.arange(len(CLASS_NAMES))
plt.xticks(tick_marks, CLASS_NAMES, rotation=25)
plt.yticks(tick_marks, CLASS_NAMES)

threshold = cm.max() / 2 if cm.max() > 0 else 0

for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(
            j,
            i,
            format(cm[i, j], "d"),
            horizontalalignment="center",
            color="white" if cm[i, j] > threshold else "black",
            fontsize=12,
            fontweight="bold",
        )

plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.tight_layout()
plt.savefig(CONFUSION_MATRIX_PATH, dpi=300)
plt.close()


# -----------------------------
# Save ROC curve image
# -----------------------------
if fpr is not None and tpr is not None:
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, label=f"ResNet18 AUC = {roc_auc:.4f}")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Random Classifier")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - Fracture Detection")
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(ROC_CURVE_PATH, dpi=300)
    plt.close()


# -----------------------------
# Save metrics CSV
# -----------------------------
metrics_row = {
    "Model": "ResNet18",
    "Accuracy": round(accuracy * 100, 2),
    "Precision": round(precision_fractured * 100, 2),
    "Recall": round(recall_fractured * 100, 2),
    "F1Score": round(f1_fractured * 100, 2),
    "Specificity": round(specificity * 100, 2),
    "ROC_AUC": round(roc_auc, 4) if not np.isnan(roc_auc) else "",
    "AvgConfidence": round(average_confidence * 100, 2),
    "FalseNegativeRate": round(false_negative_rate * 100, 2),
    "TruePositive": tp,
    "FalseNegative": fn,
    "FalsePositive": fp,
    "TrueNegative": tn,
    "Notes": (
        "Metrics generated from evaluate.py on the configured test_loader. "
        "Positive class is fractured. If using original Kaggle split, results "
        "should be interpreted with dataset leakage limitation."
    ),
}

metrics_df = pd.DataFrame([metrics_row])

# Save dedicated ResNet18 metrics
metrics_df.to_csv(OUTPUT_METRICS_PATH, index=False)

# Update root model_metrics.csv while preserving other model rows if present
if ROOT_METRICS_PATH.exists():
    existing_df = pd.read_csv(ROOT_METRICS_PATH)

    if "Model" in existing_df.columns:
        existing_df = existing_df[existing_df["Model"].astype(str).str.lower() != "resnet18"]
        final_df = pd.concat([existing_df, metrics_df], ignore_index=True)
    else:
        final_df = metrics_df
else:
    final_df = metrics_df

final_df.to_csv(ROOT_METRICS_PATH, index=False)


# -----------------------------
# Console summary
# -----------------------------
print("\nEvaluation Summary")
print("=" * 55)
print(f"Accuracy:            {metrics_row['Accuracy']}%")
print(f"Precision fractured: {metrics_row['Precision']}%")
print(f"Recall fractured:    {metrics_row['Recall']}%")
print(f"F1 fractured:        {metrics_row['F1Score']}%")
print(f"Specificity:         {metrics_row['Specificity']}%")
print(f"ROC-AUC:             {metrics_row['ROC_AUC']}")
print(f"Avg Confidence:      {metrics_row['AvgConfidence']}%")
print(f"False Negative Rate: {metrics_row['FalseNegativeRate']}%")
print("\nConfusion Matrix")
print(cm)
print("\nSaved files:")
print(f"- {CONFUSION_MATRIX_PATH}")
print(f"- {ROC_CURVE_PATH}")
print(f"- {OUTPUT_METRICS_PATH}")
print(f"- {ROOT_METRICS_PATH}")
print("=" * 55)