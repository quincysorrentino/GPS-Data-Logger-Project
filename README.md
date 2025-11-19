# GPS-Data-Logger-Project

## Overview

This project is a complete high-precision GPS tracking system featuring real-time visualization, data logging, and professional-grade monitoring capabilities. Built on a Raspberry Pi 5 with Adafruit Ultimate GPS HAT, the system captures and displays location, speed, altitude, and timing information with a modern web-based dashboard. This type of system is fundamental to flight data recorders, vehicle telemetry systems, autonomous navigation, and real-time tracking applications used in aerospace, defense, and industrial monitoring.

## Motivation

Modern GPS tracking systems combine hardware data acquisition with real-time visualization dashboards for telemetry monitoring. From aircraft black boxes and vehicle fleet tracking to autonomous systems navigation, understanding how to capture, display, and analyze GPS data in real-time is essential for aerospace, autonomous systems, and defense technology. This project demonstrates the complete pipeline from sensor hardware to professional web-based visualization, mirroring systems used in safety-critical industrial applications.

## Project Goals

- ✅ Build a functional GPS data logger from hardware components
- ✅ Interface with GPS modules and parse NMEA data formats
- ✅ Implement efficient data logging to handle continuous sensor streams
- ✅ Create real-time web dashboard with industrial-grade visualization
- ✅ Develop minimalist dark-mode UI with professional telemetry display
- ✅ Implement GPS stream simulation for testing and development
- ✅ Analyze logged data to calculate statistics and visualize tracks
- ✅ Understand GPS limitations and accuracy factors

## Hardware Components

### Core Components

- **Raspberry Pi 5 (4GB RAM)** - Main computing platform
- **Adafruit Ultimate GPS HAT** - GPS receiver module with built-in RTC
- **External Active GPS Antenna (28dB, 5m SMA)** - Improves signal reception
- **SMA to uFL Adapter Cable** - Connects antenna to GPS HAT
- **32GB microSD Card** - Operating system and data storage
- **CR1220 Coin Cell Battery** - Powers RTC for faster satellite acquisition

### Power and Accessories

- **27W USB-C Power Supply** - Desktop operation
- **USB-C Power Bank** - Portable field operation
- **Micro HDMI to HDMI Cable** - Initial setup and debugging
- **M2.5 Standoffs** - Secure HAT mounting

## Technical Specifications

### GPS Module Capabilities

- Sensitivity: -165 dBm
- Update rate: 10 Hz (configurable down to 1 Hz for power savings)
- Channels: 99 search channels
- Systems: GPS + GLONASS support
- Accuracy: ~3 meters horizontal (typical with clear sky view)
- Time to first fix: ~30 seconds (warm start with RTC battery)

### Communication Protocol

The GPS module communicates via UART serial at 9600 baud using NMEA 0183 format. Key NMEA sentences include:

- GPGGA: Position fix data
- GPRMC: Recommended minimum navigation information
- GPGSA: GPS DOP and active satellites
- GPGSV: Satellites in view

## System Architecture

The GPS tracking system integrates hardware data acquisition with real-time web-based visualization:

### 1. Hardware Data Acquisition Layer

The GPS HAT mounts directly onto the Raspberry Pi's 40-pin GPIO header, using hardware UART (pins 8 and 10) for GPS communication and GPIO pin 4 for PPS (Pulse Per Second) signal. The external 28dB active antenna connects via uFL connector on the HAT.

### 2. Data Processing Pipeline

**GPS Logger (`gps_logger.py`)**

- Reads NMEA sentences from `/dev/serial0` at 9600 baud
- Parses GGA (position/altitude) and RMC (speed/course) sentences using pynmea2
- Extracts fields: latitude, longitude, altitude, speed (knots and km/h), course, satellites, HDOP, fix quality
- Professional logging module with configurable levels
- Writes timestamped CSV files with data integrity (immediate flush)
- Handles missing data with appropriate defaults

### 3. Real-Time Visualization Layer

**Web Dashboard (`dashboard.py`)**

- Plotly Dash web application on port 8050
- Dash-Leaflet interactive mapping
- Dark mode minimalist UI with industrial design
- Updates every 0.5 seconds for real-time tracking
- Displays last 100 GPS positions with fixed origin marker
- Stats panel with speed, coordinates (6 decimal precision), altitude, course, satellites
- Pulsing cyan beacon for current position
- Map tiles: Esri World Street Map

### 4. Testing and Simulation

**GPS Stream Simulator (`gps_stream_simulator.py`)**

- Random walk algorithm generating realistic GPS paths
- Variable speed (10-80 km/h) and periodic direction changes
- Simulated satellite count and HDOP values
- No hardware required for development and testing

