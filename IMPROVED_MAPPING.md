# Cải thiện Class Mapping - Gom nhóm xử lý lớn

## 1. Vấn đề ban đầu

- Model Moondream có 12 nhãn, app chỉ hiển thị 4 nhóm chính → “other” xuất hiện quá nhiều.
- Người dùng khó phân biệt pin, quần áo, thủy tinh vì đều thành “Khác”.

## 2. Giải pháp mới

Giữ nguyên 12 nhãn để hiển thị chi tiết, nhưng bổ sung **nhóm xử lý lớn** (`TrashType`) nhằm gợi ý quy trình phân loại:

| Nhóm xử lý | Màu/Icon | Mô tả | Nhãn Moondream thuộc nhóm |
|------------|----------|-------|---------------------------|
| `organic` | 🍃 | Rác hữu cơ/ sinh học | biological |
| `recyclable` | ♻️ | Nhựa, kim loại, giấy, thủy tinh có thể tái chế | plastic, metal, paper, cardboard, brown/green/white-glass |
| `hazardous` | ⚠️ | Chất thải nguy hại (pin) | battery |
| `reusable` | 👕 | Vải vóc/quần áo có thể tái sử dụng | clothes, shoes |
| `residual` | 🗑️ | Rác hỗn hợp, khó tái chế | trash |

## 3. Thay đổi trong code

### Backend (`backend/api.py`)
- `WASTE_CLASS_MAPPING` trả về 5 nhóm trên.
- Payload detection:
  ```json
  {
    "class": "cardboard",
    "class_group": "recyclable",
    ...
  }
  ```

### Mobile
- `TrashType` (trong `src/types/index.ts`) = union của 5 nhóm mới.
- `BIN_MAPPING` cập nhật màu/icon/description tương ứng.
- `HistoryScreen`, `RewardsScreen`, `StorageService` thống kê theo 5 nhóm.
- `BoundingBoxOverlay` hiển thị nhãn gốc (12 lớp) + màu theo nhóm.

## 4. Lợi ích

- ✅ Không còn “other” chung chung – người dùng biết pin thuộc loại “Nguy hại”, quần áo thuộc “Tái sử dụng”.
- ✅ Vẫn giữ chi tiết 12 nhãn để hiển thị và lưu lịch sử.
- ✅ Chuẩn bị tốt cho các chiến dịch giáo dục phân loại rác (hữu cơ, tái chế, nguy hại, tái sử dụng, rác còn lại).

## 5. Checklist triển khai

1. Cập nhật `backend/api.py` (mapping mới + trả `class_group`).
2. Đồng bộ docs: `LABEL_MAPPING.md`, `CLASS_MAPPING_EXPLAINED.md`, `DISPLAY_LABELS.md`.
3. Mobile:
   - `src/types/index.ts`
   - `src/utils/binMapping.ts`
   - `src/components/BoundingBoxOverlay.tsx`
   - `src/screens/HistoryScreen.tsx`, `RewardsScreen.tsx`
   - `src/services/StorageService.ts`

4. Test nhanh:
   - Kiểm tra API trả về đúng `class_group`.
   - Bắn vài ảnh mẫu để đảm bảo UI lên đúng màu/icon.
   - Lưu history và xem thống kê theo nhóm mới.

## 6. Hướng mở rộng

- Nếu muốn chi tiết hơn, có thể chia nhỏ `recyclable` thành nhựa/kim loại/giấy/thủy tinh hoặc thêm nhóm `electronic`.
- Có thể dùng dữ liệu thống kê mới để gợi ý chương trình thưởng riêng cho từng nhóm.

> TL;DR: Giữ 12 nhãn Moondream cho UI, nhưng chuẩn hóa thành 5 nhóm xử lý lớn để hướng dẫn người dùng và thống kê rõ ràng hơn.*** End Patch

