# OrthoVision AI

**OrthoVision AI** is an AI-powered bone fracture detection and explainability system built using deep learning, Grad-CAM, and Streamlit. The system classifies X-ray images as **fractured** or **not fractured**, shows confidence score and risk level, visualizes model attention using **Grad-CAM**, supports batch screening, doctor feedback, QR-enabled PDF reports, and model performance analysis.

> **Disclaimer:** This project is developed for educational and research purposes only. It is not a replacement for clinical diagnosis or radiologist interpretation.

---

## Project Overview

Bone fracture detection from X-ray images is an important task in medical imaging. OrthoVision AI aims to support fracture screening by combining classification, explainability, and a professional web-based workflow.

The system allows users to upload an X-ray image, run AI inference, view the prediction result, inspect Grad-CAM heatmaps, review model performance, collect doctor feedback, and generate downloadable AI-assisted PDF reports.

---

## Key Features

- **Fracture Classification**
  - Predicts whether an X-ray image is fractured or not fractured.

- **Deep Learning Model**
  - Uses a trained ResNet18-based model for fracture classification.
  - Supports extension for CNN, EfficientNet, DenseNet, or other architectures.

- **Grad-CAM Explainability**
  - Highlights image regions that influenced the model's decision.
  - Provides visual evidence for AI prediction.

- **Confidence and Risk Level**
  - Displays prediction confidence.
  - Assigns risk level based on model output.

- **Professional Streamlit Dashboard**
  - Multi-page application with a clean medical AI interface.

- **Batch Screening**
  - Supports multiple X-ray image uploads.
  - Generates prediction results in table format.

- **Model Performance Dashboard**
  - Displays accuracy, precision, recall, F1-score, specificity, AUC, uncertainty, confusion matrices, ROC curves, and training graphs.

- **PDF Report Generation**
  - Creates an AI-assisted fracture screening report.
  - Includes prediction, confidence, risk level, original X-ray, Grad-CAM overlay, doctor review, QR code, and medical disclaimer.

- **Report History**
  - Stores generated PDF reports for later download.

- **Doctor Feedback Mode**
  - Allows a doctor or supervisor to review AI predictions.
  - Supports Agree, Disagree, and Needs Review feedback.
  - Saves review notes for future analysis.

- **QR Code in Report**
  - Adds report verification or report summary QR code inside the PDF report.

---

## Application Pages

```text
app/
├── streamlit_app.py
│
├── pages/
│   ├── 1_AI_Scan_Room.py
│   ├── 2_Batch_Screening.py
│   ├── 3_Explainability_Viewer.py
│   ├── 4_Model_Performance.py
│   ├── 5_Case_Gallery.py
│   └── 6_Report_History.py
│
├── components/
│   ├── sidebar.py
│   ├── prediction_card.py
│   ├── confidence_meter.py
│   ├── risk_badge.py
│   └── ui_styles.py
│
├── assets/
│   ├── logo.png
│   ├── banner.png
│   ├── icons/
│   └── sample_xrays/
│
├── generated_reports/
└── feedback/
    └── doctor_feedback.csv
```

---

## Final Project Structure

```text
Orthovision_FYP/
│
├── app/
│   ├── streamlit_app.py
│   ├── pages/
│   ├── components/
│   ├── assets/
│   ├── generated_reports/
│   └── feedback/
│
├── src/
│   ├── data/
│   ├── models/
│   ├── training/
│   ├── inference/
│   ├── evaluation/
│   ├── explainability/
│   ├── report/
│   └── utils/
│
├── models/
│   ├── classification/
│   ├── best_model/
│   └── detection/
│
├── outputs/
│   ├── predictions/
│   ├── gradcam/
│   ├── heatmap_overlays/
│   ├── confusion_matrices/
│   ├── roc_curves/
│   ├── training_plots/
│   ├── evaluation_tables/
│   └── generated_images/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── reports/
├── docs/
├── experiments/
├── tests/
│
├── resnet_fracture.pth
├── requirements.txt
├── README.md
└── run_app.bat
```

---

## Dataset

The project is designed for a multi-region bone fracture X-ray dataset containing two classes:

```text
fractured
not fractured
```

Recommended dataset structure:

```text
data/raw/Bone_Fracture_Multi_Region/
├── train/
│   ├── fractured/
│   └── non_fractured/
├── validation/
│   ├── fractured/
│   └── non_fractured/
└── test/
    ├── fractured/
    └── non_fractured/
```

