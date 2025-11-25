# Hướng dẫn cài đặt CLIP cho Material Classification

## Vị trí cài đặt

**Cài đặt trong thư mục `backend`** vì CLIP là dependency của backend Python.

## Cách 1: Cài đặt trực tiếp (Khuyến nghị)

```bash
# Di chuyển vào thư mục backend
cd backend

# Cài đặt PyTorch (nếu chưa có)
# CPU only:
pip install torch torchvision

# Hoặc với CUDA (nếu có GPU):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Cài đặt CLIP
pip install git+https://github.com/openai/CLIP.git
```

## Cách 2: Cài đặt từ requirements.txt

Nếu muốn thêm vào `requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
pip install git+https://github.com/openai/CLIP.git
```

**Lưu ý:** CLIP không thể thêm trực tiếp vào `requirements.txt` vì nó cần install từ Git repository.

## Kiểm tra cài đặt

```bash
cd backend
python -c "import clip; print('✅ CLIP installed successfully')"
```

Nếu thành công, bạn sẽ thấy:
```
✅ CLIP installed successfully
```

## Nếu không cài CLIP

Hệ thống vẫn hoạt động bình thường với **heuristics-based material classification** (phân tích màu sắc, độ trong suốt, edges).

## Troubleshooting

### Lỗi: "pip: command not found"
- Đảm bảo Python và pip đã được cài đặt
- Thử: `python -m pip install ...`

### Lỗi: "torch not found"
- Cài đặt PyTorch trước: `pip install torch torchvision`

### Lỗi: "git not found"
- Cài đặt Git: https://git-scm.com/downloads
- Hoặc download CLIP source code và cài thủ công

### Lỗi khi import CLIP
- Kiểm tra Python version (cần >= 3.7)
- Thử reinstall: `pip uninstall clip-by-openai && pip install git+https://github.com/openai/CLIP.git`

