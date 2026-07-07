import torch.nn as nn
from torchvision import models

try:
    from torchvision.models import ResNet18_Weights
except ImportError:
    ResNet18_Weights = None


def get_resnet_model(num_classes=2, pretrained=True, freeze_backbone=False):
    """
    Create ResNet18 model for fracture classification.

    pretrained=True:
        Used during training/fine-tuning to start from ImageNet weights.

    pretrained=False:
        Used during inference because the trained checkpoint is loaded manually.

    freeze_backbone=False:
        Full fine-tuning. All layers are trainable.

    freeze_backbone=True:
        Only final classifier is trained.
    """

    if pretrained:
        if ResNet18_Weights is not None:
            model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        else:
            model = models.resnet18(pretrained=True)
    else:
        if ResNet18_Weights is not None:
            model = models.resnet18(weights=None)
        else:
            model = models.resnet18(pretrained=False)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False
    else:
        for param in model.parameters():
            param.requires_grad = True

    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    return model