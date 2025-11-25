"""
Script to download waste classification model from Hugging Face
"""
import os
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def download_waste_model():
    """Download waste classification model from Hugging Face"""
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
        
        print("=" * 60)
        print("Downloading Waste Classification Model from Hugging Face")
        print("=" * 60)
        print()
        
        # Create models directory
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        print(f"Models directory: {models_dir.absolute()}")
        print()
        
        repo_id = "kendrickfff/waste-classification-yolov8-ken"
        print(f"Checking repository: {repo_id}")
        
        # List files in repository to find model file
        try:
            files = list_repo_files(repo_id, repo_type="model")
            print(f"Files in repository:")
            for file in files:
                print(f"   - {file}")
            print()
            
            # Try to find model file
            model_files = [f for f in files if f.endswith('.pt')]
            if not model_files:
                print("WARNING: No .pt files found in repository")
                print("Trying common filenames...")
                model_files = ['best.pt', 'weights/best.pt', 'runs/detect/train/weights/best.pt']
        except Exception as e:
            print(f"WARNING: Could not list repository files: {e}")
            print("Trying common filenames...")
            model_files = ['best.pt', 'weights/best.pt', 'runs/detect/train/weights/best.pt']
        
        # Try to download model file
        model_path = None
        for filename in model_files:
            try:
                print(f"Trying to download: {filename}...")
                model_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    local_dir=models_dir,
                    local_dir_use_symlinks=False
                )
                print(f"SUCCESS: Model downloaded successfully!")
                print(f"Location: {model_path}")
                break
            except Exception as e:
                print(f"FAILED: Could not download {filename}: {e}")
                continue
        
        if model_path is None:
            print("\nERROR: Could not download model automatically")
            print("\nManual download instructions:")
            print("1. Go to: https://huggingface.co/kendrickfff/waste-classification-yolov8-ken")
            print("2. Find and download the .pt model file")
            print("3. Place it in backend/models/ directory as 'best.pt'")
            print("4. Restart the backend server")
            return None
        
        # Check if file exists
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
            print(f"Model size: {file_size:.2f} MB")
        
        print()
        print("=" * 60)
        print("SUCCESS: Model download completed!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Backend will automatically use 'models/best.pt'")
        print("2. Restart backend server: python api.py")
        print()
        
        return model_path
        
    except ImportError:
        print("ERROR: huggingface_hub is not installed")
        print("Installing huggingface_hub...")
        print("Run: pip install huggingface-hub")
        return None
    except Exception as e:
        print(f"ERROR: Error downloading model: {e}")
        import traceback
        traceback.print_exc()
        print("\nManual download instructions:")
        print("1. Go to: https://huggingface.co/kendrickfff/waste-classification-yolov8-ken")
        print("2. Download the model file (.pt)")
        print("3. Place it in backend/models/ directory")
        print("4. Restart backend server")
        return None

if __name__ == "__main__":
    download_waste_model()