### Data Flow

```
GPS Satellites → GPS Antenna → GPS Module → UART → gps_logger.py → CSV Files → dashboard.py → Web Browser
                                                                      ↑
                                                          gps_stream_simulator.py (for testing)
```

## Features

### Real-Time GPS Tracking

- ✅ Live position updates every 0.5 seconds
- ✅ Interactive fullscreen map with zoom/pan controls
- ✅ GPS trail showing last 100 positions
- ✅ Industrial-style pulsing cyan beacon marker
- ✅ Fixed origin marker at starting point
- ✅ Automatic map centering on current position

### Professional Telemetry Display

- ✅ **Large speed display** (48px cyan monospace)
- ✅ **Latitude/Longitude** (6 decimal precision, monospace)
- ✅ **Altitude** (meters above sea level)
- ✅ **Course** (degrees true north)
- ✅ **Satellite count** (fix quality indicator)
- ✅ **Timestamp** (last update time)
- ✅ Dark mode UI (rgba(26,26,26,0.92) panels)

### Data Logging

- ✅ CSV format with headers for easy analysis
- ✅ Fields: timestamp, latitude, longitude, altitude, speed_knots, speed_kmh, course, satellites, hdop, fix_quality
- ✅ Continuous logging with file flush
- ✅ Professional logging module with INFO/ERROR levels
- ✅ Timestamped log filenames: `gps_log_YYYYMMDD_HHMMSS.csv`

### Testing and Development

- ✅ Realistic GPS path simulator
- ✅ Random walk with variable speed and direction
- ✅ Periodic course changes every 15-30 seconds
- ✅ No hardware required for dashboard development

## Installation and Setup

### Hardware Assembly

1. **Mount GPS HAT**

   - Align Adafruit Ultimate GPS HAT with Raspberry Pi 5 GPIO pins
   - Press firmly to ensure solid connection
   - Insert CR1220 coin cell battery for RTC backup

2. **Connect Antenna**

   - Attach SMA to uFL adapter cable to GPS HAT uFL connector
   - Connect 28dB external active GPS antenna
   - Position antenna with clear sky view (outdoors or near window)

3. **Power System**
   - Connect Raspberry Pi 5 to 27W USB-C power supply
   - For portable operation: Use 20,000mAh+ power bank with PD support

### Software Setup

1. **Install Raspberry Pi OS**

   ```bash
   # Use Raspberry Pi Imager to flash 32GB microSD card
   # Enable SSH and configure Wi-Fi during setup
   ```

2. **Configure Serial Port**

   ```bash
   sudo raspi-config
   # Navigate to: Interface Options → Serial Port
   # "Would you like a login shell accessible over serial?" → NO
   # "Would you like the serial port hardware enabled?" → YES
   sudo reboot
   ```

3. **Install Python Dependencies**

   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install project dependencies
   cd ~/GPS-Data-Logger-Project
   pip install -r requirements.txt
   ```

4. **Verify GPS Connection**

   ```bash
   # View raw NMEA data stream
   cat /dev/serial0

   # Should see lines like:
   # $GPGGA,123456.00,4304.2345,N,08920.1234,W,1,08,1.2,258.3,M,34.2,M,,*5E
   # $GPRMC,123456.00,A,4304.2345,N,08920.1234,W,0.0,0.0,141124,,,A*6F
   ```

## Usage

### Running the GPS Logger

Start the GPS data logger to begin capturing position data from the GPS HAT:

```bash
python gps_logger.py
```

**Output:**

- CSV file saved to `logs/gps_log_YYYYMMDD_HHMMSS.csv`
- Console logging shows GPS fix status and position updates
- Press `Ctrl+C` to stop logging gracefully

### Running the Real-Time Dashboard

Launch the web dashboard for live GPS tracking visualization:

```bash
python dashboard.py
```

**Access the dashboard:**

- Local: `http://localhost:8050`
- Remote: `http://<raspberry-pi-ip>:8050`

**Dashboard controls:**

- Auto-updates every 0.5 seconds
- Zoom: Mouse wheel or +/- buttons
- Pan: Click and drag map
- Stats panel (bottom-left): Speed, Lat/Lon, Altitude, Course, Satellites
- Timestamp (top-right): Last update time

### Running the GPS Simulator (for testing)

Generate realistic simulated GPS data for development and testing:

```bash
python gps_stream_simulator.py
```

**Features:**

- Creates new GPS log file in `logs/` directory
- Random walk algorithm with 10-80 km/h speed
- Periodic direction changes every 15-30 seconds
- Updates every 1 second
- Run simultaneously with `dashboard.py` to visualize simulated tracking

