from pathlib import Path
import random

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

from dataset import train_loader, val_loader
from model import get_resnet_model


# -----------------------------
# Reproducibility
# -----------------------------
SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False


# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_OUTPUT_PATH = PROJECT_ROOT / "resnet_fracture.pth"
LOSS_GRAPH_PATH = PROJECT_ROOT / "loss_graph.png"
ACCURACY_GRAPH_PATH = PROJECT_ROOT / "accuracy_graph.png"


# -----------------------------
# Device
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


# -----------------------------
# Model
# -----------------------------
# pretrained=True is correct for training/fine-tuning.
# freeze_backbone=False means full fine-tuning.
model = get_resnet_model(
    num_classes=2,
    pretrained=True,
    freeze_backbone=False
)

model = model.to(device)


# -----------------------------
# Loss and Optimizer
# -----------------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=0.0001
)


# -----------------------------
# Training settings
# -----------------------------
epochs = 15

train_losses = []
val_accuracies = []

best_val_accuracy = 0.0
best_epoch = 0


# -----------------------------
# Training Loop
# -----------------------------
for epoch in range(epochs):
    model.train()
    running_loss = 0.0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    avg_loss = running_loss / len(train_loader)
    train_losses.append(avg_loss)

    # -----------------------------
    # Validation
    # -----------------------------
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    val_accuracy = 100 * correct / total
    val_accuracies.append(val_accuracy)

    print(
        f"Epoch [{epoch + 1}/{epochs}] "
        f"Loss: {avg_loss:.4f} | "
        f"Val Accuracy: {val_accuracy:.2f}%"
    )

    # Save best checkpoint instead of only final epoch
    if val_accuracy > best_val_accuracy:
        best_val_accuracy = val_accuracy
        best_epoch = epoch + 1

        torch.save(model.state_dict(), MODEL_OUTPUT_PATH)

        print(
            f"Best model updated at epoch {best_epoch} "
            f"with Val Accuracy: {best_val_accuracy:.2f}%"
        )


print("\nTraining completed.")
print(f"Best epoch: {best_epoch}")
print(f"Best validation accuracy: {best_val_accuracy:.2f}%")
print(f"Model saved at: {MODEL_OUTPUT_PATH}")


# -----------------------------
# Save Graphs
# -----------------------------
plt.figure()
plt.plot(train_losses)
plt.title("Training Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.grid(True)
plt.savefig(LOSS_GRAPH_PATH, bbox_inches="tight")
plt.close()

plt.figure()
plt.plot(val_accuracies)
plt.title("Validation Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.grid(True)
plt.savefig(ACCURACY_GRAPH_PATH, bbox_inches="tight")
plt.close()

print(f"Loss graph saved at: {LOSS_GRAPH_PATH}")
print(f"Accuracy graph saved at: {ACCURACY_GRAPH_PATH}")