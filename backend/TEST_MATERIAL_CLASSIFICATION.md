# Test Material Classification

## Bước 1: Restart Backend

CLIP sẽ được load tự động khi backend khởi động.

```bash
cd backend
python api.py
```

Bạn sẽ thấy log:
```
✅ CLIP available for material classification
✅ CLIP model loaded for material classification
```

## Bước 2: Test với Web App

1. **Mở web app:**
   ```bash
   cd web
   npm run dev
   ```

2. **Truy cập:** `http://localhost:5173` hoặc `https://localhost:5173` (nếu dùng HTTPS)

3. **Bật camera** và hướng vào:
   - **Cup** (ly nhựa, ly thủy tinh, ly kim loại)
   - **Bottle** (chai nhựa, chai thủy tinh)
   - **Bowl** (bát nhựa, bát thủy tinh, bát gốm)

4. **Kiểm tra kết quả:**
   - Class name sẽ hiển thị: `cup-plastic`, `cup-glass`, `bottle-plastic`, etc.
   - Material sẽ được hiển thị trong detection response

## Bước 3: Test với API trực tiếp

### Test với curl:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test với base64 image (cần encode ảnh trước)
# Hoặc dùng Postman/Thunder Client
```

### Test với Python script:

Tạo file `test_material.py`:

```python
import requests
import base64
from PIL import Image
import io

# Load image
image_path = "path/to/your/cup_image.jpg"
with open(image_path, "rb") as f:
    image_data = f.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

# Send request
response = requests.post(
    "http://localhost:8000/detect-base64",
    json={"image": base64_image, "format": "base64"}
)

result = response.json()
print("Detections:")
for det in result.get("detections", []):
    print(f"  - Class: {det.get('class')}")
    print(f"    Material: {det.get('material', 'N/A')}")
    print(f"    Confidence: {det.get('confidence', 0):.2f}")
```

## Kết quả mong đợi

### Khi phát hiện cup:
```json
{
  "class": "cup-plastic",
  "class_original": "cup",
  "material": "plastic",
  "class_group": "recyclable",
  "confidence": 0.85
}
```

### Khi phát hiện bottle:
```json
{
  "class": "bottle-glass",
  "class_original": "bottle",
  "material": "glass",
  "class_group": "recyclable",
  "confidence": 0.82
}
```

## Troubleshooting

### CLIP không load:
- Kiểm tra log backend có thấy "✅ CLIP model loaded" không
- Nếu không, kiểm tra: `python -c "import clip; print('OK')"`

### Material không được nhận diện:
- Đảm bảo vật thể rõ ràng, đủ ánh sáng
- Bounding box phải đủ lớn (> 20x20 pixels)
- Vật thể phải là một trong: cup, bottle, bowl, wine glass, vase, container

### Performance chậm:
- CLIP chạy trên CPU có thể chậm (1-2 giây mỗi detection)
- Nếu có GPU, CLIP sẽ tự động dùng GPU
- Heuristics nhanh hơn nhưng kém chính xác

