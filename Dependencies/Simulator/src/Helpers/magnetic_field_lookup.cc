#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <list>
#include <string>
#include <iomanip>
#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>
#include "../Logging/ConsoleLogger.h"
#include "magnetic_field_lookup.h"
#include "../MagneticModel/WMM.h"

static Eigen::VectorXd* cached_magfield = NULL;

Eigen::VectorXd magnetic_field_for_latlonalt(LatLonAlt lat_lon_alt) {
    if (cached_magfield != NULL) return *cached_magfield;
    geomag_vector now;
    time_t my_time;
    struct tm * timeinfo; 
    time (&my_time);
    timeinfo = localtime (&my_time);
    WorldMagneticModel(&now, lat_lon_alt.latitude_deg, lat_lon_alt.longitude_deg, lat_lon_alt.altitude_mm / 1000000.0, timeinfo->tm_year+1900);// Lat, Lon, Alt, Time
    cached_magfield = new Eigen::VectorXd(3);
    (*cached_magfield)[0] = now.X * 1e-5;
    (*cached_magfield)[1] = now.Y * 1e-5;
    (*cached_magfield)[2] = now.Z * 1e-5;
    return *cached_magfield;
}