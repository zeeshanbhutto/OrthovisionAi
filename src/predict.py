from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from src.model import get_resnet_model
from src.gradcam import GradCAM


class FracturePredictor:
    def __init__(self, model_path=None, device=None):
        self.project_root = Path(__file__).resolve().parents[1]
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model_path = self._resolve_model_path(model_path)

        self.class_names = ["fractured", "not fractured"]

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            )
        ])

        self.model = self._load_model()
        self.gradcam = GradCAM(self.model, self.model.layer4[-1])

    def _resolve_model_path(self, model_path):
        candidates = []

        if model_path:
            candidates.append(Path(model_path))

        candidates.extend([
            self.project_root / "resnet_fracture.pth",
            self.project_root / "models" / "classification" / "resnet18_model.pth",
            self.project_root / "models" / "best_model" / "best_classifier.pth",
        ])

        for path in candidates:
            if path.exists():
                return path

        raise FileNotFoundError(
            "Model file not found. Put resnet_fracture.pth in project root "
            "or update model_path in FracturePredictor."
        )

    def _load_model(self):
        model = get_resnet_model()

        checkpoint = torch.load(self.model_path, map_location=self.device)

        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        else:
            state_dict = checkpoint

        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()

        return model

    def _get_risk_level(self, prediction, confidence_percent):
        prediction = prediction.lower()

        if prediction == "fractured":
            if confidence_percent >= 80:
                return "High"
            return "Medium"

        if confidence_percent < 70:
            return "Medium"

        return "Low"

    def predict(self, pil_image, generate_gradcam=True):
        image = pil_image.convert("RGB")

        original_224 = np.array(image.resize((224, 224)))

        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            probabilities = torch.softmax(output, dim=1)
            confidence, prediction_index = torch.max(probabilities, 1)

        pred_idx = prediction_index.item()
        confidence_percent = confidence.item() * 100
        prediction = self.class_names[pred_idx]
        risk_level = self._get_risk_level(prediction, confidence_percent)

        result = {
            "prediction": prediction,
            "confidence": confidence_percent,
            "risk_level": risk_level,
            "probabilities": probabilities.detach().cpu().numpy()[0],
            "original_image": Image.fromarray(original_224),
            "heatmap_image": None,
            "overlay_image": None,
        }

        if generate_gradcam:
            cam = self.gradcam.generate(input_tensor, pred_idx)

            heatmap = cv2.resize(cam, (224, 224))
            heatmap = np.uint8(255 * heatmap)
            heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

            overlay = cv2.addWeighted(original_224, 0.60, heatmap, 0.40, 0)

            result["heatmap_image"] = Image.fromarray(heatmap)
            result["overlay_image"] = Image.fromarray(overlay)

        return result