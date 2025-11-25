"""
Validate and summarize YOLO-format datasets.

Features:
- Checks folder structure (images/labels with train/val splits)
- Matches image/label counts and lists missing labels
- Validates annotation format (class ids, bbox ranges)
- Generates data.yaml automatically
- Prints per-class statistics for each split

Usage:
    python backend/prepare_dataset.py --dataset backend/dataset_moondream \
        --data-yaml backend/dataset_moondream/data.yaml
"""
import argparse
import os
import sys
import shutil
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Optional

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# 12 classes for waste classification model
CLASS_NAMES = [
    'battery',
    'biological',
    'brown-glass',
    'cardboard',
    'clothes',
    'green-glass',
    'metal',
    'paper',
    'plastic',
    'shoes',
    'trash',
    'white-glass'
]


def validate_yolo_structure(dataset_path: str) -> bool:
    """
    Validate YOLO format dataset structure
    
    Args:
        dataset_path: Path to dataset directory
        
    Returns:
        True if structure is valid
    """
    dataset_path = Path(dataset_path)
    
    print("=" * 60)
    print("Validating YOLO Dataset Structure")
    print("=" * 60)
    print()
    
    # Check required directories
    required_dirs = ['images/train', 'images/val', 'labels/train', 'labels/val']
    missing_dirs = []
    
    for dir_path in required_dirs:
        full_path = dataset_path / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        print()
        print("Expected structure:")
        print("dataset/")
        print("├── images/")
        print("│   ├── train/")
        print("│   └── val/")
        print("├── labels/")
        print("│   ├── train/")
        print("│   └── val/")
        print("└── data.yaml")
        return False
    
    print("✅ Directory structure is valid")
    return True


def check_image_label_matching(dataset_path: str) -> dict:
    """
    Check if images and labels match
    
    Args:
        dataset_path: Path to dataset directory
        
    Returns:
        Dictionary with matching statistics
    """
    dataset_path = Path(dataset_path)
    stats = {
        'train': {'images': 0, 'labels': 0, 'matched': 0, 'missing_labels': []},
        'val': {'images': 0, 'labels': 0, 'matched': 0, 'missing_labels': []}
    }
    
    print()
    print("Checking image/label matching...")
    
    for split in ['train', 'val']:
        images_dir = dataset_path / 'images' / split
        labels_dir = dataset_path / 'labels' / split
        
        # Count images
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        images = [f.stem for f in images_dir.iterdir() 
                 if f.suffix.lower() in image_extensions]
        stats[split]['images'] = len(images)
        
        # Count labels
        labels = [f.stem for f in labels_dir.iterdir() if f.suffix == '.txt']
        stats[split]['labels'] = len(labels)
        
        # Check matching
        matched = set(images) & set(labels)
        stats[split]['matched'] = len(matched)
        stats[split]['missing_labels'] = list(set(images) - set(labels))
        
        print(f"\n{split.upper()}:")
        print(f"  Images: {stats[split]['images']}")
        print(f"  Labels: {stats[split]['labels']}")
        print(f"  Matched: {stats[split]['matched']}")
        
        if stats[split]['missing_labels']:
            print(f"  ⚠️  Missing labels: {len(stats[split]['missing_labels'])}")
            if len(stats[split]['missing_labels']) <= 5:
                for missing in stats[split]['missing_labels']:
                    print(f"     - {missing}")
    
    return stats


def validate_annotations(dataset_path: str) -> dict:
    """
    Validate YOLO annotation format
    
    Args:
        dataset_path: Path to dataset directory
        
    Returns:
        Dictionary with validation results
    """
    dataset_path = Path(dataset_path)
    results = {
        'valid': 0,
        'invalid': 0,
        'errors': []
    }
    
    print()
    print("Validating annotation format...")
    
    for split in ['train', 'val']:
        labels_dir = dataset_path / 'labels' / split
        
        for label_file in labels_dir.glob('*.txt'):
            try:
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    parts = line.strip().split()
                    if len(parts) != 5:
                        results['invalid'] += 1
                        results['errors'].append(
                            f"{label_file.name}:{line_num} - Invalid format (expected 5 values)"
                        )
                        continue
                    
                    try:
                        class_id = int(parts[0])
                        coords = [float(x) for x in parts[1:]]
                        
                        # Check class_id range
                        if class_id < 0 or class_id >= len(CLASS_NAMES):
                            results['invalid'] += 1
                            results['errors'].append(
                                f"{label_file.name}:{line_num} - Invalid class_id: {class_id}"
                            )
                            continue
                        
                        # Check coordinates (should be 0-1)
                        if any(c < 0 or c > 1 for c in coords):
                            results['invalid'] += 1
                            results['errors'].append(
                                f"{label_file.name}:{line_num} - Coordinates out of range [0, 1]"
                            )
                            continue
                        
                        results['valid'] += 1
                    except ValueError:
                        results['invalid'] += 1
                        results['errors'].append(
                            f"{label_file.name}:{line_num} - Invalid number format"
                        )
            except Exception as e:
                results['invalid'] += 1
                results['errors'].append(f"{label_file.name} - Error: {str(e)}")
    
    print(f"  Valid annotations: {results['valid']}")
    print(f"  Invalid annotations: {results['invalid']}")
    
    if results['errors'] and len(results['errors']) <= 10:
        print("\n  Errors found:")
        for error in results['errors'][:10]:
            print(f"    - {error}")
    
    return results


