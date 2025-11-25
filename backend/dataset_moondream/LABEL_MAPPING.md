# Đối chiếu bộ nhãn Moondream ↔ App

## 1. Danh sách class theo YOLO ID

| ID | Tên gốc (YOLO) | Nhóm lớn (`class_group`) | Hiển thị trong app |
|----|----------------|--------------------------|--------------------|
| 0  | battery        | hazardous                | Pin                |
| 1  | biological     | organic                  | Hữu cơ             |
| 2  | brown-glass    | recyclable               | Thủy tinh nâu      |
| 3  | cardboard      | recyclable               | Giấy (Bìa carton)  |
| 4  | clothes        | reusable                 | Quần áo            |
| 5  | green-glass    | recyclable               | Thủy tinh xanh     |
| 6  | metal          | recyclable               | Kim loại           |
| 7  | paper          | recyclable               | Giấy               |
| 8  | plastic        | recyclable               | Nhựa               |
| 9  | shoes          | reusable                 | Giày dép           |
| 10 | trash          | residual                 | Rác tổng hợp       |
| 11 | white-glass    | recyclable               | Thủy tinh trắng    |

> Bảng trên phải luôn đồng bộ với `CLASS_NAMES` trong `backend/prepare_dataset.py`, `WASTE_CLASS_MAPPING` trong `backend/api.py` và `TrashType` + `DISPLAY_LABELS.md` bên mobile.

## 2. Thống kê dataset hiện tại

File `dataset_summary.json` (tạo bởi `scripts/summarize_dataset.py`) cho thấy:

- Train split chỉ chứa class IDs 6, 7, 8 (Metal, Paper, Plastic)
- Val split chỉ chứa class ID 8 (Plastic)
- Các class khác không có mẫu → cần bổ sung dữ liệu

## 3. Checklist đồng bộ backend/mobile

1. **Backend**: cập nhật `WASTE_CLASS_MAPPING` nếu thêm class mới (vd. hazard/glass)
2. **Mobile**:
   - `mobile/src/types/index.ts` → `TrashType`
   - `mobile/src/utils/binMapping.ts` → thông tin thùng rác
   - `mobile/DISPLAY_LABELS.md` → logic hiển thị
3. **Docs**: Ghi nhận thay đổi ở `IMPROVED_MAPPING.md` hoặc tài liệu tương ứng

## 4. Cách chạy đối chiếu tự động

```bash
python backend/scripts/summarize_dataset.py \
  --dataset backend/dataset_moondream \
  --save backend/dataset_moondream/dataset_summary.json
```

Kết quả JSON giúp kiểm tra nhanh:

- Số lượng ảnh/nhãn từng split
- Số lượng bbox
- Phân bố class IDs
- Các ảnh thiếu nhãn (nếu có)

## 5. Hành động kế tiếp

- Bổ sung dữ liệu cho các class thiếu thông qua `scripts/convert_moondream_to_yolo.py` hoặc nguồn khác
- Sau khi thêm dữ liệu, chạy lại script để xác nhận phân bố cân bằng

