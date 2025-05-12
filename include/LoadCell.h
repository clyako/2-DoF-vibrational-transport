#ifndef LoadCell_h
#define LoadCell_h
#include <Arduino.h>
#include "HX711.h"

#define DATA_PIN 27
#define CLOCK_PIN 26

class LoadCell : public HX711
{
public:
    LoadCell();
    void initialize();
    void read_non_blocking(float &force, uint32_t &force_timestamp);
    void read_non_blocking_filtered(float &force, uint32_t &force_timestamp);
    void read_raw();
    void zero();
    void set_friction_offset(float estimated_friction_force);

private:
    float _calibration_slope = 0.000112664059;
    float _calibration_intercept = -11.60340583;
    float _estimated_friction_force = -0.3;
    float _offset = 0.0;
    float _alpha = 0.7;
    float _prev_force = 0.0;
    float _prev_counts = 0.0;
};

#endif