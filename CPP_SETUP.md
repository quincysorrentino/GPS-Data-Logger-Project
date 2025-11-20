# C++ Implementation Setup Guide

## Overview

This project includes a C++ implementation of the GPS logger for better performance on embedded systems like Raspberry Pi. The C++ logger produces identical CSV output files that work with the Python dashboard.

## Why C++?

- **Performance**: ~2-5% CPU usage vs ~10-15% for Python
- **Memory**: ~2MB vs ~50MB for Python
- **Better for embedded systems**: More efficient on Raspberry Pi
- **Same functionality**: Creates identical CSV files for the dashboard

## Quick Start

### Prerequisites

**Windows:**

- MinGW-w64 or Visual Studio C++ compiler
- CMake 3.10+

**Raspberry Pi / Linux:**

- GCC (usually pre-installed)
- CMake: `sudo apt install cmake build-essential`

### Building

```bash
# Create build directory
mkdir build
cd build

# Generate build files
cmake ..

# Build
cmake --build .    # Windows
make               # Linux
```

### Running

**Windows:**

```powershell
.\build\Debug\gps_logger_boost.exe COM3
```

**Raspberry Pi:**

```bash
sudo ./build/gps_logger_boost /dev/serial0
```

## Implementation Options

### Option 1: Boost.Asio Version (Recommended)

- **File**: `gps_logger_boost.cpp`
- **Requires**: Boost libraries
- **Advantages**: Cleaner code, asynchronous I/O, industry-standard
- **Setup**: See full documentation in `CPP_DOCUMENTATION.md`

### Option 2: Pure C++ Version (No Dependencies)

- **File**: `gps_logger.cpp`
- **Requires**: Only standard C++11
- **Advantages**: Zero dependencies, works anywhere
- **Setup**: Direct compilation or CMake

## Installation

### Installing Boost (for Boost version)

**Windows (vcpkg):**

```powershell
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg install boost-asio:x64-windows
```

**Raspberry Pi / Linux:**

```bash
sudo apt install libboost-all-dev
```

## Using with Python Dashboard

The C++ logger creates CSV files in `logs/` directory. Simply run the Python dashboard to visualize the data:

```bash
# Terminal 1: C++ Logger
./build/gps_logger_boost

# Terminal 2: Python Dashboard
python dashboard.py
```

Visit: http://localhost:8050

## File Structure

```
├── gps_logger_boost.cpp    # Boost implementation (recommended)
├── gps_logger.cpp          # Pure C++ implementation
├── CMakeLists.txt          # Build configuration
└── logs/                   # CSV output directory
```

## Troubleshooting

### "cmake not found"

```bash
# Windows
choco install cmake

# Linux
sudo apt install cmake
```

### "Boost not found"

Follow installation instructions above or use pure C++ version.

### "Permission denied" on serial port (Linux)

```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

## Performance Comparison

| Metric    | Python | C++     |
| --------- | ------ | ------- |
| CPU Usage | 10-15% | 2-5%    |
| Memory    | ~50MB  | ~2MB    |
| Startup   | 1-2s   | Instant |

## More Information

For detailed documentation including:

- Beginner's guide with step-by-step instructions
- Library comparisons
- Detailed troubleshooting
- Code explanations

See: `CPP_DOCUMENTATION.md` (local reference only)

---

**Note**: Both Python and C++ implementations produce identical output. Choose based on your needs:

- **Python**: Easier for development and prototyping
- **C++**: Better for production and embedded systems
