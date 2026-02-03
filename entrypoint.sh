#!/bin/bash

# 1. Start the internal ADB server
adb start-server

# 2. Try to connect to the Emulator running on your Laptop (Host)
# 'host.docker.internal' is a special DNS name that points to your Windows machine
echo "🔗 Attempting to bridge to Host Emulator..."
adb connect host.docker.internal:5555

# 3. Start the FastAPI Server
echo "🚀 Starting CampusSync..."
exec uvicorn main:app --host 0.0.0.0 --port 8000