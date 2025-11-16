# Hướng Dẫn Cài Đặt Game Multiplayer

## Yêu Cầu
- Python 3.7+
- pip (thường đi kèm với Python)

## Cài Đặt Nhanh

### Windows:
1. Double-click `SETUP.bat` để cài đặt tự động
2. Sau đó double-click `start_game_with_audio.bat` để chạy game

### Linux/Mac/Git Bash:
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file âm thanh
python create_sounds.py

# Chạy server (terminal 1)
python -m server.main

# Chạy client (terminal 2)
python -m client.main
```

## Cấu Trúc Thư Mục
```
game_multiplayer/
├── client/          # Code client
├── server/          # Code server
├── shared/          # Code dùng chung
├── requirements.txt # Dependencies
├── SETUP.bat        # Script cài đặt (Windows)
└── start_game_with_audio.bat  # Script chạy game (Windows)
```

## Lệnh Chạy Game

### Chạy Server:
```bash
python -m server.main
```

### Chạy Client:
```bash
python -m client.main
```

### Kiểm Tra Âm Thanh:
```bash
python test_audio.py
```

### Tạo Lại File Âm Thanh:
```bash
python create_sounds.py
```

## Xử Lý Lỗi

### Lỗi "No module named pygame"
```bash
pip install pygame
```

### Lỗi "Address already in use"
- Đổi port trong `server/src/config.py` hoặc `client/src/config.py`

### Lỗi "Connection refused"
- Kiểm tra server đã chạy chưa
- Kiểm tra firewall
- Kiểm tra SERVER_IP trong config

## Chơi Multiplayer Trên Mạng LAN

1. Tìm IP máy server:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` hoặc `ip addr`

2. Sửa `client/src/config.py`:
   ```python
   SERVER_IP = "192.168.x.x"  # IP của máy server
   ```

3. Đảm bảo firewall cho phép port 5000

## Điều Khiển Trong Game
- **W/S** hoặc **↑/↓**: Di chuyển lên/xuống
- **A/D** hoặc **←/→**: Di chuyển trái/phải
- **Shift**: Chạy nhanh (dash)
- **ESC**: Thoát game

