# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# ADDED: android-tools-adb (Crucial for connecting to the emulator)
RUN apt-get update && apt-get install -y \
    build-essential \
    sqlite3 \
    android-tools-adb \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code AND the static folder
COPY . .

# ADDED: Create the entrypoint script dynamically to ensure it exists and has permissions
# This script tries to connect to the host emulator before starting the app
RUN echo '#!/bin/bash\n\
echo "🔗 Attempting to connect to Host Emulator..."\n\
adb connect host.docker.internal:5555\n\
echo "🚀 Starting CampusSync..."\n\
exec uvicorn main:app --host 0.0.0.0 --port 8000' > entrypoint.sh

# Make the script executable
RUN chmod +x entrypoint.sh

# Expose the port FastAPI runs on
EXPOSE 8000

# CHANGED: Use the script to start the app
CMD ["./entrypoint.sh"]