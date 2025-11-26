# Quick Start Guide

## Running the GPS Logger on Raspberry Pi

# Build the C++ logger
mkdir -p build
cd build
cmake ..
make -j4
cd ..
```

### Running the Logger

```bash
# Stop any services using the GPS serial port
sudo systemctl stop gpsd.socket
sudo systemctl stop gpsd
sudo killall gpsd 2>/dev/null

# Run from project root (so logs/ directory is found)
cd ~/Projects/GPS-Data-Logger-Project
./build/bin/gps_logger_boost /dev/ttyAMA0
```

### Running the Dashboard

Open a second terminal:

```bash
cd ~/Projects/GPS-Data-Logger-Project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python dashboard.py
```

Access dashboard at: `http://<raspberry-pi-ip>:8050`