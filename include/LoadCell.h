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
    void read_raw(int num_samples = 100);
    void zero();
    void set_friction_offset(float estimated_friction_force);
    float friction_compensation(float calculated_force);

private:
    float _calibration_slope = 0.0001124489699;  // 0.0001093948591;  // 0.000108998498;   // 0.000112664059;
    float _calibration_intercept = -12.68471136; //-11.61966783; //-11.38810401; //-11.60340583;
    float _estimated_friction_force = 0.0;       // 0.52;
    float _offset = 0.0;
    float _alpha = 0.1;
    float _prev_force = 0.0;
    float _prev_counts = 0.0;
};

#endif