**Use cases:**

- Dashboard development without GPS hardware
- Testing visualization features
- Demonstrating system capabilities indoors
- Training and demos

## Implementation Timeline

The project was completed in phases over approximately 1-2 weeks:

### Phase 1: Hardware Assembly ✅

- Installed Raspberry Pi OS using Raspberry Pi Imager
- Mounted GPS HAT onto Raspberry Pi 5 GPIO header
- Connected external 28dB active GPS antenna (SMA to uFL cable)
- Inserted CR1220 battery for RTC backup
- Configured serial port hardware in `raspi-config`
- Verified NMEA data reception via `/dev/serial0`

### Phase 2: GPS Logger Development ✅

- Implemented NMEA 0183 sentence parsing (GGA and RMC)
- Created CSV logging system with proper data handling
- Added professional logging module (INFO/ERROR levels)
- Implemented error handling for GPS signal loss and missing data
- Default values: altitude -999.0, course -1.0 for invalid data
- Tested with real GPS hardware for accuracy validation

### Phase 3: Real-Time Dashboard Development ✅

- Built Plotly Dash web application framework
- Integrated Dash-Leaflet for interactive mapping
- Designed minimalist dark mode UI (rgba(26,26,26,0.92) panels)
- Implemented industrial-style pulsing cyan beacon markers
- Added real-time telemetry display panel (speed, lat/lon, altitude, course, satellites)
- Optimized update rate to 0.5 seconds for responsive tracking
- Fixed origin point preservation for stable reference marker

### Phase 4: GPS Stream Simulator ✅

- Developed random walk algorithm for realistic GPS paths
- Implemented variable speed (10-80 km/h) with smooth transitions
- Added periodic major direction changes (every 15-30 seconds)
- Simulated variable satellite count (6-12) with correlated HDOP
- Enabled hardware-free testing and development workflow

### Phase 5: Testing and Validation ✅

- Tested stationary accuracy over extended periods
- Validated mobile tracking (walking, driving scenarios)
- Verified dashboard real-time updates with both hardware and simulator
- Measured GPS accuracy at known positions
- Confirmed data integrity and logging reliability
- Tested simulator for realistic movement patterns

## Data Format

### CSV Log Structure

Each log entry contains the following fields:

- **timestamp**: ISO 8601 format UTC timestamp
- **latitude**: Decimal degrees (6 decimal precision)
- **longitude**: Decimal degrees (6 decimal precision)
- **altitude**: Meters above sea level (-999.0 if invalid)
- **speed_knots**: Speed in nautical miles per hour
- **speed_kmh**: Speed in kilometers per hour
- **course**: Direction in degrees true north (-1.0 if invalid)
- **satellites**: Number of satellites used in fix
- **hdop**: Horizontal Dilution of Precision (accuracy indicator)
- **fix_quality**: 0=invalid, 1=GPS fix, 2=DGPS fix

### Example CSV Output

```csv
timestamp,latitude,longitude,altitude,speed_knots,speed_kmh,course,satellites,hdop,fix_quality
2024-11-14T15:30:45.123456,43.073125,-89.401234,258.3,0.0,0.0,45.2,8,1.2,1
2024-11-14T15:30:46.123456,43.073128,-89.401230,258.5,2.5,4.6,46.1,8,1.2,1
2024-11-14T15:30:47.123456,43.073132,-89.401225,258.7,5.1,9.4,47.3,9,1.1,1
```

## GPS Accuracy and Limitations

### Real-World Performance

The system achieves the following typical accuracies under various conditions:

**Clear Sky (Optimal):**

- Horizontal accuracy: 2-3 meters
- Altitude accuracy: 5-10 meters
- 8-12 satellites in view
- HDOP: 0.8-1.5

**Partial Obstruction:**

- Horizontal accuracy: 5-10 meters
- Altitude accuracy: 10-20 meters
- 6-8 satellites in view
- HDOP: 1.5-3.0

**Urban Canyon / Heavy Tree Cover:**

- Horizontal accuracy: 10-20+ meters
- Altitude accuracy: 20-50+ meters
- 4-6 satellites in view
- HDOP: 3.0-8.0

### Known Limitations

GPS accuracy degrades in several scenarios:

- **Urban canyons**: Tall buildings block satellite signals and cause multipath interference
- **Indoor environments**: Weak or no GPS signals indoors
- **Multipath interference**: Signals reflecting off surfaces cause position errors
- **Atmospheric conditions**: Ionospheric and tropospheric delays affect signal propagation
- **Satellite geometry**: Poor satellite distribution (high HDOP) reduces accuracy

