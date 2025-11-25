# Dataset Template

## Cấu trúc thư mục

Dataset cần có cấu trúc như sau:

```
dataset/
├── images/
│   ├── train/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── ...
│   └── val/
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── image1.txt
│   │   ├── image2.txt
│   │   └── ...
│   └── val/
│       ├── image1.txt
│       ├── image2.txt
│       └── ...
└── data.yaml
```

## YOLO Annotation Format

Mỗi file `.txt` tương ứng với một ảnh, chứa các dòng annotation:

```
class_id center_x center_y width height
```

Ví dụ:
```
0 0.5 0.5 0.3 0.4
8 0.2 0.3 0.15 0.2
```

Trong đó:
- `class_id`: ID của class (0-11)
- `center_x, center_y`: Tọa độ center của bounding box (normalized 0-1)
- `width, height`: Kích thước bounding box (normalized 0-1)

## Class IDs

| ID | Class Name |
|----|------------|
| 0  | battery |
| 1  | biological |
| 2  | brown-glass |
| 3  | cardboard |
| 4  | clothes |
| 5  | green-glass |
| 6  | metal |
| 7  | paper |
| 8  | plastic |
| 9  | shoes |
| 10 | trash |
| 11 | white-glass |

## Sử dụng

1. Copy `data.yaml` vào thư mục dataset của bạn
2. Update `path` trong `data.yaml` nếu cần
3. Đảm bảo cấu trúc thư mục đúng
4. Sử dụng `prepare_dataset.py` để validate

## Tools

- `prepare_dataset.py`: Validate và prepare dataset
- `download_dataset.py`: Download dataset từ các nguồn

