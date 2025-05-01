#include "LinearEncoder.h"

LinearEncoder::LinearEncoder(int _CHANNEL_NUM, int _A_CHANNEL, int _B_CHANNEL) : QuadEncoder(_CHANNEL_NUM, _A_CHANNEL, _B_CHANNEL) {}

void LinearEncoder::initialize(uint8_t filter_count, uint8_t filter_sample_period, float encoder_direction)
{
    setInitConfig();
    EncConfig.filterCount = filter_count;
    EncConfig.filterSamplePeriod = filter_sample_period;
    _encoder_direction = encoder_direction;
    init();
}

float LinearEncoder::read_position()
{
    return ((float)read()) * _encoder_slope * _encoder_direction + end_stop_position;
}

void LinearEncoder::print_position_change(int encoder_num)
{
    _position_raw = read();
    if (_position_raw != _prev_position_raw)
    {
        Serial.print("Encoder ");
        Serial.print(encoder_num);
        Serial.print(" position = ");
        Serial.print(((float)_position_raw) * _encoder_slope * _encoder_direction + end_stop_position);
        Serial.println(" mm");
        _prev_position_raw = _position_raw;
    }
}

void LinearEncoder::calibrate()
{
    setConfigInitialPosition();
}

void LinearEncoder::set_slope(float encoder_slope)
{
    _encoder_slope = encoder_slope;
}