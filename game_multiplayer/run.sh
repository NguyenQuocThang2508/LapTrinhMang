#!/usr/bin/env bash
# Simple runner for development. Run from repository root.

# Start server in background
python server/main.py &
SERVER_PID=$!

echo "Server started (PID=$SERVER_PID)"

echo "You can start a client in another terminal: python client/main.py"

echo "To stop server: kill $SERVER_PID"
