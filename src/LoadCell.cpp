#include "LoadCell.h"

LoadCell::LoadCell() : HX711() {}

void LoadCell::initialize()
{
    begin(DATA_PIN, CLOCK_PIN);
    delay(200);
}

void LoadCell::read_non_blocking(float &force, uint32_t &force_timestamp)
{
    if (is_ready())
    {
        force = _calibration_slope * read() + _calibration_intercept + _estimated_friction_force - _offset;
        force_timestamp = time_of_last_read();
    }
}

void LoadCell::read_non_blocking_filtered(float &force, uint32_t &force_timestamp)
{
    if (is_ready())
    {
        float unfiltered_force = _calibration_slope * read() + _calibration_intercept + _estimated_friction_force - _offset;
        force = unfiltered_force * _alpha + _prev_force * (1 - _alpha);
        _prev_force = force;
        force_timestamp = time_of_last_read();
    }
}

void LoadCell::read_raw()
{
    Serial.println(read());
}

void LoadCell::zero()
{
    float offset_value = _calibration_slope * read_average(10) + _calibration_intercept;
    _offset = offset_value;
}

void LoadCell::set_friction_offset(float estimated_friction_force)
{
    _estimated_friction_force = estimated_friction_force;
}

float LoadCell::friction_compensation(float calculated_force)
{

    float compensation_amount = 0.0;

    if (calculated_force < 0.0)
    {
        if (calculated_force > -4.5)
        {
            compensation_amount = 0.0515 * calculated_force + 0.691;
        }
        else
        {
            compensation_amount = -0.00154 * calculated_force + 0.417;
        }
    }
    return compensation_amount;
}
