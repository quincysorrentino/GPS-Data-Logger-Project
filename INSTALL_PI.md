# Raspberry Pi 5 Installation & Setup Guide

Complete setup instructions for running the GPS Data Logger and Dashboard on Raspberry Pi 5 with Adafruit Ultimate GPS HAT.

## Prerequisites

- **Hardware**: Raspberry Pi 5 (4GB or 8GB RAM)
- **OS**: Raspberry Pi OS Bookworm (64-bit)
- **GPS Hardware**: Adafruit Ultimate GPS HAT (PA1616S chipset)
- **External GPS Antenna**: 28dB active antenna (recommended for reliable fixes)
- **Power Supply**: 5V 3A USB-C power adapter
- **Internet Connection**: Required for downloading dependencies

## Step 1: Hardware Assembly

### Physical Setup

1. **Mount the GPS HAT** onto the Raspberry Pi 5's 40-pin GPIO header

   - Align pins carefully and press down firmly
   - The HAT should sit flush with the Pi

2. **Connect the External Antenna**

   - Attach the active GPS antenna to the uFL connector on the GPS HAT
   - Route the antenna cable away from power supplies to minimize interference
   - Position antenna with clear sky view (outdoors or near a window)

3. **Insert the Backup Battery**

   - Place a CR1220 coin cell battery in the holder on the GPS HAT
   - This maintains the RTC for faster warm starts (5 seconds vs 30 seconds)

4. **Power Connection**
   - Connect the 5V 3A USB-C power supply to the Raspberry Pi 5
   - The GPS HAT draws power directly from the GPIO header (3.3V rail)

### UART Configuration on Pi 5

The Pi 5 uses different UART configurations than earlier models:

- **Primary UART**: `/dev/ttyAMA0` (default for GPIO 14/15)
- **Serial Symlink**: `/dev/serial0` points to the primary UART
- The GPS HAT uses GPIO pins 8 (TX) and 10 (RX) for UART communication

## Step 2: Software Installation

### Transfer Project Files

<<<<<<< HEAD
**Option A: Git Clone (Recommended)**
Open a terminal on your Raspberry Pi 5 and run:
=======
**Git Clone**
Open a terminal on your Raspberry Pi and run:
>>>>>>> 5674c54b8315238f3aef59b8926b64d193560e18

```bash
git clone https://github.com/quincysorrentino/GPS-Data-Logger-Project.git
cd GPS-Data-Logger-Project
```

<<<<<<< HEAD
**Option B: File Transfer (SCP/SFTP)**
If you have the files on your computer, you can copy them over. Ensure you copy the following files:

- `gps_logger_boost.cpp`
- `dashboard.py`
- `gps_stream_simulator.py`
- `CMakeLists.txt`
- `requirements.txt`
- `install_pi.sh`

### Automated Installation

We provide an automated script optimized for Raspberry Pi 5 and Bookworm OS:

=======
## Step 2: Installation

>>>>>>> 5674c54b8315238f3aef59b8926b64d193560e18
1.  **Make the script executable:**

    ```bash
    chmod +x install_pi.sh
    ```

2.  **Run the installer:**
    ```bash
    ./install_pi.sh
    ```

This script will:

- Update system packages (apt-get update/upgrade)
- Install C++ build tools: GCC 12+, CMake 3.25+
- Install Boost libraries 1.74+ (required for Boost.Asio)
- Install Python 3.11+ and pip
- Create a Python virtual environment (`venv`)
- Install Python dependencies: plotly, dash, dash-leaflet, pandas
- Compile the C++ GPS logger with optimizations for ARM64
- Create necessary directories (`logs/`, `data/`)

<<<<<<< HEAD
### Manual Installation (Alternative Method)

If the automated script fails or you prefer manual control:

1.  **Install System Dependencies:**

    ```bash
    sudo apt-get update
    sudo apt-get upgrade -y
    sudo apt-get install -y build-essential cmake libboost-all-dev python3-venv python3-pip git
    ```

2.  **Set up Python Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

