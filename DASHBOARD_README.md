# GPS Dashboard - Quick Start Guide

## 🚀 Quick Start

### Option 1: Run Dashboard with Existing Data

If you already have GPS log files in the `logs/` folder:

```bash
python dashboard.py
```

Then open your browser to: **http://127.0.0.1:8050**

---

### Option 2: Run Logger + Dashboard Together

**Terminal 1 (GPS Logger):**

```bash
python gps_logger.py
```

**Terminal 2 (Dashboard):**

```bash
python dashboard.py
```

Then open your browser to: **http://127.0.0.1:8050**

---

## 📊 Dashboard Features

### Real-Time Components:

- ✅ **Live GPS Map** - Shows current position with blue trail
- ✅ **Speed Gauge** - Real-time speedometer
- ✅ **Altitude Profile** - Elevation changes over time
- ✅ **Speed Chart** - Speed variations over time
- ✅ **Satellite Count** - GPS signal quality
- ✅ **Statistics Panel** - Distance, speeds, altitude range

### Auto-Refresh:

- Updates every **2 seconds**
- Automatically reads latest CSV file
- Shows last 100 GPS points

---

## 🎨 What You'll See

1. **Header**: Shows last update time and point count
2. **Left Side**: Interactive map with your GPS trail
   - 🟢 Green marker = Start position
   - 🔴 Red marker = Current position
   - 🔵 Blue line = Your path
3. **Right Side**: Statistics and current speed gauge
4. **Bottom**: Altitude and speed graphs

---

## ⚙️ Customization Options

### Change Update Frequency

In `dashboard.py`, find this line:

```python
interval=2*1000,  # Update every 2 seconds
```

Change to `1*1000` for 1 second updates, or `5*1000` for 5 seconds.

### Show More/Fewer Points

In `dashboard.py`, find:

```python
df = load_gps_data(max_points=100)
```

Change `100` to show more or fewer points on the map.

### Change Map Style

The map uses OpenStreetMap by default. You can change the tile layer in the map component.

---

## 🐛 Troubleshooting

### "No GPS data available yet"

- Make sure you have CSV files in the `logs/` folder
- Run `gps_logger.py` first to generate data

### Dashboard won't start

- Check if port 8050 is already in use
- Make sure all packages are installed: `pip install -r requirements.txt`

### Map not centered correctly

- The map will auto-center on your first GPS point
- Default is Madison, WI until data loads

---

## 📝 Notes

- Dashboard reads the **most recent** CSV file in `logs/`
- It automatically filters out invalid GPS points (0,0 coordinates)
- Works with both real-time logging and historical data
- Can handle multiple viewers at once

---

## 🔧 Advanced Usage

### Run on Different Port

```bash
python dashboard.py --port 8080
```

### Access from Other Devices

Change in `dashboard.py`:

```python
app.run_server(debug=True, host='0.0.0.0', port=8050)
```

Then access via: `http://YOUR_IP:8050`

---

Enjoy your real-time GPS tracking dashboard! 🛰️📊
