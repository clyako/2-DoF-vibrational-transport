#ifndef QuaidWaveform_h
#define QuaidWaveform_h
#include <Arduino.h>

class QuaidWaveform
{
public:
    QuaidWaveform(float _frequency, float _a_min_gs, float _a_max_gs, float sampling_rate = 40000);
    ~QuaidWaveform();
    float get_waveform_data();

    float position_min = 3;
    float position_max = 3;
    float offset = 0;

private:
    void _set_offset();
    void _precompute_waveform();
    float _period;
    float _a_min;
    float _a_max;
    float _t1;
    float _t1_sq;
    float _period_sq;
    int _num_samples_int;
    float _num_samples_float;
    float *_position_table;
    int _position_index = 0;
};
#endif