3.  **Build C++ Logger:**
    ```bash
    mkdir -p build
    cd build
    cmake ..
    make -j4
    cd ..
    ```
=======
>>>>>>> 5674c54b8315238f3aef59b8926b64d193560e18

## Step 3: UART Configuration for Pi 5

Raspberry Pi 5 requires specific UART setup for the GPS HAT:

1.  **Disable Bluetooth on Primary UART (Recommended)**

    Edit the boot configuration:

    ```bash
    sudo nano /boot/firmware/config.txt
    ```

    Add this line at the end:

    ```
    dtoverlay=disable-bt
    ```

    Save and exit (Ctrl+X, Y, Enter).

2.  **Enable Serial Hardware**

    Run the Raspberry Pi configuration tool:

    ```bash
    sudo raspi-config
    ```

    Navigate to:

    - **3 Interface Options**
    - **I6 Serial Port**
    - "Would you like a login shell to be accessible over serial?" → **No**
    - "Would you like the serial port hardware to be enabled?" → **Yes**
    - Exit and reboot

3.  **Reboot the System**

    ```bash
    sudo reboot
    ```

4.  **Verify UART Access**

    After rebooting, check that the serial port exists:

    ```bash
    ls -l /dev/serial0
    ls -l /dev/ttyAMA0
    ```

    Both should exist. `/dev/serial0` should be a symlink to `/dev/ttyAMA0`.

5.  **Add User to dialout Group**

    Allow your user to access serial ports without sudo:

    ```bash
    sudo usermod -a -G dialout $USER
    ```

    Logout and login again (or reboot) for this to take effect.

## Step 4: GPS Hardware Verification

Before running the logger, verify the GPS is communicating:

1.  **Check for NMEA Data**

    ```bash
    cat /dev/serial0
    ```

    You should see lines like:

    ```
    $GPGGA,123456.00,4307.1234,N,08901.5678,W,1,08,1.2,258.5,M,,,*4F
    $GPRMC,123456.00,A,4307.1234,N,08901.5678,W,0.0,0.0,250125,,,A*7E
    ```

    Press `Ctrl+C` to stop.

2.  **Wait for GPS Fix**

    - **Cold start**: Up to 30 minutes (no battery backup, no almanac data)
    - **Warm start**: 5-30 seconds (with CR1220 battery installed)
    - The red LED on the GPS HAT blinks once every 15 seconds when a fix is acquired
    - Position the antenna outdoors or near a window with clear sky view

3.  **Troubleshooting No Data**

    If you see nothing:

    - Check HAT is properly seated on GPIO pins
    - Verify antenna connection to uFL connector
    - Ensure serial port is enabled in raspi-config
    - Check user is in dialout group: `groups $USER`

## Step 5: Running the System

### Start the C++ GPS Logger

Run the logger in the background to capture GPS data:

```bash
sudo ./build/gps_logger_boost /dev/serial0
```

Expected output:

```
Opening serial port: /dev/serial0
Serial port opened successfully
Waiting for GPS fix...
GPS fix acquired! Logging started.
Position: 43.0712°N, 89.4012°W | Altitude: 258.5m | Speed: 0.0 km/h
```

**To run in the background:**

```bash
nohup sudo ./build/gps_logger_boost /dev/serial0 > gps_logger.log 2>&1 &
```

Or use `tmux`/`screen` for persistent sessions.

### Start the Python Dashboard

Open a new terminal or SSH session:

```bash
cd GPS-Data-Logger-Project
source venv/bin/activate
python dashboard.py
```

Expected output:

```
Dash is running on http://0.0.0.0:8050/
```

### Access the Dashboard

**On the Pi itself:**

- Open Chromium browser
- Navigate to: `http://localhost:8050`

**From another device on the same network:**

- Find your Pi's IP address: `hostname -I`
- Navigate to: `http://<pi-ip-address>:8050`
  - Example: `http://192.168.1.100:8050`

### Dashboard Features

