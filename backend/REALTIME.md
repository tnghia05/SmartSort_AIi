# Realtime Detection Streaming

## WebSocket Endpoint

- URL: `ws://<HOST>:8000/ws/detect`
- Client gửi JSON dạng:

```json
{
  "image": "<base64 JPEG hoặc PNG>",
  "format": "base64"
}
```

- Server phản hồi các message:
  - `{"type":"ready","min_confidence":0.55,"max_fps":5}` ngay sau khi kết nối thành công.
  - `{"type":"detections","timestamp":..., "detections":[...], "count":N}` cho mỗi frame hợp lệ.
  - `{"type":"error","message":"..."} / {"type":"warning","message":"..."}` khi có lỗi hoặc timeout.

## Biến môi trường

| Tên | Mô tả | Mặc định |
| --- | --- | --- |
| `REALTIME_MAX_FPS` | Giới hạn số frame/giây xử lý per client | `5` |
| `REALTIME_CLIENT_TIMEOUT` | Timeout (giây) nếu không nhận frame nào | `10` |
| `MIN_CONFIDENCE` | Ngưỡng confidence tối thiểu dùng cho cả REST & WS | `0.55` |

## Định dạng `detections`

```json
{
  "bbox": {"x1":0.1,"y1":0.2,"x2":0.4,"y2":0.6},
  "bbox_pixels": {"x1":120,"y1":240,"x2":480,"y2":640},
  "class": "clothes",
  "class_group": "reusable",
  "class_original": "plastic",
  "confidence": 0.78
}
```

## Quy trình gợi ý cho client

1. Mở socket, chờ message `type=ready` để biết các thông số.
2. Gửi khung hình đã base64 (nên resize ~640px để giảm tải).
3. Nhận `type=detections`, cập nhật UI overlay.
4. Nếu socket bị đóng/timeout, fallback sang REST `/detect-base64` hoặc thử reconnect sau vài giây.

