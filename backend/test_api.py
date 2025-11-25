"""
Script để test API endpoints
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\nTesting / endpoint...")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_detect(image_path):
    """Test detect endpoint"""
    print(f"\nTesting /detect endpoint with image: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/detect", files=files)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Detections: {result.get('count', 0)}")
                print(f"Response: {json.dumps(result, indent=2)}")
            else:
                print(f"Error: {response.text}")
            return response.status_code == 200
    except FileNotFoundError:
        print(f"Image file not found: {image_path}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SmartSort AI - API Test Script")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health()
    
    # Test root endpoint
    root_ok = test_root()
    
    # Test detect endpoint (requires an image file)
    # Uncomment and provide path to test image
    # detect_ok = test_detect("test_image.jpg")
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Health endpoint: {'✅ OK' if health_ok else '❌ FAILED'}")
    print(f"Root endpoint: {'✅ OK' if root_ok else '❌ FAILED'}")
    print("=" * 50)
