#include "QuaidWaveform.h"

QuaidWaveform::QuaidWaveform(float _frequency, float _a_min_gs, float _a_max_gs, float sampling_rate)
{
    _period = 1e6 / _frequency;                       // [µs]
    _a_min = _a_min_gs * 9.81 / 1e9;                  // [mm/µs^2]
    _a_max = _a_max_gs * 9.81 / 1e9;                  // [mm/µs^2]
    _t1 = (_a_max / (_a_max + _a_min)) * _period / 2; // [µs]
    _t1_sq = _t1 * _t1;
    _period_sq = _period * _period;
    _set_offset();

    // create the array to be populated with precomputed values
    // period [µs] * (samping rate [Hz] / 1e6 [s / µs])
    _num_samples_int = (int)(_period * (sampling_rate / 1e6));
    _num_samples_float = (float)_num_samples_int;
    _position_table = new float[_num_samples_int];

    _precompute_waveform();
}

QuaidWaveform::~QuaidWaveform()
{
    delete[] _position_table;
}

void QuaidWaveform::_precompute_waveform()
{
    for (int i = 0; i < _num_samples_int; i++)
    {
        float periodic_t = ((float)i) * (_period / _num_samples_float);
        float periodic_t_sq = periodic_t * periodic_t;

        if (periodic_t <= _t1)
        {
            _position_table[i] = 0.5f * _a_min * periodic_t_sq + offset;
        }
        else if (_t1 < periodic_t && periodic_t <= _period - _t1)
        {
            _position_table[i] = _a_min * _t1 * (periodic_t - 0.5f * _t1) + _a_max * (_t1 * periodic_t - 0.5f * periodic_t_sq - 0.5f * _t1_sq) + offset;
        }
        else
        {
            _position_table[i] = _a_min * (0.5f * periodic_t_sq - _period * periodic_t + 0.5f * _period_sq) + offset;
        }
    }
}

float QuaidWaveform::get_waveform_data()
{
    float position = _position_table[_position_index];
    _position_index++;

    if (_position_index >= _num_samples_int)
    {
        _position_index = 0;
    }

    return position;
}

void QuaidWaveform::_set_offset()
{
    float time_at_max_position = _t1 * (_a_min / _a_max + 1);
    float max_position = _a_min * _t1 * (time_at_max_position - 0.5f * _t1) + _a_max * (_t1 * time_at_max_position - 0.5f * pow(time_at_max_position, 2) - 0.5f * pow(_t1, 2));
    float amplitude = max_position;
    offset = -amplitude / 2;
}
