# OrthoVision AI

**OrthoVision AI** is an explainable and verifiable deep learning-based web application for AI-assisted bone fracture screening from X-ray images. The system uses a trained **ResNet18** model to predict fracture-related patterns, provides **Grad-CAM explainability**, generates a professional **PDF report**, supports **QR-based report access**, captures **doctor review feedback**, and visualizes **AI-Doctor Agreement Analytics**.

> Academic note: This project is developed for Final Year Project (FYP), academic research, and educational demonstration only. It is not approved for real clinical diagnosis.

---

## Project Highlights

- X-ray fracture classification using a trained ResNet18 model
- Grad-CAM heatmap and overlay visualization
- Confidence score and clinical-style risk level
- AI Scan Room for single X-ray prediction
- Batch Screening for multiple X-ray images
- Explainability Viewer for visual interpretation
- Model Performance dashboard
- Case Gallery with sample X-ray cases
- Report History for generated reports
- PDF report generation using ReportLab
- QR-based report access/summary
- Doctor review mode with doctor metadata
- AI-Doctor Agreement Analytics dashboard
- Streamlit Cloud deployment

---

## Deployed Application

```text
https://orthovisionai-7qcmmcpxyudjc4ntut8d3s.streamlit.app
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Web App | Streamlit |
| Deep Learning | PyTorch, TorchVision |
| Model | ResNet18 |
| Explainability | Grad-CAM |
| Image Processing | OpenCV Headless, Pillow, NumPy |
| Evaluation | Scikit-learn, Matplotlib |
| Data Handling | Pandas, CSV |
| Charts | Plotly |
| Reports | ReportLab |
| QR | qrcode |
| Deployment | GitHub, Streamlit Cloud |

---

## Current Project Structure

```text
Orthovision_FYP/
├── .streamlit/
│   └── config.toml
├── app/
│   ├── streamlit_app.py
│   ├── assets/
│   │   ├── sample_doctor_feedback.csv
│   │   ├── icons/
│   │   └── sample_xrays/
│   │       ├── fractured_cases/
│   │       └── non_fractured_cases/
│   ├── components/
│   │   └── ui_styles.py
│   ├── feedback/
│   │   └── doctor_feedback.csv
│   ├── generated_reports/
│   └── pages/
│       ├── 1_AI_Scan_Room.py
│       ├── 2_Batch_Screening.py
│       ├── 3_Explainability_Viewer.py
│       ├── 4_Model_Performance.py
│       ├── 5_Case_Gallery.py
│       ├── 6_Report_History.py
│       └── 7_AI_Doctor_Agreement_Analytics.py
├── data/
│   └── Bone_Fracture_Binary_Classification/
│       ├── train/
│       ├── val/
│       └── test/
├── outputs/
├── scripts/
│   └── check_data_leakage.py
├── src/
│   ├── dataset.py
│   ├── evaluate.py
│   ├── gradcam.py
│   ├── model.py
│   ├── pdf_generator.py
│   ├── predict.py
│   └── train.py
├── confusion_matrix.png
├── model_metrics.csv
├── README.md
├── requirements.txt
├── resnet_fracture.pth
├── roc_curve_ud_resnet18.png
└── runtime.txt
```

This README is synced with the current project tree and removes references to non-existing folders/files such as `tests/`, `docs/`, `experiments/`, and old component files.

---

## Dataset

The project uses a binary X-ray dataset with two classes:

```text
fractured
not fractured
```

Expected local dataset structure:

```text
data/Bone_Fracture_Binary_Classification/
├── train/
│   ├── fractured/
│   └── not fractured/
├── val/
│   ├── fractured/
│   └── not fractured/
└── test/
    ├── fractured/
    └── not fractured/
```

The full dataset is not included in GitHub due to size and licensing considerations.

### Dataset Audit Note

A dataset leakage audit was performed because the dataset contains augmented image names such as rotated variants. The audit found augmentation-level overlap across the original train, validation, and test folders. Therefore, the reported model metrics are treated as **baseline results on the original Kaggle-provided split** and may be optimistic. A leakage-free group-wise re-split and retraining are recommended as future scientific validation work.

---

## Model

The deployed model uses **ResNet18** for binary fracture classification.

Class order used in the application:

```python
["fractured", "not fractured"]
```

Important note: `torchvision.datasets.ImageFolder` sorts classes alphabetically. The current dataset class order is:

```text
{'fractured': 0, 'not fractured': 1}
```

The prediction code is consistent with this order.

---

## Evaluation Metrics

The current ResNet18 evaluation on the original dataset split produced:

| Metric | Value |
|---|---:|
| Accuracy | 98.61% |
| Precision | 100.00% |
| Recall | 97.05% |
| F1 Score | 98.50% |
| Specificity | 100.00% |
| ROC-AUC | 0.9991 |
| Average Confidence | 99.73% |
| False Negative Rate | 2.95% |

Confusion matrix:

```text
[[230   7]
 [  0 268]]
