<!-- 4d741c6b-1e1e-44e5-9daf-c952b1bf370a 49d61be6-8efe-42bb-b338-149311c81d30 -->
# Kế Hoạch Tích Hợp Dataset Moondream

## Chuyển đổi Dataset

1. download-convert

- Viết script `backend/scripts/convert_moondream_to_yolo.py` để xuất ảnh + nhãn thành cấu trúc `dataset_moondream/` chuẩn YOLO.
- Thêm mapping từ các class của dataset (`packet`, `FoodPackaging`, …) sang 12 loại rác của app; class không map thì đưa vào `other`.

2. prepare-data

- Chạy `prepare_dataset.py` với thư mục mới để kiểm tra cấu trúc, tạo `data.yaml` và ghi lại thống kê vào `NEXT_STEPS_AFTER_DOWNLOAD.md`.

## Cập nhật Backend

3. train-upload

- Train YOLOv8 bằng dataset mới (tận dụng `train_waste_model_colab.ipynb`), xuất model tốt nhất vào `backend/models/best.pt`.

4. backend-config

- Điều chỉnh `backend/api.py` nếu mapping class/threshold cần cập nhật; bổ sung log thông tin dataset mới.

5. docs-backend

- Bổ sung hướng dẫn trong `TRAIN_MODEL_COLAB.md` / `TRAIN_QUICK_START.md` về quy trình dùng dataset Moondream.

## Thay đổi trên Mobile

6. mobile-config

- Kiểm tra `mobile/src/config/api.ts` (nếu endpoint thay đổi) và đảm bảo `DetectionService` xử lý đúng nhãn mới.

7. ui-labels

- Cập nhật `mobile/src/components/BoundingBoxOverlay.tsx`, `mobile/src/utils/binMapping.ts`, `CameraScreen`, `HistoryScreen` để hiển thị đúng tên/mô tả class đã map.

8. regression-checks

- Chạy test backend (`test_api.py`) và build Expo để đảm bảo kết quả detection hiển thị đúng với model mới.