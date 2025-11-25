# Nhận diện chất liệu (Material Classification)

## Tính năng

Hệ thống có thể nhận diện chất liệu của các vật thể như:
- **Cup** → `cup-plastic`, `cup-glass`, `cup-metal`, `cup-paper`
- **Bottle** → `bottle-plastic`, `bottle-glass`, `bottle-metal`
- **Bowl** → `bowl-plastic`, `bowl-glass`, `bowl-ceramic`
- **Vase** → `vase-glass`, `vase-ceramic`, `vase-plastic`
- **Container** → `container-plastic`, `container-glass`, `container-metal`

## Cách hoạt động

1. **YOLO detection**: Phát hiện vật thể (ví dụ: "cup")
2. **Crop bounding box**: Cắt phần ảnh chứa vật thể
3. **Material classification**: Phân loại chất liệu từ crop:
   - **CLIP model** (nếu có): Sử dụng vision-language model để phân loại chính xác
   - **Heuristics** (fallback): Phân tích màu sắc, độ trong suốt, edges

## Cài đặt CLIP (Tùy chọn - Khuyến nghị)

CLIP cho độ chính xác cao hơn, nhưng không bắt buộc. Hệ thống sẽ tự động dùng heuristics nếu CLIP không có.

### Cài đặt:

```bash
# Cài đặt PyTorch (chọn version phù hợp với hệ thống)
# CPU only:
pip install torch torchvision

# Hoặc với CUDA (nếu có GPU):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Cài đặt CLIP
pip install git+https://github.com/openai/CLIP.git
```

### Kiểm tra:

```bash
cd backend
python -c "import clip; print('✅ CLIP installed')"
```

## Cấu hình

### Classes được phân loại chất liệu:

Mặc định, các class sau sẽ được phân loại chất liệu:
- `cup`
- `bottle`
- `bowl`
- `wine glass`
- `vase`
- `container`

Có thể thêm class khác trong `MATERIAL_CLASSES` trong `api.py`.

### Material options:

Hệ thống có thể nhận diện các chất liệu:
- **plastic** - Nhựa
- **glass** - Thủy tinh
- **metal** - Kim loại
- **ceramic** - Gốm sứ
- **paper** - Giấy

## Response format

Khi phát hiện vật thể có chất liệu, response sẽ có format:

```json
{
  "detections": [
    {
      "class": "cup-plastic",
      "class_original": "cup",
      "material": "plastic",
      "class_group": "recyclable",
      "confidence": 0.85,
      "bbox": {...}
    }
  ]
}
```

## Heuristics (Fallback)

Nếu CLIP không có, hệ thống dùng heuristics dựa trên:
- **Edge density**: Glass/metal có nhiều edges hơn
- **Brightness**: Glass thường sáng hơn
- **Color variance**: Glass trong suốt → ít màu sắc
- **Aspect ratio**: Một số vật thể có tỷ lệ đặc trưng

## Troubleshooting

### CLIP không load được:
- Kiểm tra đã cài đặt: `pip list | grep clip`
- Kiểm tra PyTorch: `python -c "import torch; print(torch.__version__)"`
- Hệ thống sẽ tự động dùng heuristics

### Material không được nhận diện:
- Đảm bảo bounding box đủ lớn (> 20x20 pixels)
- Kiểm tra ánh sáng đủ tốt
- Vật thể phải rõ ràng, không bị che khuất

### Performance:
- CLIP có thể chậm hơn (cần GPU để tối ưu)
- Heuristics nhanh hơn nhưng kém chính xác hơn
- Có thể disable material classification bằng cách comment code

