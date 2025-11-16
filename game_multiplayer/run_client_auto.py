"""Script tự động chạy client với input mặc định"""
import subprocess
import sys
import os

# Thay đổi sang thư mục game
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Input tự động: Y (bật âm thanh), Enter (tên mặc định), Enter (room mặc định), 4 (tất cả điều khiển), n (không 2 người)
inputs = "Y\n\n\n4\nn\n"

print("=" * 50)
print("ĐANG KHỞI ĐỘNG CLIENT...")
print("=" * 50)
print("Cài đặt tự động:")
print("  - Bật âm thanh: CÓ")
print("  - Tên player: player1 (mặc định)")
print("  - Room ID: default (mặc định)")
print("  - Điều khiển: Tất cả (4)")
print("  - Chế độ 2 người: KHÔNG")
print("=" * 50)
print()

# Chạy client với input tự động
process = subprocess.Popen(
    [sys.executable, "-m", "client.main"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Gửi input
process.stdin.write(inputs)
process.stdin.flush()
process.stdin.close()

# Hiển thị output
for line in process.stdout:
    print(line, end='')

process.wait()

