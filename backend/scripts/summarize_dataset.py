"""
Summarize YOLO-style dataset folders (images/*, labels/*) and report class stats.

Example:
    python backend/scripts/summarize_dataset.py --dataset backend/dataset_moondream
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass
class SplitSummary:
    split: str
    images: int = 0
    labels: int = 0
    annotations: int = 0
    class_ids: Dict[int, int] | None = None
    missing_labels: List[str] | None = None

    def to_dict(self) -> Dict:
        data = {
            "images": self.images,
            "labels": self.labels,
            "annotations": self.annotations,
            "class_ids": dict(sorted((self.class_ids or {}).items())),
        }
        if self.missing_labels:
            data["missing_labels"] = self.missing_labels
        return data


def iter_images(path: Path) -> Iterable[Path]:
    for file in path.rglob("*"):
        if file.is_file() and file.suffix.lower() in IMAGE_EXTS:
            yield file


def parse_label(path: Path) -> Counter:
    counter: Counter[int] = Counter()
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return counter
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        try:
            counter[int(parts[0])] += 1
        except ValueError:
            continue
    return counter


def summarize_split(dataset_dir: Path, split: str) -> SplitSummary:
    split_summary = SplitSummary(split=split, class_ids=defaultdict(int), missing_labels=[])

    images_dir = dataset_dir / "images" / split
    labels_dir = dataset_dir / "labels" / split

    image_stems = []
    for img in iter_images(images_dir):
        split_summary.images += 1
        image_stems.append(img.stem)

    label_files = list(labels_dir.glob("*.txt"))
    split_summary.labels = len(label_files)

    stems_with_labels = {lbl.stem for lbl in label_files}
    missing = sorted(set(image_stems) - stems_with_labels)
    if missing:
        split_summary.missing_labels = missing

    for lbl in label_files:
        counts = parse_label(lbl)
        for cls_id, cnt in counts.items():
            split_summary.class_ids[cls_id] += cnt
            split_summary.annotations += cnt

    return split_summary


def summarize_dataset(dataset_dir: Path, splits: Sequence[str]) -> Dict:
    dataset_dir = dataset_dir.resolve()
    summary = {"dataset": str(dataset_dir)}
    image_root = dataset_dir / "images"
    if not image_root.exists():
        raise FileNotFoundError(f"Missing images directory: {image_root}")
    summary["img_exts"] = sorted(
        {img.suffix.lower() for img in image_root.rglob("*.*") if img.is_file()}
    )

    split_data = {}
    for split in splits:
        split_data[split] = summarize_split(dataset_dir, split).to_dict()
    summary["splits"] = split_data
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        default="backend/dataset_moondream",
        help="Đường dẫn tới thư mục dataset (mặc định: backend/dataset_moondream)",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=("train", "val"),
        help="Danh sách splits cần thống kê (mặc định: train val)",
    )
    parser.add_argument(
        "--save",
        help="Nếu cung cấp, lưu JSON summary vào đường dẫn này",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    dataset_dir = Path(args.dataset)
    if not dataset_dir.exists():
        raise SystemExit(f"Dataset không tồn tại: {dataset_dir}")

    summary = summarize_dataset(dataset_dir, args.splits)
    json_output = json.dumps(summary, indent=2, ensure_ascii=False)
    print(json_output)

    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json_output, encoding="utf-8")
        print(f"\n✅ Saved summary to {save_path}")


if __name__ == "__main__":
    main()

