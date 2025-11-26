/*
 * GPS Data Logger - C++ Implementation with Boost Libraries
 * Uses Boost.Asio for serial communication and modern C++ practices
 */

#include <iostream>
#include <fstream>
#include <string>
#include <iomanip>
#include <ctime>
#include <chrono>
#include <memory>
#include <boost/asio.hpp>
#include <boost/bind/bind.hpp>

using namespace std;
namespace asio = boost::asio;

// Structure to hold GPS data
struct GPSData
{
    string timestamp;
    double latitude = 0.0;
    double longitude = 0.0;
    double altitude = -999.0;
    double speed_knots = 0.0;
    double speed_kmh = 0.0;
    double course = -1.0;
    int satellites = 0;
    double hdop = 99.9;
    int fix_quality = 0;
};

class GPSLogger
{
private:
    asio::io_context io_;
    asio::serial_port serial_;
    asio::streambuf buffer_;
    ofstream log_file_;
    GPSData current_data_;
    int line_count_ = 0;
    bool has_valid_fix_ = false;

    // Get current UTC timestamp in ISO format
    string getCurrentTimestamp()
    {
        auto now = chrono::system_clock::now();
        time_t now_time = chrono::system_clock::to_time_t(now);
        tm utc_tm;

#ifdef _WIN32
        gmtime_s(&utc_tm, &now_time);
#else
        gmtime_r(&now_time, &utc_tm);
#endif

        auto ms = chrono::duration_cast<chrono::milliseconds>(
                      now.time_since_epoch()) %
                  1000;

        ostringstream oss;
        oss << put_time(&utc_tm, "%Y-%m-%dT%H:%M:%S");
        oss << "." << setfill('0') << setw(6) << ms.count() * 1000;

        return oss.str();
    }

    // Split string by delimiter
    vector<string> split(const string &str, char delimiter)
    {
        vector<string> tokens;
        stringstream ss(str);
        string token;

        while (getline(ss, token, delimiter))
        {
            tokens.push_back(token);
        }

        return tokens;
    }

    // Convert NMEA coordinate to decimal degrees
    double nmeaToDecimal(const string &coord, const string &direction)
    {
        if (coord.empty())
            return 0.0;

        try
        {
            size_t dotPos = coord.find('.');
            if (dotPos == string::npos)
                return 0.0;

            int degreeDigits = (coord.length() >= 5 && dotPos >= 4) ? 3 : 2;

            double degrees = stod(coord.substr(0, degreeDigits));
            double minutes = stod(coord.substr(degreeDigits));

            double decimal = degrees + (minutes / 60.0);

            if (direction == "S" || direction == "W")
            {
                decimal = -decimal;
            }

            return decimal;
        }
        catch (...)
        {
            return 0.0;
        }
    }

    // Validate NMEA checksum
    bool validateChecksum(const string &sentence)
    {
        size_t dollarPos = sentence.find('$');
        size_t asteriskPos = sentence.find('*');

        if (dollarPos == string::npos || asteriskPos == string::npos)
        {
            return false;
        }

        unsigned char checksum = 0;
        for (size_t i = dollarPos + 1; i < asteriskPos; i++)
        {
            checksum ^= sentence[i];
        }

        try
        {
            string checksumStr = sentence.substr(asteriskPos + 1, 2);
            unsigned int providedChecksum = stoi(checksumStr, nullptr, 16);
            return checksum == providedChecksum;
        }
        catch (...)
        {
            return false;
        }
    }

    // Parse GGA sentence (position and altitude)
    bool parseGGA(const string &sentence)
    {
        vector<string> fields = split(sentence, ',');

        if (fields.size() < 15)
            return false;

        try
        {
            if (!fields[2].empty() && !fields[3].empty())
            {
                current_data_.latitude = nmeaToDecimal(fields[2], fields[3]);
            }

            if (!fields[4].empty() && !fields[5].empty())
            {
                current_data_.longitude = nmeaToDecimal(fields[4], fields[5]);
            }

            if (!fields[6].empty())
            {
                current_data_.fix_quality = stoi(fields[6]);
            }

            if (!fields[7].empty())
            {
                current_data_.satellites = stoi(fields[7]);
            }

            if (!fields[8].empty())
            {
                current_data_.hdop = stod(fields[8]);
            }

            if (!fields[9].empty())
            {
                current_data_.altitude = stod(fields[9]);
            }

            return true;
        }
        catch (...)
        {
            return false;
        }
    }

    // Parse RMC sentence (speed and course)
    bool parseRMC(const string &sentence)
    {
        vector<string> fields = split(sentence, ',');

        if (fields.size() < 12)
            return false;

        try
        {
            if (!fields[7].empty())
            {
                current_data_.speed_knots = stod(fields[7]);
                // convert from knots to km/h
                current_data_.speed_kmh = current_data_.speed_knots * 1.852;
            }

            if (!fields[8].empty())
            {
                current_data_.course = stod(fields[8]);
            }

            return true;
        }
        catch (...)
        {
            return false;
        }
    }

    // Write GPS data to CSV file
    void writeToCSV()
    {
        if (!log_file_.is_open())
            return;

        log_file_ << current_data_.timestamp << ","
                  << fixed << setprecision(6) << current_data_.latitude << ","
                  << fixed << setprecision(6) << current_data_.longitude << ","
                  << fixed << setprecision(1) << current_data_.altitude << ","
                  << fixed << setprecision(1) << current_data_.speed_knots << ","
                  << fixed << setprecision(1) << current_data_.speed_kmh << ","
                  << fixed << setprecision(1) << current_data_.course << ","
                  << current_data_.satellites << ","
                  << fixed << setprecision(1) << current_data_.hdop << ","
                  << current_data_.fix_quality << "\n";

        log_file_.flush();
    }