The system logs HDOP and satellite count to assess fix quality and reliability.

### Power Management

**Raspberry Pi 5 Power Requirements:**

- Active operation: 5V @ 5A (27W max)
- Typical usage with GPS HAT: 3-4A (15-20W)
- Recommended power supply: Official 27W USB-C adapter

**Portable Operation:**

- Use 20,000mAh+ power bank with USB-C Power Delivery support
- Expected runtime: 4-6 hours continuous operation
- Consider larger capacity (30,000mAh+) for all-day logging

**Power Optimization Tips:**

- Reduce GPS update rate to 1Hz for power savings (10Hz default)
- Disable HDMI output when running headless
- Use lightweight OS configuration
- Reduce CPU frequency if thermal throttling occurs

### Data Storage

**Storage Requirements:**

- 10 Hz logging: ~30-40 KB per hour
- 1 Hz logging: ~3-4 KB per hour
- 32GB microSD card: Years of continuous logging capacity

**Data Integrity:**

- Immediate file flush after each write prevents data loss
- Timestamped log filenames prevent overwrites
- CSV format enables easy recovery and analysis

## Applications

This GPS tracking system demonstrates principles applicable to:

- **Aerospace**: Flight data recorders, UAV navigation, aircraft telemetry
- **Automotive**: Vehicle tracking, fleet management, autonomous navigation
- **Defense**: Military vehicle tracking, reconnaissance, tactical navigation
- **Emergency Services**: Search and rescue, first responder tracking
- **Industrial**: Asset tracking, construction equipment monitoring, logistics
- **Scientific**: Wildlife tracking, environmental monitoring, surveying
- **Sports**: Athletic performance analysis, race timing, training analytics

## Learning Outcomes

This project provides hands-on experience with:

- ✅ Serial communication protocols (UART at 9600 baud)
- ✅ ASCII data parsing (NMEA 0183 format)
- ✅ Real-time data acquisition and processing
- ✅ Professional logging and error handling
- ✅ CSV file I/O and data persistence
- ✅ GPS technology and satellite navigation fundamentals
- ✅ Sensor accuracy analysis and error sources (HDOP, multipath)
- ✅ Embedded systems development on Raspberry Pi
- ✅ Hardware module integration (GPIO, UART, HATs)
- ✅ Web application development (Plotly Dash framework)
- ✅ Interactive mapping and geospatial visualization
- ✅ Real-time telemetry display and monitoring
- ✅ Dark mode UI/UX design principles
- ✅ Testing and simulation for hardware-independent development

## Future Enhancements

Potential improvements to extend system capabilities:

### Navigation and Accuracy

- Integrate IMU (Inertial Measurement Unit) for dead reckoning during GPS outages
- Add Kalman filtering for smoother position estimates and noise reduction
- Implement differential GPS (DGPS) for centimeter-level accuracy
- Add raw satellite ephemeris logging for post-processing

### Monitoring and Alerts

- Implement geofencing with SMS/email alert notifications
- Add battery voltage monitoring and low-power warnings
- Create speed limit alerts and boundary violation detection
- Implement trip detection and automatic start/stop logging

### Visualization and Analysis

- Add historical track replay with speed animation
- Implement heatmaps showing time spent in areas
- Create multi-day trip comparison and analysis
- Add elevation profile graphs and 3D terrain visualization

### Security and Integration

- Add data encryption for secure location logging
- Implement secure WebSocket for lower latency updates
- Integrate with external APIs (weather, traffic, mapping services)
- Add multi-user authentication for fleet tracking

### Hardware Expansion

- Add cellular modem for remote tracking (4G/LTE)
- Integrate accelerometer for crash detection
- Add temperature/humidity sensors for environmental logging
- Implement OLED display for standalone operation

## Technical Details

### Dependencies

The system requires the following Python packages:

```txt
pynmea2>=1.18.0       # NMEA sentence parsing
pandas>=2.0.0         # Data manipulation
dash>=2.14.0          # Web dashboard framework
dash-leaflet>=0.1.0   # Interactive mapping
plotly>=5.17.0        # Plotting and visualization
```

### File Structure

```
GPS-Data-Logger-Project/
├── gps_logger.py              # GPS data logger (NMEA → CSV)
├── dashboard.py               # Real-time web dashboard
├── gps_stream_simulator.py   # GPS path simulator for testing
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── data/
│   └── output.nmea           # Sample NMEA data
└── logs/
    └── gps_log_*.csv         # Generated GPS log files
```

## Safety and Regulatory Considerations

