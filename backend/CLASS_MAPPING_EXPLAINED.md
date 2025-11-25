# Giải thích Class Mapping - Moondream → Nhóm xử lý lớn

## 1. Model Moondream có 12 nhãn gốc

`battery`, `biological`, `brown-glass`, `cardboard`, `clothes`, `green-glass`, `metal`, `paper`, `plastic`, `shoes`, `trash`, `white-glass`.

Các nhãn này được giữ nguyên khi trả về cho mobile để hiển thị chính xác (Pin, Thủy tinh nâu, Giày dép, ...).

## 2. Nhóm xử lý lớn (TrashType mới)

Để hướng dẫn người dùng xử lý đúng quy trình và tránh "other", ta gom 12 nhãn vào 5 nhóm:

| Nhóm | Ý nghĩa | Ví dụ |
|------|---------|-------|
| `organic` | Rác hữu cơ/sinh học | biological |
| `recyclable` | Có thể tái chế (nhựa/kim loại/giấy/thủy tinh) | plastic, paper, metal, glass |
| `hazardous` | Chất thải nguy hại cần xử lý riêng | battery |
| `reusable` | Có thể tái sử dụng/quyên góp | clothes, shoes |
| `residual` | Rác còn lại/hỗn hợp | trash |

## 3. Bảng mapping chi tiết

| Nhãn Moondream | Nhóm xử lý | Ghi chú |
|----------------|-----------|--------|
| battery | hazardous | Thu gom pin/ắc quy riêng |
| biological | organic | Thực phẩm, rác hữu cơ |
| brown-glass / green-glass / white-glass | recyclable | Thủy tinh tái chế |
| cardboard / paper | recyclable | Giấy, bìa carton |
| plastic | recyclable | Chai nhựa, bao bì |
| metal | recyclable | Lon, sắt/thép |
| clothes / shoes | reusable | Có thể quyên góp/tái chế dệt may |
| trash | residual | Rác hỗn hợp khó tái chế |

## 4. Payload API

```json
{
  "class": "brown-glass",     // nhãn gốc 12 lớp
  "class_group": "recyclable",// nhóm xử lý để chỉ thùng/khuyến nghị
  "confidence": 0.82,
  "bbox": { ... }
}
```

- `class` dùng để hiển thị chi tiết (ví dụ “Thủy tinh nâu”)
- `class_group` dùng để lấy màu thùng rác, thống kê lịch sử, tính điểm
- `class_original` giữ để tương thích (giá trị = `class`)

## 5. Mobile side

- `TrashType` (trong `src/types/index.ts`) = union của 5 nhóm trên.
- `BIN_MAPPING` cung cấp màu/icon/hướng dẫn cho từng nhóm.
- `HistoryScreen`, `RewardsScreen`, `StorageService` đếm số lần theo nhóm lớn.

## 6. Lý do lựa chọn

- ✅ Không còn category "other" chung chung.
- ✅ Người dùng hiểu rõ pin thuộc nhóm “Nguy hại”, quần áo thuộc “Tái sử dụng”, v.v.
- ✅ Vẫn giữ được thông tin chi tiết 12 nhãn gốc cho UI và analytics.
- ✅ Dễ mở rộng: chỉ cần thêm entry trong bảng là xong.

## 7. Nếu cần mở rộng thêm

- Có thể tách `recyclable` thành các nhóm con (nhựa, kim loại, giấy, thủy tinh) nếu muốn hệ thống thùng riêng biệt.
- Có thể bổ sung `electronic` hay `biohazard` nếu dataset mới có thêm nhãn đặc thù.

Nhưng với 5 nhóm trên, app đã bao phủ được toàn bộ Moondream dataset mà vẫn giữ UX rõ ràng.*** End Patch

