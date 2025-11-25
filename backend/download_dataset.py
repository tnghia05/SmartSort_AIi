"""
Script to download waste classification datasets from various sources
Supports: Kaggle, Roboflow, Hugging Face, GitHub
"""
import os
import sys
import zipfile
import shutil
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def download_from_kaggle(dataset_name: str, output_dir: str = "dataset"):
    """
    Download dataset from Kaggle
    
    Args:
        dataset_name: Kaggle dataset name (e.g., 'garythung/trashnet')
        output_dir: Output directory for dataset
    """
    try:
        import kaggle
        print(f"Downloading dataset from Kaggle: {dataset_name}")
        print("Note: You need to set up Kaggle API credentials first.")
        print("See: https://www.kaggle.com/docs/api")
        
        # Download dataset
        kaggle.api.dataset_download_files(
            dataset_name,
            path=output_dir,
            unzip=True
        )
        print(f"✅ Dataset downloaded to: {output_dir}")
        return True
    except ImportError:
        print("❌ kaggle package not installed")
        print("Install with: pip install kaggle")
        return False
    except Exception as e:
        print(f"❌ Error downloading from Kaggle: {e}")
        return False


def download_from_roboflow(workspace: str, project: str, version: int, api_key: str, output_dir: str = "dataset"):
    """
    Download dataset from Roboflow
    
    Args:
        workspace: Roboflow workspace name
        project: Project name
        version: Dataset version number
        api_key: Roboflow API key
        output_dir: Output directory for dataset
    """
    try:
        from roboflow import Roboflow
        
        print(f"Downloading dataset from Roboflow: {workspace}/{project}")
        print("⚠️  Lưu ý: Dataset có thể nặng 2-4 GB, download sẽ mất vài phút đến vài chục phút")
        print()
        
        rf = Roboflow(api_key=api_key)
        project_obj = rf.workspace(workspace).project(project)
        
        # Try to detect project type and use appropriate format
        try:
            # Try YOLOv8 format first (for object detection)
            print("🔄 Trying YOLOv8 format (object detection)...")
            dataset = project_obj.version(version).download("yolov8", location=output_dir)
            print("✅ Downloaded as YOLOv8 format (object detection)")
        except Exception as e1:
            error_str = str(e1)
            if "invalid format for project type classification" in error_str.lower():
                # It's a classification project, use folder format
                print("⚠️  Project is classification type, using 'folder' format...")
                try:
                    dataset = project_obj.version(version).download("folder", location=output_dir)
                    print("✅ Downloaded as folder format (classification)")
                    print()
                    print("⚠️  LƯU Ý: Dataset này là CLASSIFICATION (không có bounding boxes)")
                    print("   Để train YOLOv8 cho object detection, bạn cần:")
                    print("   1. Tìm dataset OBJECT DETECTION khác trên Roboflow")
                    print("   2. Hoặc convert classification → detection (cần annotate lại)")
                    print("   3. Xem: backend/ALTERNATIVE_DATASETS.md để tìm dataset detection")
                    print()
                except Exception as e2:
                    print(f"❌ Error downloading with folder format: {e2}")
                    print()
                    print("💡 Gợi ý:")
                    print("   1. Download thủ công từ Roboflow website:")
                    print(f"      https://universe.roboflow.com/{workspace}/{project}")
                    print("   2. Click 'Download Dataset' → Chọn format phù hợp")
                    print("   3. Hoặc tìm dataset OBJECT DETECTION khác")
                    return False
            else:
                raise e1
        
        # Estimate size
        import os
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(output_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        
        size_mb = total_size / (1024 * 1024)
        size_gb = total_size / (1024 * 1024 * 1024)
        
        print(f"✅ Dataset downloaded to: {output_dir}")
        print(f"📦 Dataset size: {size_mb:.2f} MB ({size_gb:.2f} GB)")
        return True
    except ImportError:
        print("❌ roboflow package not installed")
        print("Install with: pip install roboflow")
        return False
    except Exception as e:
        print(f"❌ Error downloading from Roboflow: {e}")
        return False


def download_from_huggingface(dataset_name: str, output_dir: str = "dataset"):
    """
    Download dataset from Hugging Face
    
    Args:
        dataset_name: Hugging Face dataset name (e.g., 'username/dataset-name')
        output_dir: Output directory for dataset
    """
    try:
        from datasets import load_dataset
        
        print(f"Downloading dataset from Hugging Face: {dataset_name}")
        dataset = load_dataset(dataset_name)
        
        # Save to local directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # Save dataset (format depends on dataset structure)
        dataset.save_to_disk(str(output_path))
        
        print(f"✅ Dataset downloaded to: {output_dir}")
        return True
    except ImportError:
        print("❌ datasets package not installed")
        print("Install with: pip install datasets")
        return False
    except Exception as e:
        print(f"❌ Error downloading from Hugging Face: {e}")
        return False


def list_available_datasets():
    """List available waste classification datasets"""
    print("=" * 60)
    print("Available Waste Classification Datasets")
    print("=" * 60)
    print()
    
    print("1. Kaggle Datasets:")
    print("   - garythung/trashnet (TrashNet - 6 classes)")
    print("   - Search: 'waste classification' on Kaggle")
    print("   - URL: https://www.kaggle.com/datasets")
    print()
    
    print("2. Roboflow Datasets (Khuyến nghị - YOLO format sẵn):")
    print("   - Search: 'waste' or 'trash' on Roboflow")
    print("   - URL: https://roboflow.com/datasets")
    print()
    print("   📝 Cách lấy thông tin:")
    print("   1. Vào dataset page trên Roboflow")
    print("   2. URL sẽ có dạng: roboflow.com/[workspace]/[project]/[version]")
    print("   3. Lấy API key: Settings → API → Copy API key")
    print("   4. Xem hướng dẫn chi tiết: backend/ROBOFLOW_GUIDE.md")
    print()
    
    print("3. Hugging Face Datasets:")
    print("   - Search: 'waste classification' on Hugging Face")
    print("   - URL: https://huggingface.co/datasets")
    print()
    
    print("4. GitHub Repositories:")
    print("   - TrashNet: https://github.com/garythung/trashnet")
    print("   - TACO: http://tacodataset.org/")
    print()
    
    print("5. Recommended for YOLO format:")
    print("   - Roboflow (easiest - YOLO format ready)")
    print("   - Kaggle (may need conversion)")
    print()


def main():
    """Main function"""
    print("=" * 60)
    print("Waste Classification Dataset Downloader")
    print("=" * 60)
    print()
    
    print("Choose download source:")
    print("1. List available datasets")
    print("2. Download from Kaggle")
    print("3. Download from Roboflow")
    print("4. Download from Hugging Face")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        list_available_datasets()
    elif choice == "2":
        dataset_name = input("Enter Kaggle dataset name (e.g., 'garythung/trashnet'): ").strip()
        output_dir = input("Enter output directory (default: 'dataset'): ").strip() or "dataset"
        download_from_kaggle(dataset_name, output_dir)
    elif choice == "3":
        print("\n📝 Hướng dẫn tìm dataset lớn:")
        print("1. Vào https://universe.roboflow.com")
        print("2. Search 'waste classification'")
        print("3. Filter 'Image Count: 5000+' để tìm dataset nhiều ảnh")
        print("4. Hoặc scroll xuống tìm dataset 'by GaCha' (9161 images)")
        print("5. Click vào dataset → URL có dạng: universe.roboflow.com/[workspace]/[project]/[version]")
        print("6. Lấy API key: Đăng nhập → Settings → API → Copy")
        print("7. Xem chi tiết: backend/FIND_LARGE_DATASET.md")
        print()
        
        workspace = input("Enter Roboflow workspace (ví dụ: waste-classification): ").strip()
        if not workspace:
            print("❌ Workspace không được để trống!")
            return
            
        project = input("Enter project name (ví dụ: waste-classification-dataset): ").strip()
        if not project:
            print("❌ Project name không được để trống!")
            return
            
        version_str = input("Enter version number (ví dụ: 1): ").strip()
        try:
            version = int(version_str)
        except ValueError:
            print("❌ Version phải là số!")
            return
            
        api_key = input("Enter Roboflow API key (Settings → API): ").strip()
        if not api_key:
            print("❌ API key không được để trống!")
            return
            
        output_dir = input("Enter output directory (default: 'dataset'): ").strip() or "dataset"
        download_from_roboflow(workspace, project, version, api_key, output_dir)
    elif choice == "4":
        dataset_name = input("Enter Hugging Face dataset name: ").strip()
        output_dir = input("Enter output directory (default: 'dataset'): ").strip() or "dataset"
        download_from_huggingface(dataset_name, output_dir)
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()

