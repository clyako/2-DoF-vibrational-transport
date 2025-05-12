#ifndef ForceMotor_h
#define ForceMotor_h
#include <Arduino.h>
#include "Controller.h"

class ForceMotor : public Controller
{
public:
    ForceMotor();
    void force_control(float target_position, float current_position);
    void retract(uint32_t retract_time = 4000);

private:
        // for driving motor
    int _PWM_A_PIN;
    int _PWM_B_PIN;
    int _max_speed = 1000;

    // force control
    float _prev_error = 0;
    float _error_sum = 0;
    float _windup = 200;
    float _kp = 1000;
    float _kd = 0;
    float _ki = 30;

    elapsedMillis _force_control_timer;
    uint32_t _force_control_period = 25;
};

#endif