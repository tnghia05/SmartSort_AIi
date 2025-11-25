"""
Test script for /detect-base64 endpoint
"""
import requests
import base64
import io
from PIL import Image

# Create a test image
img = Image.new('RGB', (640, 640), color='red')
buf = io.BytesIO()
img.save(buf, format='JPEG')
img_b64 = base64.b64encode(buf.getvalue()).decode()

# Test the endpoint
print("Testing /detect-base64 endpoint...")
print(f"Image size: {len(img_b64)} bytes (base64)")

try:
    response = requests.post(
        'http://localhost:8000/detect-base64',
        json={
            'image': img_b64,
            'format': 'base64'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"Detections: {result.get('count', 0)}")
        print(f"Response: {result}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

