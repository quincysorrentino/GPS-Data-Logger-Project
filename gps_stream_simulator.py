"""
GPS Data Stream Simulator
Generates real-time GPS data for testing the dashboard
Simulates movement around Madison, WI
"""

import time
import csv
from datetime import datetime
import math
import random

# Starting position (Madison, WI)
START_LAT = 43.0731
START_LON = -89.4012
START_ALT = 260.0

# Movement state
current_lat = START_LAT
current_lon = START_LON
current_alt = START_ALT
current_course = random.uniform(0, 360)  # Random initial direction
current_speed = 40.0  # Start at 40 km/h

def generate_gps_point(point_num):
    """Generate a GPS point that simulates random realistic movement"""
    global current_lat, current_lon, current_alt, current_course, current_speed
    
    # Periodic major direction changes (every 15-30 seconds)
    if point_num > 0 and point_num % random.randint(15, 30) == 0:
        # Major course change - turn to a new random direction
        current_course = random.uniform(0, 360)
        print(f"  >> Major direction change: {current_course:.0f}°")
    # Random course changes (more realistic driving)
    # Small adjustments each second, occasional larger turns
    elif random.random() < 0.15:  # 15% chance of significant turn
        course_change = random.uniform(-45, 45)
        current_course = (current_course + course_change) % 360
    else:
        course_change = random.uniform(-10, 10)  # Small adjustments
        current_course = (current_course + course_change) % 360
    
    # Random speed changes (acceleration/deceleration)
    speed_change = random.uniform(-20, 20)
    current_speed = max(5, min(100, current_speed + speed_change))
    
    # Calculate movement based on speed and course
    # Speed in km/h, convert to degrees per second (rough approximation)
    distance_per_second = current_speed / 3600 / 111  # km to degrees latitude
    
    # Move in current direction
    lat_change = distance_per_second * math.cos(math.radians(current_course))
    lon_change = distance_per_second * math.sin(math.radians(current_course)) / math.cos(math.radians(current_lat))
    
    current_lat += lat_change
    current_lon += lon_change
    
    # Simulate altitude changes (gradual terrain changes)
    alt_change = random.uniform(-2, 2)
    current_alt = max(250, min(300, current_alt + alt_change))  # Keep between 250-300m
    
    # Satellites (8-12, occasionally fewer)
    if random.random() < 0.05:  # 5% chance of signal degradation
        satellites = random.randint(6, 8)
    else:
        satellites = random.randint(10, 12)
    
    # HDOP varies with satellite count
    if satellites < 8:
        hdop = random.uniform(2.0, 3.5)
    else:
        hdop = random.uniform(0.8, 1.5)
    
    speed_knots = current_speed / 1.852
    
    return {
        'timestamp': datetime.now().isoformat(),
        'latitude': current_lat,
        'longitude': current_lon,
        'altitude': current_alt,
        'speed_knots': speed_knots,
        'speed_kmh': current_speed,
        'course': current_course,
        'satellites': satellites,
        'hdop': hdop,
        'fix_quality': 1
    }

def main():
    """Main function to stream GPS data"""
    print("\n" + "="*60)
    print("GPS Data Stream Simulator")
    print("="*60)
    print("Generating real-time GPS data...")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Create/open CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/gps_log_{timestamp}.csv"
    
    # Write header
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'latitude', 'longitude', 'altitude',
            'speed_knots', 'speed_kmh', 'course', 'satellites',
            'hdop', 'fix_quality'
        ])
        writer.writeheader()
    
    print(f"Writing to: {filename}\n")
    
    point_num = 0
    
    try:
        while True:
            # Generate GPS point
            point = generate_gps_point(point_num)
            
            # Append to CSV
            with open(filename, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=point.keys())
                writer.writerow(point)
            
            # Print status
            print(f"Point {point_num + 1}: "
                  f"Lat: {point['latitude']:.6f} | "
                  f"Lon: {point['longitude']:.6f} | "
                  f"Speed: {point['speed_kmh']:.1f} km/h | "
                  f"Course: {point['course']:.0f}° | "
                  f"Alt: {point['altitude']:.1f}m | "
                  f"Sats: {point['satellites']}")
            
            point_num += 1
            
            # Wait 1 second before next point
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("Stream stopped")
        print(f"Total points generated: {point_num}")
        print(f"File: {filename}")
        print("="*60)

if __name__ == "__main__":
    main()
