#pragma once

#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <vector>
#include <stdlib.h>     /* system, NULL, EXIT_FAILURE */

/*
 * For each frame 30 different GPS/IMU values are stored in a text file, such as:  
 * -lat:   latitude of the oxts-unit (deg)
 * -lon:   longitude of the oxts-unit (deg)
 * -alt:   altitude of the oxts-unit (m)
 * -roll:  roll angle (rad),    0 = level, positive = left side up,      range: -pi   .. +pi
 * -pitch: pitch angle (rad),   0 = level, positive = front down,        range: -pi/2 .. +pi/2
 * -yaw:   heading (rad),       0 = east,  positive = counter clockwise, range: -pi   .. +pi
 * -vn:    velocity towards north (m/s)
 * -ve:    velocity towards east (m/s)
 * -vf:    forward velocity, i.e. parallel to earth-surface (m/s)
 * -vl:    leftward velocity, i.e. parallel to earth-surface (m/s)
 * -vu:    upward velocity, i.e. perpendicular to earth-surface (m/s)
 * -ax:    acceleration in x, i.e. in direction of vehicle front (m/s^2)
 * -ay:    acceleration in y, i.e. in direction of vehicle left (m/s^2)
 * -az:    acceleration in z, i.e. in direction of vehicle top (m/s^2)
 * -af:    forward acceleration (m/s^2)
 * -al:    leftward acceleration (m/s^2)
 * -au:    upward acceleration (m/s^2)
 * -wx:    angular rate around x (rad/s)
 * -wy:    angular rate around y (rad/s)
 * -wz:    angular rate around z (rad/s)
 * -wf:    angular rate around forward axis (rad/s)
 * -wl:    angular rate around leftward axis (rad/s)
 * -wu:    angular rate around upward axis (rad/s)
 * -pos_accuracy:  velocity accuracy (north/east in m)
 * -vel_accuracy:  velocity accuracy (north/east in m/s)
 * -navstat:       navigation status (see navstat_to_string)
 * -numsats:       number of satellites tracked by primary GPS receiver
 * -posmode:       position mode of primary GPS receiver (see gps_mode_to_string)
 * -velmode:       velocity mode of primary GPS receiver (see gps_mode_to_string)
 * -orimode:       orientation mode of primary GPS receiver (see gps_mode_to_string)
 */


class OxtsData {

    struct GeoGoordinates {
        double lat;
        double lon;
        double alt;

        GeoGoordinates() {
            lat = lon = alt = 0;
        }

        GeoGoordinates(double lat, double lon, double alt) : lat(lat), lon(lon)
        , alt(alt) {
        }

        void setGeoGoordinates(double lat, double lon, double alt) {
            this->lat = lat;
            this->lon = lon;
            this->alt = alt;
        }

    };

    struct Rotation {
        double roll;
        double pitch;
        double yaw;

        Rotation() {
        }

        Rotation(double roll, double pitch, double yaw) : roll(roll),
        pitch(pitch), yaw(yaw) {
        }

        void setRotation(double roll, double pitch, double yaw) {
            this->roll = roll;
            this->pitch = pitch;
            this->yaw = yaw;
        }

    };

    struct Velocity {
        double vn;
        double ve;
        double vf;
        double vl;
        double vu;

        Velocity() {
        }

        Velocity(double vn, double ve, double vf, double vl, double vu) :
        vn(vn), ve(ve), vf(vf), vl(vl), vu(vu) {
        }

        void setVelocity(double vn, double ve, double vf, double vl,
                double vu) {
            this->vn = vn;
            this->ve = ve;
            this->vf = vf;
            this->vl = vl;
            this->vu = vu;
        }

    };

    struct Acceleration {
        double ax;
        double ay;
        double az;
        double af;
        double al;
        double au;

        Acceleration() {
        }

        Acceleration(double ax, double ay, double az, double af, double al,
                double au) : ax(ax), ay(ay), az(az), af(af), al(al), au(au) {
        }

        void setAcceleration(double ax, double ay, double az, double af,
                double al, double au) {
            this->ax = ax;
            this->ay = ay;
            this->az = az;
            this->af = af;
            this->al = al;
            this->au = au;
        }

    };

    struct AngularRateAround {
        double wx;
        double wy;
        double wz;
        double wf;
        double wl;
        double wu;

        AngularRateAround() : wx(0), wy(0), wz(0), wf(0), wl(0), wu(0) {

        }

        AngularRateAround(double wx, double wy, double wz, double wf, double wl,
                double wu) : wx(wx), wy(wy), wz(wz), wf(wf), wl(wl), wu(wu) {
        }

        void setAngularRateAround(double wx, double wy, double wz, double wf,
                double wl, double wu) {

            this->wx = wx;
            this->wy = wy;
            this->wz = wz;
            this->wf = wf;
            this->wl = wl;
            this->wu = wu;

        }

    };

    struct VelocityAccuracy {
        double pos_accuracy;
        double vel_accuracy;

        VelocityAccuracy() {
        }

        VelocityAccuracy(double pos_accuracy, double vel_accuracy) :
        pos_accuracy(pos_accuracy), vel_accuracy(vel_accuracy) {
        }

        void setVelocityAccuracy(double pos_accuracy, double vel_accuracy) {
            this->pos_accuracy = pos_accuracy;
            this->vel_accuracy = vel_accuracy;
        }

    };

    struct GPSMode {
        int posmode;
        int velmode;
        int orimode;

        GPSMode() {
        }

        GPSMode(int posmode, int velmode, int orimode) : posmode(posmode),
        velmode(velmode), orimode(orimode) {
        }

        void setGPSMode(int posmode, int velmode, int orimode) {
            this->posmode = posmode;
            this->velmode = velmode;
            this->orimode = orimode;
        }
    };

public:

    GeoGoordinates geoCoordinates;
    Rotation rotation;
    Velocity velocity;
    Acceleration acceleration;
    AngularRateAround angularRateAround;
    VelocityAccuracy velocityAccuracy;
    int navigationStatus;
    int numSatelites;
    GPSMode gpsMode;

    // constructor / deconstructor

public:

    OxtsData() {

    }

    OxtsData(std::string line) {

        std::string token;
        std::stringstream data_row(line);
        std::vector<double> tokens;

        while (getline(data_row, token, ' ')) {
            tokens.push_back(atof(token.c_str()));
        }

        geoCoordinates.setGeoGoordinates(tokens[0], tokens[1], tokens[2]);
        rotation.setRotation(tokens[3], tokens[4], tokens[5]);
        velocity.setVelocity(tokens[6], tokens[7], tokens[8], tokens[9],
                tokens[10]);
        acceleration.setAcceleration(tokens[11], tokens[12], tokens[13],
                tokens[14], tokens[15], tokens[16]);
        angularRateAround.setAngularRateAround(tokens[17], tokens[18],
                tokens[19], tokens[20], tokens[21], tokens[22]);
        velocityAccuracy.setVelocityAccuracy(tokens[23], tokens[24]);
        navigationStatus = (int) tokens[25];
        numSatelites = (int) tokens[26];
        gpsMode.setGPSMode((int) tokens[27], (int) tokens[28],
                (int) tokens[29]);
    }

    ~OxtsData() {
    }

};