- GPS devices are passive receivers and do not transmit radio signals
- No radio licensing required for GPS reception
- Be aware of privacy implications when logging location data
- Follow local regulations regarding GPS use while driving
- Secure logged data containing location information
- Do not rely solely on GPS for safety-critical navigation
- Always maintain situational awareness when operating vehicles

## Project Timeline

**Total Duration: 1-2 weeks**

| Phase                 | Time      | Activities                                              |
| --------------------- | --------- | ------------------------------------------------------- |
| Hardware Assembly     | 2-3 hours | Mount GPS HAT, connect antenna, configure Raspberry Pi  |
| Software Setup        | 3-4 hours | Install OS, configure serial port, install dependencies |
| Logger Development    | 6-8 hours | NMEA parsing, CSV logging, error handling               |
| Dashboard Development | 6-8 hours | Web framework, mapping, UI design, real-time updates    |
| Simulator Development | 3-4 hours | Random walk algorithm, realistic data generation        |
| Testing & Validation  | 4-6 hours | Accuracy testing, mobile logging, dashboard validation  |
| Documentation         | 2-3 hours | README updates, usage guides, technical documentation   |

## Additional Resources

### Official Documentation

- [Adafruit GPS HAT Guide](https://learn.adafruit.com/adafruit-ultimate-gps-hat-for-raspberry-pi)
- [NMEA 0183 Protocol Specification](https://www.nmea.org/content/STANDARDS/NMEA_0183_Standard)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [Plotly Dash Documentation](https://dash.plotly.com/)
- [Dash-Leaflet Documentation](https://www.dash-leaflet.com/)

### Python Libraries

- [pynmea2 Documentation](https://github.com/Knio/pynmea2)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Python Serial Communication](https://pyserial.readthedocs.io/)

### GPS Technology

- [GPS.gov - Official U.S. Government GPS Information](https://www.gps.gov/)
- [GPS Accuracy Factors and Limitations](https://www.gps.gov/systems/gps/performance/accuracy/)
- [Understanding HDOP and GPS Accuracy](<https://en.wikipedia.org/wiki/Dilution_of_precision_(navigation)>)

## Troubleshooting

### No GPS Data Received

- Verify antenna connection (SMA to uFL cable properly seated)
- Ensure antenna has clear sky view (outdoors or near window)
- Check serial port configuration: `sudo raspi-config` → Serial Port enabled
- Test with `cat /dev/serial0` to view raw NMEA data
- Wait 30-60 seconds for initial satellite acquisition

### Dashboard Not Updating

- Verify GPS logger is running and creating CSV files in `logs/` directory
- Check that dashboard is reading the latest log file
- Ensure port 8050 is not blocked by firewall
- Refresh browser and check console for JavaScript errors

### Poor GPS Accuracy

- Move antenna to location with better sky view
- Check satellite count (should be 6+ for good fix)
- Monitor HDOP (lower is better, <2.0 is good)
- Avoid urban canyons, dense tree cover, and indoor locations
- Consider using external active antenna for improved reception

### Raspberry Pi Performance Issues

- Monitor CPU temperature: `vcgencmd measure_temp`
- Ensure adequate cooling (heatsink or fan)
- Reduce dashboard update rate if needed (change from 0.5s to 1.0s)
- Consider reducing GPS update rate from 10Hz to 1Hz

## Conclusion

This GPS tracking system successfully demonstrates the complete pipeline from hardware sensor integration to real-time web-based visualization. The project combines embedded systems development, serial communication protocols, NMEA data parsing, professional data logging, and modern web dashboard technologies to create a functional tracking system applicable to aerospace, defense, automotive, and industrial applications.

The system features:

- **Real-time tracking** with sub-second update rates
- **Professional telemetry display** with speed, position, altitude, course, and satellite monitoring
- **Industrial-grade UI** with minimalist dark mode design and pulsing beacon markers
- **Hardware simulation** enabling development and testing without GPS equipment
- **Production-quality logging** with proper error handling and data integrity

The skills and technologies demonstrated in this project—including Raspberry Pi hardware integration, UART serial communication, NMEA protocol parsing, real-time data acquisition, web-based telemetry dashboards, and geospatial visualization—are directly applicable to safety-critical systems used in aircraft flight data recorders, autonomous vehicle navigation, military reconnaissance, fleet management, search and rescue operations, and precision surveying.

The completed system serves as both an educational platform for learning GPS technology and embedded systems development, and a functional tool for real-world tracking and navigation applications.

---

**Project Status: Complete and Operational ✅**

For questions, improvements, or contributions, please refer to the documentation and feel free to extend the system with additional features from the Future Enhancements section.
