# Checklist Test Model - Trước khi quyết định Train

## ✅ Bước 1: Restart Backend

### 1. Stop backend hiện tại (nếu đang chạy)
- Nhấn `Ctrl+C` trong terminal backend

### 2. Start backend mới
```bash
cd backend
python api.py
```

### 3. Kiểm tra log
Bạn sẽ thấy:
```
Trying to load model: models/best.pt
✅ Model loaded successfully: models/best.pt

============================================================
Model loaded successfully!
============================================================
Model classes: ['battery', 'biological', 'brown-glass', ...]
Total classes: 12
SUCCESS: This is a waste classification model!
Class mapping:
  - biological           -> organic
  - plastic              -> plastic
  - metal                -> metal
  - paper                -> paper
  - cardboard            -> paper
  ...
============================================================

INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test API health
```bash
curl http://localhost:8000/health
```

Response phải có:
```json
{
  "status": "ok",
  "model_loaded": true,
  "class_names": ["battery", "biological", ...],
  "total_classes": 12,
  "is_waste_model": true
}
```

## ✅ Bước 2: Test trên App

### 1. Reload app trên device
- Shake device → Reload
- Hoặc restart Expo Go

### 2. Mở camera screen
- Đảm bảo đang ở mode "Detection"
- Bật realtime detection (nút Play ▶️)

### 3. Test với các loại rác thật

#### Test 1: Chai nhựa
- **Vật thể**: Chai nhựa (PET, HDPE, etc.)
- **Kỳ vọng**: 
  - ✅ Detect "Nhựa" (plastic)
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 2: Lon kim loại
- **Vật thể**: Lon nhôm, lon sắt (Coca-Cola, Bia, etc.)
- **Kỳ vọng**: 
  - ✅ Detect "Kim loại" (metal)
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 3: Giấy
- **Vật thể**: Giấy A4, sách, báo
- **Kỳ vọng**: 
  - ✅ Detect "Giấy" (paper)
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 4: Bìa carton
- **Vật thể**: Hộp carton, thùng carton
- **Kỳ vọng**: 
  - ✅ Detect "Giấy (Bìa carton)" hoặc "Giấy"
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 5: Rác hữu cơ
- **Vật thể**: Rác thực phẩm, rau củ quả
- **Kỳ vọng**: 
  - ✅ Detect "Hữu cơ" (organic)
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 6: Pin
- **Vật thể**: Pin AA, AAA, pin điện thoại
- **Kỳ vọng**: 
  - ✅ Detect "Pin" (battery)
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 7: Thủy tinh
- **Vật thể**: Chai thủy tinh, ly thủy tinh
- **Kỳ vọng**: 
  - ✅ Detect "Thủy tinh" (glass)
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 8: False Positive Test - Cốc
- **Vật thể**: Cốc (ceramic, plastic, glass)
- **Kỳ vọng**: 
  - ✅ Không detect hoặc detect đúng class
  - ❌ Không detect sai thành "Giấy (Bìa carton)" với confidence thấp
  - ✅ Nếu detect, confidence phải >= 50%
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 9: Quần áo
- **Vật thể**: Quần áo, vải
- **Kỳ vọng**: 
  - ✅ Detect "Quần áo" (clothes)
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

#### Test 10: Giày dép
- **Vật thể**: Giày, dép
- **Kỳ vọng**: 
  - ✅ Detect "Giày dép" (shoes)
  - ✅ Confidence >= 50%
  - ✅ Bounding box đúng vị trí
- **Kết quả**: [ ] Pass / [ ] Fail
- **Ghi chú**: ________________

## ✅ Bước 3: Đánh giá kết quả

### Đếm kết quả
- **Tổng số test**: 10
- **Pass**: _____ / 10
- **Fail**: _____ / 10
- **Tỷ lệ thành công**: _____%

### Phân tích

#### Nếu Pass >= 8/10 (80%+):
- ✅ **Không cần train**
- ✅ Model hoạt động tốt
- ✅ Chỉ cần điều chỉnh threshold nếu cần
- **Hành động**: Giữ nguyên model hiện tại

#### Nếu Pass 5-7/10 (50-70%):
- ⚠️ **Cân nhắc fine-tune**
- ⚠️ Model hoạt động tốt nhưng có thể cải thiện
- **Hành động**: 
  - Xem xét fine-tune nếu có dataset
  - Hoặc điều chỉnh threshold
  - Hoặc cải thiện điều kiện test (ánh sáng, góc chụp)

#### Nếu Pass < 5/10 (< 50%):
- ❌ **Cần train/fine-tune**
- ❌ Model không đủ tốt
- **Hành động**: 
  - Fine-tune với dataset riêng
  - Hoặc train lại model
  - Xem `backend/TRAIN_MODEL_COLAB.md`

## ✅ Bước 4: Ghi chú các vấn đề

### Vấn đề gặp phải:
1. ________________
2. ________________
3. ________________

### False positives:
- Vật thể nào bị detect sai?
- Confidence bao nhiêu?
- Detect thành class nào?

### False negatives:
- Vật thể nào không được detect?
- Có hiển thị gì không?
- Confidence bao nhiêu nếu có?

### Vấn đề kỹ thuật:
- App có crash không?
- API có lỗi không?
- Performance có chậm không?

## ✅ Bước 5: Quyết định

### Option 1: Giữ nguyên model
- **Lý do**: Pass >= 8/10
- **Hành động**: Không làm gì thêm

### Option 2: Điều chỉnh threshold
- **Lý do**: Có false positives hoặc false negatives
- **Hành động**: 
  - Tăng threshold nếu có false positives
  - Giảm threshold nếu có false negatives
  - Test lại

### Option 3: Fine-tune model
- **Lý do**: Pass 5-7/10 hoặc cần cải thiện
- **Hành động**: 
  - Thu thập dataset (100-500 ảnh)
  - Fine-tune trên Google Colab
  - Test lại

### Option 4: Train lại model
- **Lý do**: Pass < 5/10
- **Hành động**: 
  - Thu thập dataset lớn (1000+ ảnh)
  - Train trên Google Colab
  - Test lại

## 📝 Lưu ý khi test

### Điều kiện test tốt:
- ✅ Ánh sáng đủ
- ✅ Vật thể rõ ràng
- ✅ Nền đơn giản
- ✅ Vật thể chiếm đủ diện tích trong frame
- ✅ Camera ổn định (không rung)

### Điều kiện test khó:
- ⚠️ Ánh sáng yếu
- ⚠️ Nền phức tạp
- ⚠️ Vật thể nhỏ
- ⚠️ Camera rung
- ⚠️ Nhiều vật thể trong frame

### Tips:
- Test nhiều lần với cùng một vật thể
- Test với nhiều góc chụp khác nhau
- Test với nhiều điều kiện ánh sáng
- Ghi chú lại confidence scores
- Chụp screenshot để so sánh

## 🎯 Kết quả mong đợi

### Tốt nhất:
- ✅ Detect đúng 90%+ các loại rác
- ✅ Confidence >= 50% cho hầu hết detections
- ✅ Không có false positives với confidence cao
- ✅ Bounding box chính xác

### Chấp nhận được:
- ✅ Detect đúng 80%+ các loại rác
- ✅ Confidence >= 50% cho hầu hết detections
- ✅ Ít false positives
- ✅ Bounding box tương đối chính xác

### Cần cải thiện:
- ⚠️ Detect đúng < 80% các loại rác
- ⚠️ Nhiều false positives
- ⚠️ Confidence thấp
- ⚠️ Bounding box không chính xác

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra backend log
2. Kiểm tra app console log
3. Test API trực tiếp
4. Xem `backend/CONFIDENCE_FIX.md`
5. Xem `backend/SHOULD_RETRAIN.md`

## 🔄 Next Steps

Sau khi test xong:
1. Điền kết quả vào checklist này
2. Quyết định có cần train không
3. Nếu cần train → Xem `backend/TRAIN_MODEL_COLAB.md`
4. Nếu không cần → Giữ nguyên model hiện tại