def generate_data_yaml(dataset_path: str, output_path: str = None) -> str:
    """
    Generate data.yaml file for YOLO training
    
    Args:
        dataset_path: Path to dataset directory
        output_path: Output path for data.yaml (default: dataset_path/data.yaml)
        
    Returns:
        Path to generated data.yaml
    """
    dataset_path = Path(dataset_path)
    if output_path is None:
        output_path = dataset_path / 'data.yaml'
    else:
        output_path = Path(output_path)
    
    # Use absolute path for Colab
    abs_dataset_path = dataset_path.resolve()
    
    data = {
        'path': str(abs_dataset_path),
        'train': 'images/train',
        'val': 'images/val',
        'names': {i: name for i, name in enumerate(CLASS_NAMES)},
        'nc': len(CLASS_NAMES)
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print()
    print(f"✅ Generated data.yaml: {output_path}")
    return str(output_path)


def get_dataset_statistics(dataset_path: str) -> dict:
    """
    Get dataset statistics
    
    Args:
        dataset_path: Path to dataset directory
        
    Returns:
        Dictionary with statistics
    """
    dataset_path = Path(dataset_path)
    stats = defaultdict(lambda: defaultdict(int))
    
    for split in ['train', 'val']:
        labels_dir = dataset_path / 'labels' / split
        
        for label_file in labels_dir.glob('*.txt'):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        class_name = CLASS_NAMES[class_id] if class_id < len(CLASS_NAMES) else f"unknown_{class_id}"
                        stats[split][class_name] += 1
    
    return stats


def print_statistics(stats: dict):
    """Print dataset statistics"""
    print()
    print("=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    print()
    
    for split in ['train', 'val']:
        print(f"{split.upper()}:")
        total = sum(stats[split].values())
        for class_name in CLASS_NAMES:
            count = stats[split][class_name]
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {class_name:15} : {count:4} ({percentage:5.1f}%)")
        print(f"  {'TOTAL':15} : {total:4}")
        print()


def split_dataset(source_dir: str, output_dir: str, train_ratio: float = 0.8):
    """
    Split dataset into train/val
    
    Args:
        source_dir: Source directory with images and labels
        output_dir: Output directory
        train_ratio: Ratio for training set (default: 0.8)
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    
    # Create output structure
    for split in ['train', 'val']:
        (output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    # Get all images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    images = [f for f in source_dir.iterdir() 
             if f.suffix.lower() in image_extensions]
    
    # Shuffle and split
    import random
    random.shuffle(images)
    split_idx = int(len(images) * train_ratio)
    train_images = images[:split_idx]
    val_images = images[split_idx:]
    
    # Copy files
    for img in train_images:
        label = source_dir / f"{img.stem}.txt"
        shutil.copy2(img, output_dir / 'images' / 'train' / img.name)
        if label.exists():
            shutil.copy2(label, output_dir / 'labels' / 'train' / label.name)
    
    for img in val_images:
        label = source_dir / f"{img.stem}.txt"
        shutil.copy2(img, output_dir / 'images' / 'val' / img.name)
        if label.exists():
            shutil.copy2(label, output_dir / 'labels' / 'val' / label.name)
    
    print(f"✅ Dataset split: {len(train_images)} train, {len(val_images)} val")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate YOLO dataset and generate reports")
    parser.add_argument(
        "--dataset",
        default="dataset",
        help="Đường dẫn tới thư mục dataset (mặc định: dataset)",
    )
    parser.add_argument(
        "--data-yaml",
        default=None,
        help="Đường dẫn lưu data.yaml (mặc định: <dataset>/data.yaml)",
    )
    parser.add_argument(
        "--skip-structure",
        action="store_true",
        help="Bỏ qua kiểm tra cấu trúc (không khuyến nghị)",
    )
    return parser.parse_args()


def run(dataset_path: Path, yaml_output: Optional[Path] = None, skip_structure: bool = False) -> dict:
    print("=" * 60)
    print("Dataset Preparation Tool")
    print("=" * 60)
    print()

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {dataset_path}")

    if not skip_structure and not validate_yolo_structure(dataset_path):
        raise ValueError("Dataset structure is invalid.")

    matching_stats = check_image_label_matching(dataset_path)
    validation_results = validate_annotations(dataset_path)
    data_yaml_path = generate_data_yaml(dataset_path, yaml_output)
    stats = get_dataset_statistics(dataset_path)
    print_statistics(stats)

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✅ Dataset structure: Valid")
    print(f"✅ Train images with labels: {matching_stats['train']['matched']}")
    print(f"✅ Val images with labels: {matching_stats['val']['matched']}")
    print(f"✅ Valid annotations: {validation_results['valid']}")
    print(f"✅ data.yaml: {data_yaml_path}")
    print()
    print("Dataset is ready for training!")

    return {
        "matching": matching_stats,
        "annotations": validation_results,
        "data_yaml": data_yaml_path,
        "stats": stats,
    }


if __name__ == "__main__":
    args = parse_args()
    dataset = Path(args.dataset)
    yaml_target = Path(args.data_yaml) if args.data_yaml else None
    run(dataset, yaml_target, skip_structure=args.skip_structure)

