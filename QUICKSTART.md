# Quick Start Guide


### Automated Installation

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
- Install Boost libraries 1.74+
- Install Python 3.11+ and pip
- Create a Python virtual environment (`venv`)
- Install Python dependencies
- Compile the C++ GPS logger
- Create necessary directories (`logs/`, `data/`)


## Step 3: UART Configuration for Pi 5

Raspberry Pi 5 requires specific UART setup for the GPS HAT:

1.  **Disable Bluetooth on Primary UART**

    Edit the boot configuration:

    ```bash
    sudo nano /boot/firmware/config.txt
    ```

    Add this line at the end:

    ```
    dtoverlay=disable-bt
    ```

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

5.  **Add User to dialout Group**

    Allow your user to access serial ports without sudo:

    ```bash
    sudo usermod -a -G dialout $USER
    ```

   Reboot


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

# Run from project root
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
