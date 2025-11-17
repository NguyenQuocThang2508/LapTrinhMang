# 🎮 HƯỚNG DẪN CHẠY GAME MULTIPLAYER

## ✅ KIỂM TRA TRƯỚC KHI CHẠY

- ✅ Python 3.12.6 đã được cài đặt
- ✅ Dependencies đã được cài đặt (pygame, numpy)

## 🚀 CÁCH CHẠY GAME

### **CÁCH 1: Dùng file batch (Đơn giản nhất - Windows)**

1. **Double-click vào file:** `start_game.bat` hoặc `start_game_with_audio.bat`
   - File này sẽ tự động khởi động server và client
   - Khi được hỏi "Bật âm thanh?", nhập `Y` để bật hoặc `n` để tắt

### **CÁCH 2: Chạy thủ công (2 terminal)**

#### **Bước 1: Khởi động Server**

Mở Terminal 1 và chạy:
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer"
python -m server.main
```

Bạn sẽ thấy thông báo server đã sẵn sàng chờ kết nối.

#### **Bước 2: Khởi động Client**

Mở Terminal 2 mới và chạy:
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer"
python -m client.main
```

Khi chạy client, bạn sẽ được hỏi:
- **Bật âm thanh? (Y/n):** Nhập `Y` để bật hoặc `n` để tắt
- **Tên player:** Nhập tên của bạn
- **Room ID:** Nhập ID phòng (hoặc Enter để dùng mặc định)
- **Chọn điều khiển (1-4):** Chọn loại điều khiển
- **Bật chế độ 2 người 1 màn hình? (y/N):** Nhập `y` nếu muốn hoặc `N` để bỏ qua

## 🎮 ĐIỀU KHIỂN TRONG GAME

- **W/S** hoặc **↑/↓**: Di chuyển lên/xuống
- **A/D** hoặc **←/→**: Di chuyển trái/phải
- **Shift**: Chạy nhanh (dash)
- **ESC**: Thoát game

## 📝 LƯU Ý QUAN TRỌNG

1. ✅ **Phải chạy SERVER trước**, sau đó mới chạy CLIENT
2. ✅ Có thể mở nhiều client để chơi multiplayer
3. ✅ Đảm bảo bạn đang ở đúng thư mục: `D:/LTM/LTM/LTM/game_multiplayer`
4. ✅ Lệnh đúng: `python -m server.main` và `python -m client.main`

## 🔧 NẾU GẶP LỖI

### Lỗi "ModuleNotFoundError"
- Đảm bảo bạn đang ở đúng thư mục `game_multiplayer`
- Sử dụng lệnh: `python -m server.main` (không phải `python server/main.py`)

### Lỗi thiếu dependencies
Chạy lệnh cài đặt:
```bash
pip install -r requirements.txt
```

### Kiểm tra âm thanh
Chạy script test:
```bash
python test_audio.py
```

## 🎯 CHẠY NHANH (Copy & Paste)

**Terminal 1 - Server:**
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer" && python -m server.main
```

**Terminal 2 - Client:**
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer" && python -m client.main
```

---

**Chúc bạn chơi game vui vẻ! 🎮**

