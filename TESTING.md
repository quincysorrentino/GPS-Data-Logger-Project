# Testing Real-Time Dashboard

## How to Test with Simulated Data Stream

### Step 1: Start the Dashboard

In **Terminal 1**:

```powershell
python dashboard.py
```

Open browser to: **http://127.0.0.1:8050**

### Step 2: Start the Data Stream Simulator

In **Terminal 2**:

```powershell
python gps_stream_simulator.py
```

This will:

- Generate a new GPS point every 1 second
- Simulate circular movement around Madison, WI
- Create realistic speed, altitude, and satellite variations
- Write to a new CSV file in `logs/`

### Step 3: Watch the Dashboard Update

The dashboard will:

- Update every 1 second (reduced from 2 seconds)
- Show the moving marker on the map
- Update speed, altitude, course, and satellites in real-time
- Draw a cyan trail showing the path

## Dashboard Features (Dark Mode)

### Map

- **Dark theme** using CartoDB Dark Matter tiles
- **Cyan trail** (#00d4ff) shows GPS path
- **Red marker** shows current position
- **Green marker** shows start position

### Stats Panel (Bottom Left)

- **Large speed** in cyan color
- **Altitude** in meters
- **Course** in degrees
- **Satellite count**

### Update Indicator (Top Right)

- Shows last update time (HH:MM:SS)
- Monospace font
- Updates every second

## Stop Testing

Press `Ctrl+C` in Terminal 2 to stop the simulator
Press `Ctrl+C` in Terminal 1 to stop the dashboard

## Map Schemes Available

You can change the map tile in `dashboard.py`:

**Current (Dark):**

```python
dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png')
```

**Other Options:**

Light theme:

```python
dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png')
```

Satellite:

```python
dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}')
```

Standard OpenStreetMap:

```python
dl.TileLayer()  # Default
```
