import torch
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

from model import get_resnet_model
from dataset import test_loader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = get_resnet_model()
model.load_state_dict(torch.load("resnet_fracture.pth", map_location=device))
model.to(device)
model.eval()

all_preds = []
all_labels = []

# Collect predictions
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)

        outputs = model(images)
        _, preds = torch.max(outputs, 1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# 📊 Classification Report
print("\n📊 Classification Report:\n")
print(classification_report(all_labels, all_preds, target_names=["fractured", "not fractured"]))

# 📊 Confusion Matrix
cm = confusion_matrix(all_labels, all_preds)

plt.figure()
sns.heatmap(cm, annot=True, fmt="d", xticklabels=["fractured", "not fractured"], yticklabels=["fractured", "not fractured"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")

plt.savefig("confusion_matrix.png")
plt.show()