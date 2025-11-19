"""
GPS Logger Script
Reads NMEA sentences from a file and logs GPS data to CSV
"""

import pynmea2
import csv
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_csv_file():
    """
    Create a CSV file with timestamp in the filename
    Returns the file object and csv writer
    """
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/gps_log_{timestamp}.csv"
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Open file for writing
    csvfile = open(filename, 'w', newline='')
    csv_writer = csv.writer(csvfile)
    
    # Write header row
    header = [
        'timestamp',
        'latitude',
        'longitude',
        'altitude',
        'speed_knots',
        'speed_kmh',
        'course',
        'satellites',
        'hdop',
        'fix_quality'
    ]
    csv_writer.writerow(header)
    
    logger.info(f"Created CSV file: {filename}")
    return csvfile, csv_writer, filename


def parse_nmea_file(nmea_filename):
    """
    Parse NMEA file and extract GPS data
    """
    # Create CSV file
    csvfile, csv_writer, csv_filename = create_csv_file()
    
    # Counters and data storage
    points_logged = 0
    gga_data = {}  # Store latest GGA data
    rmc_data = {}  # Store latest RMC data
    
    logger.info(f"Reading NMEA file: {nmea_filename}")
    logger.info("Processing NMEA sentences...")
    
    try:
        with open(nmea_filename, 'r') as nmea_file:
            for line in nmea_file:
                # Strip whitespace
                line = line.strip()
                
                # Skip empty lines or lines that don't start with $
                if not line or not line.startswith('$'):
                    continue
                
                # Try to parse the NMEA sentence
                try:
                    msg = pynmea2.parse(line)
                    
                    # Process GGA messages (position, altitude, fix quality)
                    if isinstance(msg, pynmea2.types.talker.GGA):
                        # Check if we have a valid GPS fix
                        if msg.gps_qual and msg.gps_qual > 0:
                            gga_data = {
                                'latitude': msg.latitude,
                                'longitude': msg.longitude,
                                'altitude': msg.altitude if msg.altitude is not None else -999.0,  # -999.0 = No altitude data
                                'satellites': msg.num_sats if msg.num_sats is not None else 0,     # 0 = No satellites
                                'hdop': msg.horizontal_dil if msg.horizontal_dil is not None else 99.9,  # 99.9 = Poor/unknown precision
                                'fix_quality': msg.gps_qual
                            }
                    
                    # Process RMC messages (speed, course)
                    elif isinstance(msg, pynmea2.types.talker.RMC):
                        if msg.status == 'A':  # A = Active/Valid, V = Void/Invalid
                            rmc_data = {
                                'speed_knots': msg.spd_over_grnd if msg.spd_over_grnd is not None else 0.0,  # 0.0 = Stationary/no data
                                'course': msg.true_course if msg.true_course is not None else -1.0  # -1.0 = No course data (valid course: 0-360°)
                            }
                            
                            # If we have both GGA and RMC data, write to CSV
                            if gga_data:
                                # Get current timestamp
                                timestamp = datetime.now().isoformat()
                                
                                # Calculate speed in km/h (1 knot = 1.852 km/h)
                                speed_knots = rmc_data['speed_knots']
                                speed_kmh = speed_knots * 1.852
                                
                                # Create data row
                                data_row = [
                                    timestamp,
                                    gga_data['latitude'],
                                    gga_data['longitude'],
                                    gga_data['altitude'],
                                    speed_knots,
                                    speed_kmh,
                                    rmc_data['course'],
                                    gga_data['satellites'],
                                    gga_data['hdop'],
                                    gga_data['fix_quality']
                                ]
                                
                                # Write to CSV
                                csv_writer.writerow(data_row)
                                csvfile.flush()  # Ensure data is saved
                                
                                points_logged += 1
                                
                except pynmea2.ParseError as e:
                    # Skip invalid sentences
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error parsing sentence: {e}")
                    continue
    
    finally:
        # Close CSV file
        csvfile.close()
    
    # Log summary
    logger.info("="*60)
    logger.info("GPS logging complete!")
    logger.info(f"Total points logged: {points_logged}")
    logger.info(f"Output file: {csv_filename}")
    logger.info("="*60)


def main():
    """
    Main function to run the GPS logger
    """
    logger.info("="*60)
    logger.info("GPS LOGGER - NMEA to CSV Converter")
    logger.info("="*60)
    
    # NMEA file to process
    nmea_file = "data/output.nmea"
    
    # Check if file exists
    if not os.path.exists(nmea_file):
        logger.error(f"NMEA file not found: {nmea_file}")
        return
    
    # Parse the file
    parse_nmea_file(nmea_file)


if __name__ == "__main__":
    main()
