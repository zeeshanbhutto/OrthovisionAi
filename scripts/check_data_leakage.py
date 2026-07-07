from pathlib import Path
import argparse
import csv
import re
from collections import defaultdict


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def normalize_base_id(filename: str) -> str:
    """
    Extract base image ID from augmented image names.

    Example:
    1-rotated1-rotated2.jpg -> 1
    25_rotated3.png -> 25
    image_10-flip.jpg -> image_10
    """
    stem = Path(filename).stem.lower().strip()

    patterns = [
        r"[-_]?rotated\d*",
        r"[-_]?rotate\d*",
        r"[-_]?rotation\d*",
        r"[-_]?flip\w*",
        r"[-_]?mirror\w*",
        r"[-_]?aug\w*",
        r"[-_]?zoom\w*",
        r"[-_]?brightness\w*",
        r"[-_]?contrast\w*",
        r"[-_]?shear\w*",
    ]

    combined_pattern = "|".join(patterns)
    base = re.split(combined_pattern, stem)[0]
    base = base.strip("-_ ")

    if base:
        return base

    return stem


def collect_images(split_dir: Path):
    images = []

    if not split_dir.exists():
        return images

    for file in split_dir.rglob("*"):
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(file)

    return images


def find_split_dirs(dataset_root: Path):
    split_candidates = {
        "train": ["train", "training"],
        "validation": ["validation", "val", "valid"],
        "test": ["test", "testing"],
    }

    found = {}

    for split_name, possible_names in split_candidates.items():
        for name in possible_names:
            direct_path = dataset_root / name
            if direct_path.exists() and direct_path.is_dir():
                found[split_name] = direct_path
                break

    if len(found) >= 2:
        return found

    for split_name, possible_names in split_candidates.items():
        if split_name in found:
            continue

        for folder in dataset_root.rglob("*"):
            if folder.is_dir() and folder.name.lower() in possible_names:
                found[split_name] = folder
                break

    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=str,
        default="data",
        help="Dataset root path. Example: data/raw/Bone_Fracture_Multi_Region",
    )
    args = parser.parse_args()

    project_root = Path.cwd()
    dataset_root = Path(args.dataset)

    if not dataset_root.is_absolute():
        dataset_root = project_root / dataset_root

    print("\nOrthoVision AI - Dataset Leakage Check")
    print("=" * 55)
    print(f"Dataset root: {dataset_root}")

    if not dataset_root.exists():
        print("\nERROR: Dataset path does not exist.")
        print("Please provide correct path using:")
        print("python scripts/check_data_leakage.py --dataset your_dataset_path")
        return

    split_dirs = find_split_dirs(dataset_root)

    if not split_dirs:
        print("\nERROR: No train/validation/test folders found.")
        return

    print("\nDetected split folders:")
    for split, path in split_dirs.items():
        print(f"{split}: {path}")

    split_base_map = defaultdict(lambda: defaultdict(list))

    for split, split_dir in split_dirs.items():
        images = collect_images(split_dir)

        for image_path in images:
            base_id = normalize_base_id(image_path.name)
            split_base_map[base_id][split].append(str(image_path))

        print(f"\n{split} image count: {len(images)}")
        print(f"{split} unique base IDs: {len(set(normalize_base_id(img.name) for img in images))}")

    leakage_rows = []

    for base_id, split_files in split_base_map.items():
        used_splits = list(split_files.keys())

        if len(used_splits) > 1:
            leakage_rows.append({
                "base_id": base_id,
                "splits_found": ", ".join(used_splits),
                "train_files": " | ".join(split_files.get("train", [])),
                "validation_files": " | ".join(split_files.get("validation", [])),
                "test_files": " | ".join(split_files.get("test", [])),
            })

    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)

    report_path = output_dir / "data_leakage_report.csv"

    with open(report_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "base_id",
            "splits_found",
            "train_files",
            "validation_files",
            "test_files",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leakage_rows)

    print("\n" + "=" * 55)

    if leakage_rows:
        print("LEAKAGE FOUND")
        print(f"Number of leaked base IDs: {len(leakage_rows)}")
        print(f"Report saved at: {report_path}")
        print("\nExample leaked base IDs:")
        for row in leakage_rows[:10]:
            print(f"- {row['base_id']} found in {row['splits_found']}")
    else:
        print("NO DATA LEAKAGE FOUND")
        print("No same base image ID was found across train/validation/test splits.")

    print("=" * 55)


if __name__ == "__main__":
    main()