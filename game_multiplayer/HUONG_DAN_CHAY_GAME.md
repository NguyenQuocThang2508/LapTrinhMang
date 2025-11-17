# 🎮 HƯỚNG DẪN CHẠY GAME MULTIPLAYER - ĐẦY ĐỦ

## ✅ BƯỚC 1: KIỂM TRA YÊU CẦU

### **Python đã cài đặt:**
```bash
python --version
```
Cần Python 3.8 trở lên (đã có Python 3.12.6 ✓)

### **Dependencies đã cài đặt:**
```bash
python -c "import pygame; import numpy; print('✓ OK')"
```

Nếu thiếu, cài đặt:
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer"
pip install -r requirements.txt
```

## 🚀 BƯỚC 2: CHẠY GAME

### **CÁCH 1: Dùng file batch (Đơn giản nhất - Windows)**

**Double-click vào:**
- `start_game.bat` - Chạy cả server và client
- `start_server.bat` - Chỉ chạy server
- `start_client.bat` - Chỉ chạy client

### **CÁCH 2: Chạy thủ công (2 terminal)**

#### **Terminal 1 - Server (Git Bash):**
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer"
export PYTHONPATH=.
python -m server.main
```

**Hoặc Windows CMD:**
```cmd
cd "D:\LTM\LTM\LTM\game_multiplayer"
set PYTHONPATH=%CD%
python -m server.main
```

**Kết quả mong đợi:**
```
Server listening on 0.0.0.0:5000
```

**⚠️ ĐỂ NGUYÊN TERMINAL NÀY, ĐỪNG ĐÓNG!**

---

#### **Terminal 2 - Client (Mở terminal mới):**

**Git Bash:**
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer"
export PYTHONPATH=.
python -m client.main
```

**Windows CMD:**
```cmd
cd "D:\LTM\LTM\LTM\game_multiplayer"
set PYTHONPATH=%CD%
python -m client.main
```

## 📝 BƯỚC 3: NHẬP THÔNG TIN KHI CLIENT CHẠY

Khi chạy client, bạn sẽ được hỏi:

1. **Bật âm thanh? (Y/n):** 
   - Nhập `Y` để bật hoặc `n` để tắt (khuyến nghị `n` để test nhanh)

2. **Tên player:** 
   - Nhập tên bất kỳ (ví dụ: `Player1`)

3. **Room ID:** 
   - **Nhấn Enter** để dùng `default` (khuyến nghị)
   - Hoặc nhập tên room khác

4. **Chọn điều khiển (1-4):** 
   - Nhập `4` để dùng tất cả (WASD + Mũi tên + Numpad)

5. **Bật chế độ 2 người 1 màn hình? (y/N):** 
   - Nhập `N` để chơi đơn (khuyến nghị cho lần đầu)
   - Hoặc `y` nếu muốn 2 người cùng màn hình

## 🎮 BƯỚC 4: CHƠI GAME

### **Điều khiển:**
- **W/A/S/D** hoặc **↑/↓/←/→**: Di chuyển
- **Shift**: Chạy nhanh (dash)
- **ESC**: Thoát game

### **Mục tiêu:**
- Di chuyển đến vùng đích màu xanh lá (góc trên bên phải)
- Tránh obstacles (hình chữ nhật nâu)
- Nhặt power-up (vật vàng) để tăng tốc
- Đạt điểm cao nhất!

## 🧪 BƯỚC 5: TEST CÁC TÍNH NĂNG MỚI

### ✅ **1. Hệ thống Điểm số**
- Đi đến goal (màu xanh lá) → +10 điểm
- Điểm hiển thị dưới tên player (màu vàng)

### ✅ **2. Leaderboard Top 3**
- Mở thêm 1-2 client để có nhiều player
- Leaderboard ở góc trên bên phải
- Top 1: Vàng, Top 2: Bạc, Top 3: Đồng

### ✅ **3. Power-up System**
- Power-up màu vàng spawn mỗi 10 giây
- Di chuyển đến để nhặt
- Tăng tốc 2x trong 5 giây

### ✅ **4. Respawn Cooldown**
- Chạm obstacles để chết
- Phải đợi 3 giây mới respawn
- Không thể di chuyển trong thời gian cooldown

### ✅ **5. Collision Detection**
- Không thể đi xuyên qua obstacles
- Collision chính xác hơn

## ⚠️ XỬ LÝ LỖI

### **Lỗi: `ModuleNotFoundError: No module named 'server'`**

**Giải pháp:** Set PYTHONPATH trước khi chạy:
```bash
export PYTHONPATH=.  # Git Bash
set PYTHONPATH=%CD%  # Windows CMD
```

### **Lỗi: `[WinError 10054] An existing connection was forcibly closed`**

**Giải pháp:**
1. Kiểm tra server có đang chạy không
2. Khởi động lại server
3. Dùng Room ID là `default` (nhấn Enter)

### **Lỗi: `Address already in use`**

**Giải pháp:** Port 5000 đang bị chiếm
```bash
# Tìm process đang dùng port 5000
netstat -ano | findstr :5000
# Hoặc đơn giản: Đợi vài giây rồi thử lại
```

### **Server không nhận kết nối**

**Kiểm tra:**
1. Server có in "Server listening on 0.0.0.0:5000" không?
2. Firewall có chặn không?
3. IP và Port đúng không? (127.0.0.1:5000)

## 📋 TÓM TẮT NHANH

### **Chạy Server:**
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer"
export PYTHONPATH=.
python -m server.main
```

### **Chạy Client (terminal mới):**
```bash
cd "D:/LTM/LTM/LTM/game_multiplayer"
export PYTHONPATH=.
python -m client.main
```

### **Khi được hỏi:**
- Bật âm thanh? → `n`
- Tên player → `Player1`
- Room ID → **Enter** (default)
- Điều khiển → `4`
- 2 người? → `N`

## 🎯 LƯU Ý QUAN TRỌNG

1. ✅ **Luôn chạy SERVER trước**, sau đó mới chạy CLIENT
2. ✅ **Giữ terminal server mở** trong khi chơi
3. ✅ **Set PYTHONPATH** trước khi chạy (hoặc dùng file batch)
4. ✅ **Dùng Room ID `default`** để tránh lỗi
5. ✅ **Có thể mở nhiều client** để chơi multiplayer

## 🔗 THÔNG TIN BỔ SUNG

- **Repository:** https://github.com/NguyenQuocThang2508/LapTrinhMang
- **Branch:** `develop`
- **Port:** 5000
- **IP:** 127.0.0.1 (localhost)

---

**Chúc bạn chơi game vui vẻ! 🎮**
