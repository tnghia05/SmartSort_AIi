"""
Wrapper script to train the Moondream waste detection model with Ultralytics YOLO.

Usage examples:
    # Train with default config (yolov8n) for 50 epochs
    python backend/train.py

    # Train with custom settings
    python backend/train.py --data backend/dataset_moondream/data.yaml \
        --model yolov8m.pt --epochs 80 --imgsz 640 --batch 16 --name moondream-v1
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLO model for waste detection")
    parser.add_argument(
        "--data",
        default="backend/dataset_moondream/data.yaml",
        help="Đường dẫn tới file data.yaml",
    )
    parser.add_argument(
        "--model",
        default="yolov8n.pt",
        help="Checkpoint khởi tạo (ví dụ: yolov8n.pt hoặc path tới model tuỳ chỉnh)",
    )
    parser.add_argument("--epochs", type=int, default=50, help="Số epoch huấn luyện")
    parser.add_argument("--imgsz", type=int, default=640, help="Kích thước ảnh (imgsz)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--workers", type=int, default=4, help="Số worker dataloader")
    parser.add_argument(
        "--project",
        default="runs/train",
        help="Thư mục lưu kết quả (tương tự --project của Ultralytics)",
    )
    parser.add_argument(
        "--name",
        default="moondream",
        help="Tên run (mặc định: moondream)",
    )
    parser.add_argument(
        "--resume",
        default=None,
        help="Đường dẫn run để resume (ví dụ: runs/train/moondream)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f"data.yaml không tồn tại: {data_path}")

    if args.resume:
        print(f"▶️ Resuming training from {args.resume}")
        model = YOLO(args.resume)
        model.train(resume=True)
        return

    print(f"🚀 Training YOLO model: {args.model}")
    print(f"📁 Dataset config: {data_path}")

    model = YOLO(args.model)
    model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        workers=args.workers,
        project=args.project,
        name=args.name,
    )


if __name__ == "__main__":
    main()

