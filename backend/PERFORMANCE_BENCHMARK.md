# Performance Benchmark - Delay Analysis

## Delay 53-70ms: Có mượt không?

### Đánh giá

| Delay | Đánh giá | Trải nghiệm |
|-------|----------|-------------|
| **< 30ms** | ⭐⭐⭐⭐⭐ Rất mượt | Gần như realtime, không cảm nhận delay |
| **30-50ms** | ⭐⭐⭐⭐ Mượt | Tốt, delay nhẹ, chấp nhận được |
| **50-70ms** | ⭐⭐⭐ Chấp nhận được | Có delay nhẹ, vẫn dùng được |
| **70-100ms** | ⭐⭐ Hơi chậm | Delay rõ rệt, ảnh hưởng trải nghiệm |
| **> 100ms** | ⭐ Rất chậm | Delay lớn, không mượt |

### Với Frame Rate 5 FPS (200ms interval)

- **Delay 53-70ms**: Chiếm **26-35%** của frame interval
- **Còn lại**: 130-147ms cho network, rendering, etc.
- **Kết luận**: ✅ **Chấp nhận được**, nhưng chưa mượt lắm

### So sánh với các ứng dụng khác

| Ứng dụng | Delay | Ghi chú |
|----------|-------|---------|
| **Realtime video call** | 50-150ms | End-to-end latency |
| **Gaming (60 FPS)** | 16ms | Mỗi frame |
| **AR/VR** | < 20ms | Cần rất mượt |
| **Object detection (YOLO)** | 30-100ms | Tùy model size |

## Cách tối ưu để giảm delay

### 1. Giảm Image Size (Đã làm)

```python
# Backend: imgsz=416
results = model(image_bgr, conf=MIN_CONFIDENCE, imgsz=416)
```

```typescript
// Web: maxWidth=416
const maxWidth = 416;
```

**Kết quả**: Giảm từ 100ms → 50-70ms ✅

### 2. Giảm Frame Rate

```python
# Backend: REALTIME_MAX_FPS=3 (thay vì 5)
REALTIME_MAX_FPS = float(os.getenv("REALTIME_MAX_FPS", "3"))
```

**Kết quả**: Ít frame hơn → ít processing → mượt hơn

### 3. Dùng Model nhỏ hơn

- **YOLOv8n (nano)**: ~30-50ms ✅ (hiện tại)
- **YOLOv8s (small)**: ~50-80ms
- **YOLOv8m (medium)**: ~80-120ms

### 4. Tối ưu Image Processing

```typescript
// Web: Giảm JPEG quality
const base64 = scaledCanvas.toDataURL('image/jpeg', 0.7); // 0.7 thay vì 0.8
```

### 5. Disable Material Classification (Đã làm)

- **CLIP**: 100-500ms ❌
- **Heuristics**: 1-5ms ✅

## Khuyến nghị

### Cho Realtime Detection (5 FPS):

- ✅ **Delay 50-70ms**: **Chấp nhận được**
- ⚠️ Nếu muốn mượt hơn: Giảm xuống **< 50ms**

### Cách đạt < 50ms:

1. **Giảm image size xuống 320:**
   ```python
   results = model(image_bgr, conf=MIN_CONFIDENCE, imgsz=320)
   ```

2. **Giảm frame rate xuống 3 FPS:**
   ```python
   REALTIME_MAX_FPS = 3
   ```

3. **Tối ưu web app:**
   ```typescript
   const maxWidth = 320; // Thay vì 640
   const base64 = scaledCanvas.toDataURL('image/jpeg', 0.6); // Lower quality
   ```

## Kết luận

**Delay 53-70ms:**
- ✅ **Chấp nhận được** cho realtime detection
- ⚠️ **Chưa mượt lắm** - có thể cảm nhận delay nhẹ
- 💡 **Có thể tối ưu thêm** để đạt < 50ms nếu cần

**Nếu muốn mượt hơn:** Giảm image size xuống 320 và frame rate xuống 3 FPS.

