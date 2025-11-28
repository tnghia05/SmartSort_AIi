# THUẬT TOÁN - TÓM TẮT CHO PRESENTATION
## 2-3 Thuật toán chính (1-2 phút trình bày)

---

## 🎯 3 THUẬT TOÁN CHÍNH

### 1. **YOLOv8 - Object Detection** ⭐ Core Algorithm

**Mô tả**: Deep Learning model phát hiện và phân loại vật thể trong ảnh

**Cách hoạt động**:
- Input: Ảnh RGB (640x640 pixels)
- Model: YOLOv8 (You Only Look Once version 8)
- Output: 
  - Bounding boxes (vị trí vật thể)
  - Class labels (Glass, Metal, Paper, Plastic, Waste)
  - Confidence scores (0.0 - 1.0)

**Tại sao chọn YOLOv8?**
- ✅ State-of-the-art object detection
- ✅ Real-time performance (30+ FPS với GPU)
- ✅ Phát hiện nhiều vật thể cùng lúc trong 1 lần quét
- ✅ Cân bằng tốt giữa tốc độ và độ chính xác

**Đặc điểm kỹ thuật**:
- Single-stage detector (1 lần forward pass)
- Anchor-free architecture
- Trained trên waste classification dataset

---

### 2. **Non-Maximum Suppression (NMS)** - Loại bỏ trùng lặp

**Vấn đề**: Model có thể phát hiện cùng 1 vật thể nhiều lần với các bounding box khác nhau

**Giải pháp - Thuật toán NMS**:
```
1. Tính IoU (Intersection over Union) giữa các bounding boxes
2. Nếu IoU > 0.4 → Coi như trùng lặp
3. Giữ lại box có confidence cao nhất
4. Loại bỏ các box còn lại
```

**Công thức IoU**:
```
IoU = Diện tích giao nhau / Diện tích hợp
```

**Kết quả**: 
- ✅ Loại bỏ duplicates
- ✅ Chỉ giữ detection tốt nhất cho mỗi vật thể
- ✅ Tăng độ chính xác và giảm false positives

---

### 3. **Image Preprocessing** - Tăng cường chất lượng ảnh

#### a) CLAHE (Contrast Limited Adaptive Histogram Equalization)

**Mục đích**: Tăng cường độ tương phản để model nhận diện tốt hơn

**Cách hoạt động**:
- Chia ảnh thành grid 8x8
- Tăng cường tương phản từng vùng riêng biệt
- Giới hạn tăng cường để tránh over-enhancement

**Lợi ích**: 
- ✅ Cải thiện nhận diện trong điều kiện ánh sáng không đều
- ✅ Adaptive: Mỗi vùng được xử lý riêng

#### b) Bilateral Filter

**Mục đích**: Làm mịn nhiễu nhưng giữ lại edges (biên)

**Cách hoạt động**:
- Làm mịn dựa trên cả khoảng cách không gian và độ khác biệt màu sắc
- Giữ lại các edges quan trọng

**Lợi ích**:
- ✅ Giảm noise mà không làm mất chi tiết
- ✅ Tốt hơn Gaussian Blur thông thường

---

## 🔄 PIPELINE ĐƠN GIẢN

```
1. Ảnh Input
   ↓
2. Image Preprocessing
   - CLAHE (tăng tương phản)
   - Bilateral Filter (làm mịn)
   ↓
3. YOLOv8 Inference
   - Phát hiện vật thể
   - Phân loại class
   ↓
4. Non-Maximum Suppression
   - Loại bỏ duplicates
   - Giữ detection tốt nhất
   ↓
5. Output: Detections + Guidance
```

---

## 📊 METRICS QUAN TRỌNG

- **Tốc độ**: 30+ FPS (GPU), 10-15 FPS (CPU)
- **Độ chính xác**: Confidence threshold = 0.6
- **IoU Threshold**: 0.4 (để merge duplicates)
- **Max detections**: 8 objects/frame

---

## 💡 ĐIỂM NỔI BẬT

1. **YOLOv8**: Model deep learning hiện đại, phát hiện real-time
2. **NMS**: Đảm bảo mỗi vật thể chỉ có 1 detection tốt nhất
3. **Preprocessing**: Tăng chất lượng ảnh → tăng độ chính xác

---

## 🎤 SCRIPT TRÌNH BÀY (1-2 phút)

**Slide: Thuật toán**

"Về phần thuật toán, chúng em sử dụng 3 thuật toán chính:

**Thứ nhất là YOLOv8** - một model deep learning state-of-the-art cho object detection. Model này có thể phát hiện nhiều vật thể cùng lúc trong thời gian thực với tốc độ 30+ FPS. YOLOv8 được train trên dataset chuyên về phân loại rác thải với 5 classes: Glass, Metal, Paper, Plastic, và Waste.

**Thứ hai là Non-Maximum Suppression** - một kỹ thuật post-processing để loại bỏ các detection trùng lặp. Vấn đề là model có thể phát hiện cùng 1 vật thể nhiều lần với các bounding box khác nhau. Chúng em tính IoU - Intersection over Union - giữa các boxes, và nếu IoU lớn hơn 0.4, chúng em coi như trùng lặp và chỉ giữ lại box có confidence cao nhất.

**Thứ ba là Image Preprocessing** - trước khi đưa vào model, chúng em áp dụng CLAHE để tăng cường độ tương phản và Bilateral Filter để làm mịn nhiễu mà vẫn giữ lại các chi tiết quan trọng. Điều này giúp model nhận diện tốt hơn, đặc biệt trong điều kiện ánh sáng không đều.

Kết quả là một hệ thống vừa nhanh, vừa chính xác, có thể xử lý real-time trên video stream."

---

**Tài liệu này là bản tóm tắt ngắn gọn, phù hợp để trình bày trong presentation.**

