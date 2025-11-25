# Test với Confidence Threshold Thấp

## Vấn đề
Model không detect được vật thể với confidence threshold 0.55 (55%).

## Giải pháp tạm thời
Đã giảm `MIN_CONFIDENCE` xuống **0.3 (30%)** để test.

## Cách test

1. **Restart backend:**
   ```bash
   cd backend
   # Dừng server hiện tại (Ctrl+C)
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test trên web app:**
   - Refresh trang web
   - Đưa vật thể vào camera
   - Kiểm tra xem có detections không

## Nếu vẫn không detect

Có thể do:
1. **Model không được train cho loại vật thể này**
   - Model chỉ detect: battery, biological, brown-glass, cardboard, clothes, green-glass, metal, paper, plastic, shoes, trash, white-glass
   - Cốc nhựa có thể không được train đủ

2. **Vật thể quá nhỏ hoặc không rõ**
   - Đảm bảo vật thể chiếm phần lớn khung hình
   - Đủ ánh sáng
   - Không bị che khuất

3. **Cần test với vật thể khác:**
   - Chai nhựa rõ ràng
   - Lon kim loại
   - Giấy/bìa carton
   - Quần áo

## Nếu detect được nhưng có nhiều false positives

Tăng lại confidence threshold:
```python
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.4"))  # hoặc 0.5
```

## Kiểm tra model classes

Kiểm tra xem model có class nào:
```bash
curl http://localhost:8000/health
```

Xem `class_names` để biết model detect được những gì.

