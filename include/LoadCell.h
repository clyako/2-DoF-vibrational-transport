#ifndef LoadCell_h
#define LoadCell_h
#include <Arduino.h>
#include "HX711.h"

#define DATA_PIN 26
#define CLOCK_PIN 27

class LoadCell : public HX711
{
public:
    LoadCell();
    void initialize();
    void read_non_blocking(float &force, uint32_t &force_timestamp);

private:
    float _calibration_slope = 0.0;
    float _calibration_intercept = 0.0;
};

#endif