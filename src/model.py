import torch
import torch.nn as nn
from torchvision import models

def get_resnet_model(num_classes=2):
    # Load pretrained ResNet18
    model = models.resnet18(pretrained=True)

    # Freeze all layers (optional but recommended)
    for param in model.parameters():
        param.requires_grad = True

    # Replace final layer
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, 2)

    return model


# Test model
if __name__ == "__main__":
    model = get_resnet_model()
    print(model)