"""
Convert the Hugging Face dataset `moondream/waste_detection` into YOLO format.

Usage:
    python backend/scripts/convert_moondream_to_yolo.py \
        --output-dir dataset_moondream
"""

from __future__ import annotations

import argparse
import os
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
from datasets import load_dataset
from PIL import Image

YOLO_CLASSES: List[str] = [
    "battery",
    "biological",
    "brown-glass",
    "cardboard",
    "clothes",
    "green-glass",
    "metal",
    "paper",
    "plastic",
    "shoes",
    "trash",
    "white-glass",
]

CLASS_MAPPING: Dict[str, str] = {
    "packet": "plastic",
    "FoodPackaging": "plastic",
    "PlasticBag": "plastic",
    "bottle": "plastic",
    "tissue": "paper",
    "paper": "paper",
    "can": "metal",
}

SPLIT_MAPPING = {
    "train": "train",
    "test": "val",
}


def pil_from_dataset(image) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    if isinstance(image, np.ndarray):
        return Image.fromarray(image)
    raise ValueError(f"Unsupported image type: {type(image)}")


def ensure_structure(base_dir: Path):
    for split in ("train", "val"):
        (base_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (base_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def convert(
    output_dir: Path,
    overwrite: bool = False,
) -> Tuple[Counter, Counter]:
    dataset = load_dataset("moondream/waste_detection")
    ensure_structure(output_dir)
    trash_to_id = {name: idx for idx, name in enumerate(YOLO_CLASSES)}

    mapped_counter = Counter()
    skipped_counter = Counter()

    for split, target_split in SPLIT_MAPPING.items():
        split_images = output_dir / "images" / target_split
        split_labels = output_dir / "labels" / target_split
        for idx, record in enumerate(dataset[split]):
            image_id = record.get("image_id")
            suffix = f"{image_id}" if image_id is not None else f"{idx}"
            filename_stub = f"{split}_{suffix}"
            image_path = split_images / f"{filename_stub}.jpg"
            label_path = split_labels / f"{filename_stub}.txt"

            if image_path.exists() and not overwrite:
                raise FileExistsError(
                    f"{image_path} already exists. Use --overwrite to replace existing files."
                )

            image = pil_from_dataset(record["image"])
            image.save(image_path, format="JPEG", quality=95)

            boxes: Iterable[Iterable[float]] = record["boxes"]
            labels: Iterable[str] = record["labels"]
            lines: List[str] = []

            for label, box in zip(labels, boxes):
                mapped_class = CLASS_MAPPING.get(label)
                if not mapped_class:
                    skipped_counter[label] += 1
                    continue
                class_id = trash_to_id[mapped_class]
                cx, cy, w, h = map(float, box)
                lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
                mapped_counter[mapped_class] += 1

            if not lines:
                image_path.unlink(missing_ok=True)
                continue

            label_path.write_text("\n".join(lines), encoding="utf-8")

    return mapped_counter, skipped_counter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="dataset_moondream",
        help="Thư mục chứa output dataset (mặc định: dataset_moondream)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Ghi đè nếu file ảnh đã tồn tại",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    mapped_counter, skipped_counter = convert(output_dir, overwrite=args.overwrite)

    print("\n=== Kết quả chuyển đổi ===")
    total = sum(mapped_counter.values())
    print(f"Ảnh/nhãn đã tạo: {total}")
    for cls in YOLO_CLASSES:
        if mapped_counter[cls]:
            print(f"{cls:12}: {mapped_counter[cls]}")
    if skipped_counter:
        print("\nClasses không map:")
        for label, count in skipped_counter.most_common():
            print(f"{label:12}: {count}")
        print("→ Cập nhật CLASS_MAPPING nếu cần.")


if __name__ == "__main__":
    main()