```

Generate metrics with:

```bash
python src/evaluate.py
```

Output files:

```text
confusion_matrix.png
roc_curve_ud_resnet18.png
model_metrics.csv
outputs/resnet18_model_metrics.csv
```

---

## Application Pages

### 1. AI Scan Room

Single X-ray upload and prediction page. It provides patient/image ID input, body region selection, fracture prediction, confidence score, risk level, Grad-CAM overlay, doctor review form, PDF report generation, and QR-based report access.

### 2. Batch Screening

Allows multiple X-ray images to be screened in one workflow and summarizes predictions in a table.

### 3. Explainability Viewer

Shows Grad-CAM heatmap and overlay explanation to make model decisions more transparent.

### 4. Model Performance

Displays model evaluation graphs such as confusion matrix, ROC curve, training loss, and accuracy plots.

### 5. Case Gallery

Displays sample fractured and non-fractured X-ray cases for demonstration.

### 6. Report History

Shows generated PDF reports available in the local report folder.

### 7. AI-Doctor Agreement Analytics

Reads doctor feedback records and displays total reviewed cases, doctor agreed/disagreed count, needs-review count, agreement rate, average AI confidence, charts, and recent reviewed cases.

---

## Installation

### 1. Clone repository

```bash
git clone https://github.com/zeeshanbhutto/OrthovisionAi.git
cd OrthovisionAi
```

### 2. Create virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add model file

Place the trained model file in the project root:

```text
resnet_fracture.pth
```

### 5. Run application

```bash
streamlit run app/streamlit_app.py
```

---

## Training

```bash
python src/train.py
```

The training script saves the best validation checkpoint as:

```text
resnet_fracture.pth
```

It also saves:

```text
loss_graph.png
accuracy_graph.png
```

---

## Evaluation

```bash
python src/evaluate.py
```

This regenerates the model metrics CSV, confusion matrix, and ROC curve.

---

## Data Leakage Check

```bash
python scripts/check_data_leakage.py --dataset data\Bone_Fracture_Binary_Classification
```

This creates:

```text
outputs/data_leakage_report.csv
```

The leakage report is useful for documenting dataset limitations and scientific credibility in the FYP report.

---

## Deployment

The project is deployed using Streamlit Cloud.

Important deployment files:

```text
requirements.txt
runtime.txt
.streamlit/config.toml
```

For OpenCV compatibility on Streamlit Cloud, the project uses:

```text
opencv-python-headless
```

---

## Generated Files and Git Ignore

The following should generally not be committed:

```text
app/feedback/*.csv
app/generated_reports/*.pdf
outputs/generated_images/
data/
venv/
__pycache__/
```

A small demo file such as `app/assets/sample_doctor_feedback.csv` can be committed because it is used for dashboard demonstration.

---

## Limitations

- The model is trained and evaluated on a limited public dataset.
- Dataset audit found augmentation-level leakage in the original split.
- Current QR functionality provides report access/summary, not cryptographic verification.
- Doctor feedback is stored in CSV for prototype demonstration.
- Streamlit Cloud local file storage is not permanent database storage.
- The system is not clinically certified.

---

## Future Work

- Re-split dataset by base image/patient ID and retrain model
- Add independent external test dataset
- Add threshold tuning for higher fracture recall
- Add calibration and reliability diagram
- Add SQLite, Supabase, or PostgreSQL for persistent feedback storage
- Add HMAC/digital signature for QR report verification
- Add more automated tests
- Add Grad-CAM++ or Score-CAM comparison
- Add role-based doctor login
- Add mobile-responsive clinical report view

---

## Academic Disclaimer

This application is developed for academic research and educational demonstration only. It is not approved for clinical use. The prediction output should not be used as a final medical diagnosis. All results must be reviewed and validated by a qualified healthcare professional.

---

## Author

**Zeeshan Hyder Bhutto**  
BSCS Final Year Project  
Department of Computer Science  
Sindh Madressatul Islam University  

Supervisor: **Sir Ameen Khowaja**

---

## License

This project is released for academic and educational purposes.
