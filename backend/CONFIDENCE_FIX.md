# Fix Confidence Threshold - Giảm False Positives

## Vấn đề

Model đang detect sai với confidence thấp:
- Cốc (cup) bị detect là "Giấy (Bìa carton)" với confidence 44% và 36%
- Confidence threshold quá thấp (25%) → cho phép nhiều false positives

## Giải pháp

### 1. Tăng Confidence Threshold

**Trước:**
- `conf=0.25` (25%) trong model inference
- `min_confidence = 0.25` (25%) trong filter

**Sau:**
- `conf=0.5` (50%) trong model inference
- `min_confidence = 0.5` (50%) trong filter

### 2. Logic hiển thị cho Cardboard

Chỉ hiển thị "Giấy (Bìa carton)" khi:
- Confidence >= 50%
- Nếu confidence thấp → chỉ hiển thị "Giấy" để tránh nhầm lẫn

## Kết quả mong đợi

### Trước:
- ❌ Cốc → "Giấy (Bìa carton)" 44% (false positive)
- ❌ Cốc → "Giấy (Bìa carton)" 36% (false positive)

### Sau:
- ✅ Cốc → Không detect (vì confidence < 50%)
- ✅ Hoặc detect đúng class (nếu model có class "cup" hoặc "other")

## Files Changed

1. `backend/api.py`:
   - Tăng `conf=0.25` → `conf=0.5` trong model inference
   - Tăng `min_confidence = 0.25` → `min_confidence = 0.5` trong filter
   - Apply cho cả `/detect`, `/detect-base64`, và `/detect-batch`

2. `mobile/src/components/BoundingBoxOverlay.tsx`:
   - Chỉ hiển thị "Giấy (Bìa carton)" khi confidence >= 50%
   - Nếu confidence thấp → chỉ hiển thị "Giấy"

## Trade-off

### Ưu điểm:
- ✅ Giảm false positives
- ✅ Chỉ hiển thị detections có độ tin cậy cao
- ✅ Trải nghiệm người dùng tốt hơn

### Nhược điểm:
- ⚠️ Có thể bỏ sót một số detections với confidence 30-50%
- ⚠️ Cần model tốt hơn để có confidence cao hơn

## Next Steps

1. ✅ Code đã được update
2. ⏳ Restart backend để apply changes
3. ⏳ Test lại trên app
4. 🔄 Nếu vẫn có false positives → có thể tăng lên 0.6 (60%) hoặc 0.7 (70%)

## Alternative Solutions

Nếu vẫn có vấn đề:

1. **Tăng confidence threshold lên 60-70%**
   ```python
   conf=0.6  # hoặc 0.7
   min_confidence = 0.6  # hoặc 0.7
   ```

2. **Filter theo class**
   - Loại bỏ một số classes dễ nhầm lẫn
   - Ví dụ: Nếu detect "cardboard" với confidence < 60% → ignore

3. **Improve model**
   - Fine-tune model với dataset tốt hơn
   - Sử dụng model lớn hơn (YOLOv8m, YOLOv8l thay vì YOLOv8n)

4. **Post-processing**
   - Filter detections dựa trên kích thước bounding box
   - Filter dựa trên tỷ lệ khung hình (aspect ratio)
   - Non-maximum suppression (NMS) để loại bỏ duplicates

## Testing

Sau khi restart backend:

1. Test với cốc:
   - Trước: Detect "Giấy (Bìa carton)" 44%, 36%
   - Sau: Không detect hoặc detect đúng class

2. Test với rác thực tế:
   - Chai nhựa → "Nhựa" với confidence > 50%
   - Lon kim loại → "Kim loại" với confidence > 50%
   - Giấy → "Giấy" với confidence > 50%

3. Test với bìa carton thật:
   - Bìa carton → "Giấy (Bìa carton)" với confidence > 50%

