# Raspberry Pi Installation & Setup Guide

This guide provides detailed instructions for setting up the GPS Data Logger and Dashboard on a Raspberry Pi.

## Prerequisites

- **Hardware**: Raspberry Pi 3, 4, or 5.
- **OS**: Raspberry Pi OS (64-bit recommended).
- **GPS Hardware**: Adafruit Ultimate GPS HAT (or compatible UART GPS module).
- **Internet Connection**: Required for downloading dependencies.

## Step 1: Transfer Files to Raspberry Pi

You can either clone the repository directly on the Pi or transfer the files from your computer.

**Option A: Git Clone (Recommended)**
Open a terminal on your Raspberry Pi and run:

```bash
git clone <your-repo-url>
cd GPS-Data-Logger-Project
```

**Option B: File Transfer (SCP/SFTP)**
If you have the files on your computer, you can copy them over. Ensure you copy the following files:

- `gps_logger_boost.cpp`
- `dashboard.py`
- `gps_stream_simulator.py`
- `CMakeLists.txt`
- `requirements.txt`
- `install_pi.sh`

## Step 2: Installation

We have provided an automated script to handle all dependencies and building.

1.  **Make the script executable:**

    ```bash
    chmod +x install_pi.sh
    ```

2.  **Run the installer:**
    ```bash
    ./install_pi.sh
    ```

This script will:

- Update your system packages.
- Install C++ compilers (GCC, CMake) and Boost libraries.
- Install Python 3 and pip.
- Create a Python virtual environment (`venv`).
- Install the required Python libraries for the dashboard.
- Compile the C++ GPS logger.

### Manual Installation (If the script fails)

If you prefer to install manually, follow these steps:

1.  **Install System Dependencies:**

    ```bash
    sudo apt-get update
    sudo apt-get install -y build-essential cmake libboost-all-dev python3-venv
    ```

2.  **Set up Python Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Build C++ Logger:**
    ```bash
    mkdir -p build
    cd build
    cmake ..
    make
    cd ..
    ```

## Step 3: Hardware Configuration

1.  **Enable Serial Port:**

    - Run `sudo raspi-config`
    - Go to **Interface Options** -> **Serial Port**.
    - **Login shell**: Select **No**.
    - **Serial hardware**: Select **Yes**.
    - Reboot the Pi: `sudo reboot`.

2.  **Verify GPS Connection:**
    - The GPS HAT usually communicates over `/dev/serial0`.
    - You can check if raw data is coming in:
      ```bash
      cat /dev/serial0
      ```
      You should see lines starting with `$GP...` or `$GN...`. Press `Ctrl+C` to stop.

## Step 4: Running the System

### 1. Start the GPS Logger

This runs in the background to capture data.

```bash
./build/gps_logger_boost /dev/serial0
```

_Leave this terminal open, or run it in a multiplexer like `tmux` or `screen`._

### 2. Start the Dashboard

Open a new terminal window.

```bash
source venv/bin/activate
python dashboard.py
```

### 3. Access the Dashboard

Open the Chromium browser on the Raspberry Pi and go to:
`http://localhost:8050`

If accessing from another computer on the same network, use the Pi's IP address:
`http://<raspberry-pi-ip>:8050`

## Troubleshooting

- **Permission Denied for Serial Port**:
  If you get an error opening `/dev/serial0`, add your user to the dialout group:

  ```bash
  sudo usermod -a -G dialout $USER
  ```

  Then logout and login again.

- **No GPS Fix**:

  - Ensure the antenna has a clear view of the sky.
  - It may take up to 30 minutes for a "cold start" fix.
  - Check the red LED on the GPS HAT: it blinks once every 15 seconds when a fix is found.

- **Dashboard not updating**:
  - Ensure the C++ logger is running and printing "GPS fix acquired!".
  - Check that CSV files are being created in the `logs/` folder.
