#include <boost/format.hpp>
#include <boost/algorithm/string.hpp>
#include "../Logging/ConsoleLogger.h"
#include "http_req.h"
#include "magnetic_field_lookup.h"

#define MAG_LOOKUP_ENDPOINT "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateIgrfwmm?resultFormat=csv&coordinateSystem=M&lat1=%1%&lon1=%2%&alt=%3%"
#define TO_RAD(d) (d*(M_PI / 180.0))

std::vector<double> parse_doubles_in_line(std::string s) {
    std::vector<std::string> values_s;
    std::vector<double> values;
    boost::split(values_s, s, [](char c){return c == ',';});    
    for (int i = 0; i < values_s.size(); i++) {
        values.push_back(std::stod(values_s[i]));
    }
    return values;
}

Eigen::VectorXd parse_response_to_vector(std::string s) {
    std::vector<std::string> lines;
    boost::split(lines, s, [](char c){return c == '\n';});
    // Last line of the canonical response from MAG_LOOKUP_ENDPOINT
    std::vector<double> mag_values = parse_doubles_in_line(lines[lines.size() - 2]);

    // Indices are specified in the response (which is human readable)
    Eigen::VectorXd magfield{3};
    // Nanotesla to Gauss
    magfield[0] = mag_values[5] * 1e-5;
    magfield[1] = mag_values[6] * 1e-5;
    magfield[2] = mag_values[7] * 1e-5;

    return magfield;
}

static Eigen::VectorXd cached_magfield = Eigen::VectorXd::Zero(3);

Eigen::VectorXd magnetic_field_for_latlonalt(LatLonAlt lat_lon_alt) {
    try {
        if (cached_magfield.isZero()) {
            URL u(boost::str((boost::format(MAG_LOOKUP_ENDPOINT) % 
                    (lat_lon_alt.latitude_deg) % // LatLon are converted to int form by multiplying by 1.e7 in DroneStateEncode 
                    (lat_lon_alt.longitude_deg) % // ^^^^^^^^^^ This is a re-normalization to decimal form
                    ((lat_lon_alt.altitude_mm / 1000) / 1000) // mm to km
                )));
            cached_magfield = parse_response_to_vector(u.get_body());
        } return cached_magfield;
    } catch(const std::exception& e) {
        ConsoleLogger* logger = ConsoleLogger::shared_instance();
        logger->debug_log("Error in magnetic_field_for_latlonalt");
        fprintf(stderr, "%s\n", e.what());
    }
}