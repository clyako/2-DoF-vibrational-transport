#ifndef LinearEncoder_h
#define LinearEncoder_h
#include <Arduino.h>
#include "QuadEncoder.h"

#define FILTER_COUNT 0
#define FILTER_SAMPLE_PERIOD 5

class LinearEncoder : public QuadEncoder
{
public:
    LinearEncoder(int _CHANNEL_NUM, int _A_CHANNEL, int _B_CHANNEL);
    void initialize(uint8_t filter_count = FILTER_COUNT, uint8_t filter_sample_period = FILTER_SAMPLE_PERIOD, float encoder_direction = 1.0);
    float read_position();
    void print_position_change(int encoder_num);
    void calibrate();
    void set_slope(float encoder_slope);
    float end_stop_position = -3.05;

private:
    long _position_raw = 0;
    long _prev_position_raw = 0;
    float _encoder_slope = 0.005;
    float _encoder_direction = 1.0;
};

#endif