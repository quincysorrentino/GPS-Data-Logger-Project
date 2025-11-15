# GPS-Data-Logger-Project

## Overview

This project involves building a portable GPS data logging system using a Raspberry Pi 5 and the Adafruit Ultimate GPS HAT. The system records GPS coordinates, speed, altitude, and timestamp data for later analysis. This type of system is fundamental to flight data recorders, vehicle telemetry systems, and navigation applications used in aerospace and defense.

## Motivation

Aircraft black boxes and vehicle tracking systems rely on GPS data logging to record position and movement data. Understanding how to capture, store, and analyze GPS data is essential for anyone working in aerospace, autonomous systems, or defense technology. This project demonstrates the core principles behind data acquisition systems used in safety-critical applications.

## Project Goals

- Build a functional GPS data logger from hardware components
- Learn to interface with GPS modules and parse NMEA data formats
- Implement efficient data logging to handle continuous sensor streams
- Analyze logged data to calculate statistics and visualize tracks
- Understand GPS limitations and accuracy factors

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

### Hardware Stack

The GPS HAT mounts directly onto the Raspberry Pi's 40-pin GPIO header. It uses the hardware UART (pins 8 and 10) for GPS communication and GPIO pin 4 for the PPS (Pulse Per Second) signal. The external antenna connects via uFL connector on the HAT.

### Software Architecture

The system operates in three main stages:

1. **Data Acquisition**: Read NMEA sentences from GPS module via serial port
2. **Data Processing**: Parse NMEA format and extract relevant fields
3. **Data Storage**: Write processed data to timestamped log files

### Data Flow

```
GPS Satellites → GPS Antenna → GPS Module → UART → Raspberry Pi → SD Card
```

## Implementation Plan

### Phase 1: Hardware Assembly (Day 1)

1. Install Raspberry Pi OS on microSD card using Raspberry Pi Imager
2. Mount GPS HAT onto Raspberry Pi GPIO header
3. Secure with M2.5 standoffs at mounting holes
4. Connect external antenna: HAT uFL → adapter cable → SMA antenna
5. Insert CR1220 battery into HAT coin cell holder
6. Connect power supply and verify LED indicators

### Phase 2: Software Setup (Day 2)

1. Boot Raspberry Pi and complete initial configuration
2. Disable serial console to free UART for GPS use
3. Install required Python libraries (pyserial, pynmea2)
4. Test GPS communication by reading raw NMEA sentences
5. Verify satellite acquisition and position fix

### Phase 3: Logger Development (Days 3-4)

1. Write Python script to continuously read GPS data
2. Implement NMEA sentence parsing
3. Create CSV logging format with relevant fields
4. Add error handling for GPS signal loss
5. Implement graceful shutdown on keyboard interrupt

### Phase 4: Testing and Validation (Days 5-6)

1. Test stationary accuracy over extended period
2. Test mobile logging (walking, driving)
3. Measure battery life with portable power bank
4. Verify data integrity and completeness

### Phase 5: Analysis Tools (Days 7-8)

1. Write script to parse logged CSV files
2. Calculate statistics (total distance, max speed, average speed)
3. Generate track visualization on map
4. Analyze GPS accuracy by comparing positions at known stationary point

## Data Format

### Logged Fields

Each log entry contains:

- Timestamp (UTC)
- Latitude (decimal degrees)
- Longitude (decimal degrees)
- Altitude (meters above sea level)
- Speed (knots or km/h)
- Course (degrees true)
- Satellites in use
- HDOP (Horizontal Dilution of Precision)
- Fix quality (0=invalid, 1=GPS fix, 2=DGPS fix)

### File Format

CSV format for easy analysis:

```
timestamp,latitude,longitude,altitude,speed,course,satellites,hdop,fix_quality
2024-11-14T15:30:45,43.0731,-89.4012,258.3,0.0,0.0,8,1.2,1
```

## Expected Challenges

### GPS Accuracy Limitations

GPS accuracy degrades in several scenarios:

- Urban canyons with tall buildings blocking satellite view
- Indoor environments with weak signals
- Multipath interference from reflective surfaces
- Atmospheric conditions affecting signal propagation

The project will document these limitations through testing.

### Power Management

The Raspberry Pi 5 requires 27W power supply, which limits portable operation time. Battery selection and power optimization are critical for extended field use.

### Data Storage

Continuous 10 Hz logging generates significant data volume. The system must handle sustained write operations without buffer overflows or data loss.

## Applications

This GPS logging system demonstrates principles applicable to:

- Flight data recorders in aircraft
- Vehicle tracking and fleet management
- Autonomous navigation systems
- Search and rescue operations
- Wildlife tracking
- Athletic performance analysis
- Surveying and mapping

## Learning Outcomes

By completing this project, I will gain experience with:

- Serial communication protocols (UART)
- Binary and ASCII data parsing (NMEA format)
- Real-time data acquisition systems
- File I/O and data persistence
- GPS technology and satellite navigation
- Sensor accuracy analysis and error sources
- Embedded systems development on Raspberry Pi
- Integration of hardware modules (HATs)

## Future Enhancements

Potential improvements beyond the initial scope:

- Integrate IMU for dead reckoning during GPS outages
- Add Kalman filtering for smoother position estimates
- Implement geofencing with alert notifications
- Create real-time web dashboard for live tracking
- Add data encryption for secure logging
- Integrate with mapping APIs for automatic route visualization
- Implement differential GPS for centimeter accuracy
- Add logging of raw satellite ephemeris data

## Safety and Regulatory Considerations

- GPS devices are passive receivers and do not transmit
- No radio licensing required for GPS reception
- Be aware of privacy implications when logging location data
- Follow local regulations regarding GPS use while driving
- Secure logged data containing location information

## Timeline

Total project duration: 1-2 weeks

- Hardware assembly: 2-3 hours
- Software setup: 3-4 hours
- Logger development: 6-8 hours
- Testing: 4-6 hours
- Analysis tools: 4-6 hours
- Documentation: 2-3 hours

## Resources

- Adafruit GPS HAT documentation and tutorials
- NMEA 0183 protocol specification
- Raspberry Pi GPIO pinout reference
- Python serial communication libraries
- GPS accuracy analysis methodologies

## Conclusion

This project provides hands-on experience with GPS technology, data acquisition systems, and embedded computing. The skills developed are directly applicable to aerospace and defense applications where position tracking and data logging are critical capabilities. The completed system serves as both a learning platform and a functional tool for various tracking and navigation applications.
