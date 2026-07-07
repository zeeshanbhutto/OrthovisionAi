from pathlib import Path

from PIL import ImageFile
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


# Fix truncated/corrupted image loading issue
ImageFile.LOAD_TRUNCATED_IMAGES = True


# -----------------------------
# Project paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data" / "Bone_Fracture_Binary_Classification"
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "val"
TEST_DIR = DATA_DIR / "test"


# -----------------------------
# Parameters
# -----------------------------
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
NUM_WORKERS = 0


# -----------------------------
# Validate dataset folders
# -----------------------------
def validate_dataset_path():
    required_dirs = {
        "DATA_DIR": DATA_DIR,
        "TRAIN_DIR": TRAIN_DIR,
        "VAL_DIR": VAL_DIR,
        "TEST_DIR": TEST_DIR,
    }

    missing = []

    for name, path in required_dirs.items():
        if not path.exists():
            missing.append(f"{name}: {path}")

    if missing:
        missing_text = "\n".join(missing)

        raise FileNotFoundError(
            "Dataset folder structure is incomplete.\n\n"
            "Expected structure:\n"
            "data/Bone_Fracture_Binary_Classification/\n"
            "  train/\n"
            "    fractured/\n"
            "    not fractured/\n"
            "  val/\n"
            "    fractured/\n"
            "    not fractured/\n"
            "  test/\n"
            "    fractured/\n"
            "    not fractured/\n\n"
            f"Missing paths:\n{missing_text}"
        )


validate_dataset_path()


# -----------------------------
# Transforms
# -----------------------------
train_transforms = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    ),
])

val_test_transforms = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    ),
])


# -----------------------------
# Datasets
# -----------------------------
train_dataset = datasets.ImageFolder(
    root=str(TRAIN_DIR),
    transform=train_transforms,
)

val_dataset = datasets.ImageFolder(
    root=str(VAL_DIR),
    transform=val_test_transforms,
)

test_dataset = datasets.ImageFolder(
    root=str(TEST_DIR),
    transform=val_test_transforms,
)


# -----------------------------
# Class names
# -----------------------------
class_names = train_dataset.classes

EXPECTED_CLASS_NAMES = ["fractured", "not fractured"]

if class_names != EXPECTED_CLASS_NAMES:
    print(
        "\nWARNING: Dataset class order is different from expected.\n"
        f"Expected: {EXPECTED_CLASS_NAMES}\n"
        f"Found:    {class_names}\n"
        "Update src/predict.py class_names if required.\n"
    )


# -----------------------------
# DataLoaders
# -----------------------------
train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=NUM_WORKERS,
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
)


# -----------------------------
# Debug / Check
# -----------------------------
if __name__ == "__main__":
    print("Dataset path:", DATA_DIR)
    print("Classes:", class_names)
    print("Class to index:", train_dataset.class_to_idx)

    print("\nImage counts:")
    print("Train images:", len(train_dataset))
    print("Validation images:", len(val_dataset))
    print("Test images:", len(test_dataset))

    print("\nBatch counts:")
    print("Train batches:", len(train_loader))
    print("Validation batches:", len(val_loader))
    print("Test batches:", len(test_loader))