---

## Model Details

The current deployed version uses a trained **ResNet18** model.

Expected model path:

```text
resnet_fracture.pth
```

or:

```text
models/classification/resnet18_model.pth
```

The model predicts one of the following classes:

```python
class_names = ["fractured", "not fractured"]
```

> Important: If your training class order is different, update the class order in the predictor file.

---

## Model Performance Metrics

The Model Performance Dashboard supports the following metrics:

- Accuracy
- Precision
- Recall / Sensitivity
- F1-score
- Specificity
- ROC-AUC
- Average Confidence
- Uncertainty
- Confusion Matrix
- Training Accuracy and Loss
- Validation Accuracy and Loss
- ROC Curve

Metrics should be stored in:

```text
outputs/evaluation_tables/model_metrics.csv
```

Expected CSV format:

```csv
Model,Accuracy,Precision,Recall,F1,Specificity,AUC,AvgConfidence
CNN,94.20,93.50,92.80,93.14,95.10,96.30,91.80
ResNet18,97.10,96.80,97.40,97.09,96.70,98.20,94.60
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/zeeshanbhutto/OrthovisionAi.git
cd OrthovisionAi
```

### 2. Create virtual environment

For Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

For Windows CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

Run the Streamlit app from the project root:

```bash
streamlit run app/streamlit_app.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

---

## PDF Report Generation

The system can generate a PDF report containing:

- Report ID
- Patient/Image ID
- Body region
- Model used
- Prediction
- Confidence score
- Risk level
- Original X-ray image
- Grad-CAM overlay
- Doctor feedback
- Doctor notes
- QR code
- Medical disclaimer

Generated reports are saved in:

```text
app/generated_reports/
```

---

## Doctor Feedback Mode

Doctor Feedback Mode allows a user to review the AI prediction.

Supported feedback options:

```text
Agree
Disagree
Needs Review
```

Feedback is saved in:

```text
app/feedback/doctor_feedback.csv
```

This feature supports a human-in-the-loop medical AI workflow.

---

## Deployment

The project can be deployed on **Streamlit Community Cloud**.

Deployment settings:

```text
Repository: zeeshanbhutto/OrthovisionAi
Branch: main
Main file path: app/streamlit_app.py
```

Before deployment, make sure:

- `requirements.txt` is available in the root directory.
- `resnet_fracture.pth` or model file is available.
- `app/streamlit_app.py` runs locally.
- Full dataset is not pushed to GitHub.
- Required outputs such as metrics and graphs are included.

For cloud deployment, prefer:

```text
opencv-python-headless
```

instead of:

```text
opencv-python
```

---

## Recommended `.gitignore`

```gitignore
venv/
myenv/
__pycache__/
*.pyc
.ipynb_checkpoints/

data/
app/generated_reports/*.pdf
outputs/generated_images/
outputs/predictions/
outputs/gradcam/
outputs/heatmap_overlays/

.DS_Store
.env
```

Do not ignore these if you want to show dashboard results on deployment:

```text
outputs/confusion_matrices/
outputs/roc_curves/
outputs/training_plots/
outputs/evaluation_tables/
```

---

## Screenshots

Add your screenshots here after deployment:

```markdown
![Home Dashboard](docs/screenshots/home_dashboard.png)
![AI Scan Room](docs/screenshots/ai_scan_room.png)
![Grad-CAM Viewer](docs/screenshots/gradcam_viewer.png)
![Model Performance](docs/screenshots/model_performance.png)
![PDF Report](docs/screenshots/pdf_report.png)
```

---

## Future Improvements

- Add EfficientNet or DenseNet model comparison.
- Add YOLO-based fracture localization.
- Add U-Net based fracture segmentation.
- Add Supabase/Firebase database for persistent feedback storage.
- Add authentication for doctor/admin users.
- Add region-wise model performance analysis.
- Add model calibration and advanced uncertainty estimation.
- Add DICOM image support.
- Add mobile-friendly UI improvements.

---

## Medical Disclaimer

This application is developed for academic research and educational demonstration only. It is not approved for clinical use. The prediction output should not be used as a final medical diagnosis. All results must be reviewed and validated by a qualified healthcare professional.

---

## Author

**Muhammad Saleem Ul Haq**  
Final Year Project: OrthoVision AI  
AI-Powered Bone Fracture Detection and Explainability System

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
