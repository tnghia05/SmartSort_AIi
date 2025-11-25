# Hướng Dẫn Download Dataset từ Roboflow

## Bước 1: Tạo tài khoản Roboflow

1. Truy cập: https://roboflow.com
2. Đăng ký tài khoản miễn phí (Sign Up)
3. Xác nhận email

## Bước 2: Tìm Dataset Waste Classification

**Cách 1: Tìm qua Roboflow Universe (Khuyến nghị)**
1. Vào: https://universe.roboflow.com
2. Search: "waste classification" hoặc "trash"
3. Chọn dataset phù hợp (12 classes hoặc tương tự)

**Cách 2: Tìm qua Google**
1. Google search: "roboflow waste classification dataset"
2. Click vào kết quả từ universe.roboflow.com
3. Chọn dataset phù hợp

**Cách 3: Tạo dataset mới (nếu không tìm thấy)**
1. Đăng nhập Roboflow
2. Tạo project mới
3. Upload ảnh và annotate

**Dataset phổ biến:**
- Waste Classification Dataset
- Trash Detection Dataset
- Recyclable Waste Dataset

## Bước 3: Lấy Thông Tin Dataset

Khi mở một dataset, bạn sẽ thấy URL như:
```
https://roboflow.com/[WORKSPACE]/[PROJECT]/[VERSION]
```

Ví dụ:
```
https://roboflow.com/waste-classification/dataset-abc/1
```

Trong đó:
- **Workspace**: `waste-classification` (phần đầu tiên)
- **Project**: `dataset-abc` (phần thứ hai)
- **Version**: `1` (số ở cuối)

## Bước 4: Lấy API Key

1. Click vào avatar (góc trên bên phải)
2. Chọn **Settings**
3. Vào tab **API**
4. Copy **API Key** (bắt đầu bằng `..._...`)

## Bước 5: Download Dataset

### Cách 1: Sử dụng Script

```bash
cd backend
python download_dataset.py
# Chọn option 3 (Roboflow)
# Nhập:
# - Workspace: waste-classification
# - Project: dataset-abc
# - Version: 1
# - API Key: [paste API key]
```

### Cách 2: Download trực tiếp từ Roboflow

1. Vào dataset page
2. Click **Download**
3. Chọn format: **YOLOv8**
4. Click **Download**
5. Extract file zip
6. Đặt vào thư mục `backend/dataset/`

## Ví dụ Cụ Thể

### Dataset: Waste Classification Dataset

**URL**: `https://roboflow.com/waste-classification/waste-classification-dataset/1`

**Thông tin:**
- Workspace: `waste-classification`
- Project: `waste-classification-dataset`
- Version: `1`

**Trong script:**
```
Enter Roboflow workspace: waste-classification
Enter project name: waste-classification-dataset
Enter version number: 1
Enter Roboflow API key: [paste your API key]
```

## Lưu ý

1. **API Key** là bí mật - không chia sẻ
2. **Version** thường là số (1, 2, 3, ...)
3. Dataset sẽ được download với **YOLO format sẵn**
4. Sau khi download, kiểm tra bằng `prepare_dataset.py`

## Troubleshooting

### "Invalid workspace/project"
- Kiểm tra lại tên workspace và project trong URL
- Đảm bảo dataset là public hoặc bạn có quyền truy cập

### "Invalid API key"
- Kiểm tra lại API key trong Settings
- Đảm bảo copy đầy đủ (không có khoảng trắng)

### "Version not found"
- Kiểm tra version number trong URL
- Thử version 1 trước (thường là version đầu tiên)

## Next Steps

Sau khi download:
1. Kiểm tra dataset: `python prepare_dataset.py`
2. Train model: Xem `TRAIN_QUICK_START.md`