- **Real-time map** showing GPS position updates every 0.5 seconds
- **Telemetry panel** with speed, coordinates, altitude, heading, satellites
- **Toggleable overlays**: Path trails, speed heatmap, speed graph, trip statistics
- **Map layers**: Dark Matter (default), OpenStreetMap, Satellite imagery

## System Performance on Pi 5

Expected resource usage:

- **C++ Logger**: 2-5% CPU, 2MB RAM
- **Python Dashboard**: 10-15% CPU, 50MB RAM
- **Total System Load**: <20% CPU usage on Pi 5's quad-core BCM2712
- **Update Latency**: <100ms (logger), <500ms (dashboard refresh)

## Troubleshooting

### Serial Port Issues

**"Permission denied" error when accessing /dev/serial0:**

```bash
sudo usermod -a -G dialout $USER
# Then logout and login again
```

**Serial port doesn't exist:**

- Check UART is enabled in raspi-config
- Verify `/boot/firmware/config.txt` has `dtoverlay=disable-bt`
- Reboot after making changes

**No NMEA data visible:**

- Ensure GPS HAT is firmly seated on GPIO header
- Check antenna is connected to uFL connector
- Try `sudo cat /dev/ttyAMA0` instead of `/dev/serial0`

### GPS Fix Issues

**No GPS fix after 30+ minutes:**

- Move antenna outdoors with clear sky view
- Check antenna cable isn't damaged
- Verify red LED on GPS HAT is present (indicates power)
- Active antenna requires power from GPS module - check connection

**Slow/intermittent fixes:**

- Install CR1220 battery for RTC backup
- Keep antenna away from metal objects and power supplies
- Urban environments with tall buildings cause multipath interference
- Check HDOP value in dashboard - lower is better (<2.0 ideal)

### Dashboard Issues

**Dashboard not updating:**

- Verify C++ logger is running: `ps aux | grep gps_logger`
- Check CSV files are being created: `ls -lt logs/`
- Ensure logger shows "GPS fix acquired!" message
- Verify Python dashboard is polling the correct logs directory

**Cannot access dashboard from another device:**

- Find Pi's IP: `hostname -I`
- Check firewall isn't blocking port 8050: `sudo ufw status`
- Ensure both devices are on same network
- Try accessing from Pi locally first: `http://localhost:8050`

**Dashboard crashes/freezes:**

- Check available RAM: `free -h`
- Close other applications
- Reduce dashboard refresh rate in `dashboard.py`

### Build/Compilation Issues

**CMake errors:**

- Ensure CMake version ≥ 3.25: `cmake --version`
- Update if needed: `sudo apt-get install cmake`

**Boost library not found:**

```bash
sudo apt-get install libboost-all-dev
```

**Compiler errors:**

- Verify GCC version ≥ 12: `gcc --version`
- Update if needed: `sudo apt-get install build-essential`

### Performance Issues

**High CPU usage:**

- Check for runaway processes: `top`
- Reduce GPS update rate (edit baud rate to 4800)
- Increase dashboard refresh interval

**System overheating:**

- Raspberry Pi 5 requires active cooling for sustained loads
- Install heatsink or fan
- Monitor temperature: `vcgencmd measure_temp`

## Auto-Start on Boot (Optional)

To run the GPS logger automatically on startup:

1. **Create systemd service:**

```bash
sudo nano /etc/systemd/system/gps-logger.service
```

2. **Add this content:**

```ini
[Unit]
Description=GPS Data Logger
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/GPS-Data-Logger-Project
ExecStart=/home/pi/GPS-Data-Logger-Project/build/gps_logger_boost /dev/serial0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

3. **Enable and start:**

```bash
sudo systemctl enable gps-logger.service
sudo systemctl start gps-logger.service
sudo systemctl status gps-logger.service
```

## Additional Resources

- [Adafruit GPS HAT Documentation](https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi)
- [Raspberry Pi 5 GPIO Pinout](https://pinout.xyz/)
- [NMEA 0183 Protocol Specification](https://www.nmea.org/content/STANDARDS/NMEA_0183_Standard)
- [Boost.Asio Documentation](https://www.boost.org/doc/libs/release/doc/html/boost_asio.html)
