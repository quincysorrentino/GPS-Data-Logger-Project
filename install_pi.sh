#!/bin/bash

echo "=========================================="
echo "GPS Data Logger - Raspberry Pi Installer"
echo "=========================================="

# Update system
echo "[INFO] Updating system..."
sudo apt-get update

# Install build tools and CMake
echo "[INFO] Installing build tools..."
sudo apt-get install -y build-essential cmake git

# Install Boost libraries
echo "[INFO] Installing Boost libraries..."
sudo apt-get install -y libboost-all-dev

# Install Python dependencies for dashboard
echo "[INFO] Installing Python dependencies..."
sudo apt-get install -y python3-pip python3-venv

# Create virtual environment
echo "[INFO] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install Python packages
echo "[INFO] Installing Python packages..."
pip install -r requirements.txt

# Build C++ Logger
echo "[INFO] Building C++ GPS Logger..."
rm -rf build
mkdir -p build
cd build
cmake ..
make

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo "To run the logger:"
echo "  ./build/gps_logger_boost /dev/serial0"
echo ""
echo "To run the dashboard:"
echo "  source venv/bin/activate"
echo "  python dashboard.py"
echo "=========================================="
