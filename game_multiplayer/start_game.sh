#!/bin/bash
# Script chạy game với âm thanh (cho Git Bash/WSL)

echo "========================================"
echo "  KHỞI ĐỘNG GAME MULTIPLAYER"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "[1/2] Đang khởi động Server..."
python -m server.main &
SERVER_PID=$!
sleep 2

echo "[2/2] Đang khởi động Client..."
echo ""
echo "✓ Khi được hỏi 'Bật âm thanh?', nhập Y để bật âm thanh"
echo ""

python -m client.main

# Dừng server khi client thoát
kill $SERVER_PID 2>/dev/null

