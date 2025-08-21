#include "ForceMotor.h"

ForceMotor::ForceMotor() : Controller() {};

void ForceMotor::force_control(float target_force, float current_force)
{
    if (_force_control_timer > _force_control_period)
    {
        _force_control_timer = 0;

        float error = (target_force - current_force);
        _error_sum += error;
        _error_sum = constrain(_error_sum, -_windup, _windup);
        float error_derivative = error - _prev_error;
        float control_signal = error * _kp + error_derivative * _kd + _error_sum * _ki;

        _prev_error = error;

        int direction = (control_signal > 0) - (control_signal < 0);
        int motor_pwm = constrain(abs(control_signal), 0, _max_speed);

        drive_motor(direction, motor_pwm);
    }
}

void ForceMotor::retract()
{
    drive_motor(1, 4000);
}