    // Process received NMEA sentence
    void processSentence(const string &line)
    {
        line_count_++;

        if (line.empty() || !validateChecksum(line))
            return;

        if (line.find("$GPGGA") != string::npos || line.find("$GNGGA") != string::npos)
        {
            if (parseGGA(line))
            {
                current_data_.timestamp = getCurrentTimestamp();

                if (current_data_.fix_quality > 0 &&
                    current_data_.latitude != 0 &&
                    current_data_.longitude != 0)
                {

                    if (!has_valid_fix_)
                    {
                        has_valid_fix_ = true;
                        cout << "[INFO] GPS fix acquired!" << endl;
                    }

                    writeToCSV();

                    if (line_count_ % 10 == 0)
                    {
                        cout << "[GPS] Lat: " << fixed << setprecision(6) << current_data_.latitude
                             << " Lon: " << current_data_.longitude
                             << " Alt: " << setprecision(1) << current_data_.altitude << "m"
                             << " Speed: " << current_data_.speed_kmh << "km/h"
                             << " Sats: " << current_data_.satellites << endl;
                    }
                }
            }
        }
        else if (line.find("$GPRMC") != string::npos || line.find("$GNRMC") != string::npos)
        {
            parseRMC(line);
        }
    }

    // Async read handler
    void startRead()
    {
        asio::async_read_until(
            serial_,
            buffer_,
            '\n',
            [this](const boost::system::error_code &error, size_t bytes_transferred)
            {
                if (!error)
                {
                    // Extract line from buffer
                    istream is(&buffer_);
                    string line;
                    getline(is, line);

                    // Remove carriage return if present
                    if (!line.empty() && line.back() == '\r')
                    {
                        line.pop_back();
                    }

                    // Process the sentence
                    processSentence(line);

                    // Continue reading
                    startRead();
                }
                else
                {
                    // Log the error
                    cerr << "[ERROR] Read error: " << error.message()
                         << " (code: " << error.value() << ")" << endl;

                    // On ANY error (including EOF), just keep trying
                    // The GPS might be temporarily unavailable but will recover
                    cerr << "[INFO] Waiting 100ms before retry..." << endl;

                    // Wait a moment before retrying
                    auto timer = make_shared<asio::steady_timer>(io_, chrono::milliseconds(100));
                    timer->async_wait([this, timer](const boost::system::error_code &ec)
                                      {
                        if (!ec) {
                            startRead();
                        } });
                }
            });
    }

    // Create CSV log file with headers
    bool createLogFile()
    {
        time_t now = time(nullptr);
        tm local_tm;

#ifdef _WIN32
        localtime_s(&local_tm, &now);
#else
        localtime_r(&now, &local_tm);
#endif

        ostringstream filename;
        filename << "logs/gps_log_"
                 << put_time(&local_tm, "%Y%m%d_%H%M%S")
                 << ".csv";

        log_file_.open(filename.str());

        if (log_file_.is_open())
        {
            log_file_ << "timestamp,latitude,longitude,altitude,speed_knots,speed_kmh,"
                      << "course,satellites,hdop,fix_quality\n";
            log_file_.flush();

            cout << "[INFO] Created log file: " << filename.str() << endl;
            return true;
        }
        else
        {
            cerr << "[ERROR] Failed to create log file: " << filename.str() << endl;
            return false;
        }
    }

public:
    GPSLogger() : serial_(io_) {}

    ~GPSLogger()
    {
        if (log_file_.is_open())
        {
            log_file_.close();
        }
    }

    // Open serial port and start logging
    bool start(const string &port_name, unsigned int baud_rate = 9600)
    {
        try
        {
            // Open serial port
            serial_.open(port_name);

            // Configure serial port
            serial_.set_option(asio::serial_port_base::baud_rate(baud_rate));
            serial_.set_option(asio::serial_port_base::character_size(8));
            serial_.set_option(asio::serial_port_base::parity(
                asio::serial_port_base::parity::none));
            serial_.set_option(asio::serial_port_base::stop_bits(
                asio::serial_port_base::stop_bits::one));
            serial_.set_option(asio::serial_port_base::flow_control(
                asio::serial_port_base::flow_control::none));

            cout << "[INFO] Serial port opened: " << port_name
                 << " at " << baud_rate << " baud" << endl;

            // Create log file
            if (!createLogFile())
            {
                return false;
            }

            cout << "[INFO] Waiting for GPS fix..." << endl;
            cout << "[INFO] Press Ctrl+C to stop logging" << endl;
            cout << string(60, '=') << "\n"
                 << endl;

            // Start async reading
            startRead();

            // Run the io_service
            io_.run();

            return true;
        }
        catch (const boost::system::system_error &e)
        {
            cerr << "[ERROR] Failed to open serial port: " << e.what() << endl;
            return false;
        }
    }

    void stop()
    {
        io_.stop();
        if (serial_.is_open())
        {
            serial_.close();
        }
    }
};

int main(int argc, char *argv[])
{
    cout << "\n"
         << string(60, '=') << endl;
    cout << "GPS Data Logger - C++ Boost Implementation" << endl;
    cout << string(60, '=') << endl;

// Default serial port
#ifdef _WIN32
    string portName = (argc > 1) ? argv[1] : "COM3";
#else
    string portName = (argc > 1) ? argv[1] : "/dev/serial0";
#endif

    GPSLogger logger;

    if (!logger.start(portName))
    {
        return 1;
    }

    cout << "\n[INFO] Logging stopped" << endl;

    return 0;
}
