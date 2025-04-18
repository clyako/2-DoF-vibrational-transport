#include "LoadCell.h"

LoadCell::LoadCell() : HX711() {}

void LoadCell::initialize()
{
    begin(DATA_PIN, CLOCK_PIN);
    delay(200);
    tare();
}

void LoadCell::read_non_blocking(float &force, uint32_t &force_timestamp)
{
    if (is_ready())
    {
        force = _calibration_slope * read() + _calibration_intercept;
        force_timestamp = last_read();
    }
}
