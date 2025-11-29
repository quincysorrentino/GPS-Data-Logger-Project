# GPS-Data-Logger-Project

## Overview

A high-precision GPS tracking system with real-time visualization, data logging, and professional-grade monitoring. Built on Raspberry Pi 5 with Adafruit Ultimate GPS HAT, featuring a C++ logger with async serial I/O using Boost.Asio, and a web dashboard with interactive mapping.

**Key Capabilities:**

- Sub-second real-time position tracking with 0.5s dashboard updates
- High-performance C++ logger
- NMEA 0183 protocol parser with checksum validation
- Interactive web dashboard with toggleable overlays (speed heatmap, path trails, statistics)

## Demo

### Real-Time Dashboard in Action

<img src="https://media.githubusercontent.com/media/quincysorrentino/GPS-Data-Logger-Project/main/assets/demo.gif" alt="Dashboard Demo" />

#### Dashboard Satellite View

![Dashboard Satellite View](assets/dashboard_sat.png)

#### Dashboard OpenStreetMap View

![Dashboard OpenStreetMap View](assets/dashboard_opensat.png)

> **Live GPS tracking system** featuring sub-second updates, multiple map base layers (Dark Matter, OpenStreetMap, Satellite), and dynamic overlays for speed analysis and route visualization.

**Dashboard Features:**

**Interactive Control Panel (Top Left):**

- **Toggleable Overlays**: Click checkboxes to show/hide features
  - Path Trail: Real-time GPS route
  - Speed Graph: Live speed-over-time chart
  - Speed Heatmap: Color-coded dots showing velocity (purple=slow, orange=medium, red=fast)
  - Trip Statistics: Detailed metrics panel

### Key Technical Features

- **Asynchronous Data Acquisition**: Boost.Asio for non-blocking serial I/O
- **NMEA Protocol Parser**: Custom implementation with checksum validation
- **Multiple Map Layers**: Dark Matter (default), OpenStreetMap, Satellite imagery
- **Real-time Overlays**: Toggleable path trails, speed graphs, and heatmaps

---

## Hardware

### System Overview

#### Complete System

<img src="assets\full.jpg" alt="Complete System" width="500" />

#### Raspberry Pi with GPS HAT

<img src="assets\pi.jpg" alt="Raspberry Pi with GPS HAT" width="500" />

#### External GPS Antenna

<img src="assets\antenna.jpg" alt="External GPS Antenna" width="500" />

### Bill of Materials

| Component                     | Specification                      | Purpose                               | Link                                              |
| ----------------------------- | ---------------------------------- | ------------------------------------- | ------------------------------------------------- |
| **Raspberry Pi 5**            | 4GB RAM, BCM2712 quad-core         | Main computing platform               | [Adafruit](https://www.adafruit.com/product/5812) |
| **Adafruit Ultimate GPS HAT** | PA1616S chipset, 99 channels       | GPS receiver with UART interface      | [Adafruit](https://www.adafruit.com/product/2324) |
| **External GPS Antenna**      | 28dB gain, 5m cable, SMA connector | Active antenna for improved reception | [Adafruit](https://www.adafruit.com/product/960)  |
| **MicroSD Card**              | 32GB Class 10                      | OS and data storage                   | -                                                 |
| **Power Supply**              | 5V 3A USB-C                        | Raspberry Pi power                    | -                                                 |

### Technical Specifications

**GPS Module (PA1616S):**

- **Sensitivity**: -165 dBm
- **Accuracy**: ±3 meters horizontal
- **Channels**: 99 acquisition channels (66 tracking)
- **Satellite Systems**: GPS + GLONASS + Galileo
- **Communication**: UART serial @ 9600 baud, NMEA 0183 protocol

**Raspberry Pi Integration:**

- **Interface**: Hardware UART on GPIO 14/15 (pins 8/10)
- **Device Path**: `/dev/serial0` (primary UART)
- **Power Consumption**: ~150mA @ 3.3V
- **PPS Output**: GPIO 4

### System Architecture

```
GPS Satellites
    ↓ (L1 1575.42 MHz)
External Active Antenna (28dB amplification)
    ↓ (SMA cable)
GPS HAT Module (PA1616S chipset)
    ↓ (UART @ 9600 baud - NMEA sentences)
Raspberry Pi 5 (GPIO pins 8/10)
    ↓ (Serial read /dev/ttyAMA0)
C++ Logger (Boost.Asio async I/O)
    ↓ (CSV file write)
Data Files (logs/ directory)
    ↓ (File polling every 0.5s)
Python Dashboard (Plotly Dash)
    ↓ (HTTP @ port 8050)
Web Browser Visualization
```

### Hardware Integration

**Physical Assembly:**

- GPS HAT mounted on 40-pin GPIO header with UART alignment (TX/RX pins 8/10)
- External antenna connected via uFL connector
- Powered by 5V 3A USB-C supply
- CR1220 coin cell battery for RTC backup

### Communication Protocol

**NMEA 0183 Sentences Parsed:**

- `$GPGGA` / `$GNGGA`: Position fix data, altitude, satellites
- `$GPRMC` / `$GNRMC`: Velocity, course, timestamp
- `$GPGSA` / `$GNGSA`: DOP values, fix quality
- `$GPGSV` / `$GNGSV`: Satellite visibility data

**Data Flow:**

1. GPS module outputs NMEA sentences at 9600 baud
2. C++ logger reads serial stream asynchronously
3. Parser validates checksums and extracts fields
4. Data written to timestamped CSV files
5. Dashboard polls latest CSV and updates UI

## Technical Stack

**Languages & Frameworks:**

- C++11 with Boost.Asio (async I/O, cross-platform serial communication)
- Python 3 with Plotly Dash (web framework), Dash-Leaflet (mapping), pandas (data processing)

**Protocols & Standards:**

- NMEA 0183 (GPS data sentences: GGA, RMC, GSA, GSV)
- UART serial @ 9600 baud
- CSV data logging format
- HTTP web server (port 8050)

## Additional Resources

### Official Documentation

- [Adafruit GPS HAT Guide](https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi)
- [NMEA 0183 Protocol Specification](https://www.nmea.org/content/STANDARDS/NMEA_0183_Standard)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [Plotly Dash Documentation](https://dash.plotly.com/)
- [Dash-Leaflet Documentation](https://www.dash-leaflet.com/)
- [CMake Documentation](https://cmake.org/documentation/)

### Python Libraries

- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Dash Documentation](https://dash.plotly.com/)
- [Dash-Leaflet Documentation](https://www.dash-leaflet.com/)

### C++ Resources

- [C++ Serial Communication](https://en.cppreference.com/w/)
- [Windows Serial Port API](https://learn.microsoft.com/en-us/windows/win32/devio/communications-resources)
- [Linux termios Serial Programming](https://man7.org/linux/man-pages/man3/termios.3.html)

### GPS Technology

- [GPS.gov - Official U.S. Government GPS Information](https://www.gps.gov/)
- [GPS Accuracy Factors and Limitations](https://www.gps.gov/systems/gps/performance/accuracy/)
- [Understanding HDOP and GPS Accuracy](<https://en.wikipedia.org/wiki/Dilution_of_precision_(navigation)>)
