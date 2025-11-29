cmake_minimum_required(VERSION 3.10)
project(GPSLogger VERSION 1.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Find Boost (required)
find_package(Boost 1.65 REQUIRED COMPONENTS system)

if(Boost_FOUND)
    message(STATUS "Boost found: ${Boost_VERSION}")
    message(STATUS "Boost include dirs: ${Boost_INCLUDE_DIRS}")
    message(STATUS "Boost libraries: ${Boost_LIBRARIES}")
else()
    message(FATAL_ERROR "Boost not found. Please install Boost libraries.")
endif()

# Add executable
add_executable(gps_logger_boost gps_logger_boost.cpp)

# Include Boost headers
target_include_directories(gps_logger_boost PRIVATE ${Boost_INCLUDE_DIRS})

# Link Boost libraries and threading support
find_package(Threads REQUIRED)
target_link_libraries(gps_logger_boost ${Boost_LIBRARIES} Threads::Threads)

# Set output directory
set_target_properties(gps_logger_boost PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# Print build information
message(STATUS "C++ Compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
