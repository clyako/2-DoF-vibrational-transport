#include "Controller.h"

Controller::Controller() {};

void Controller::initialize(int PWM_A_PIN, int PWM_B_PIN, int SLP)
{
    pinMode(SLP, OUTPUT);
    digitalWrite(SLP, LOW);
#if defined(PWM_FREQ_35000)
    {
        pwm_frequency = 35000;
        num_bits = 12;
        max_read_val = pow(2, num_bits) - 1;
    }
#elif defined(PWM_FREQ_120000)
    {
        pwm_frequency = 120000;
        num_bits = 10;
        max_read_val = pow(2, num_bits) - 1;
    }
#endif

    _PWM_A_PIN = PWM_A_PIN;
    _PWM_B_PIN = PWM_B_PIN;
    // motor control setup
    pinMode(_PWM_A_PIN, OUTPUT);
    pinMode(_PWM_B_PIN, OUTPUT);
    digitalWrite(_PWM_A_PIN, LOW);
    digitalWrite(_PWM_B_PIN, LOW);
    analogWriteFrequency(_PWM_A_PIN, pwm_frequency);
    analogWriteFrequency(_PWM_B_PIN, pwm_frequency);
    analogWriteResolution(num_bits);

    digitalWrite(SLP, HIGH);

    stop_motor();
}

void Controller::compute_control_signal(int &direction, int &motor_pwm, float target_position, float current_position)
{
    float error = target_position - current_position;
    float error_derivative = error - _prev_error;
    float control_signal = error * _kp + error_derivative * _kd;

    _prev_error = error;

    direction = (control_signal > 0) - (control_signal < 0);
    motor_pwm = constrain(abs(control_signal), 0, max_read_val);
}

void Controller::set_gains(float kp, float kd, float closed_loop_sample_time)
{
    _kp = kp;
    _kd = kd / (closed_loop_sample_time / 1e6);
}

void Controller::drive_motor(int direction, int speed)
{
    if (direction == 1)
    {
        analogWrite(_PWM_A_PIN, LOW);
        analogWrite(_PWM_B_PIN, speed);
    }
    else
    {
        analogWrite(_PWM_A_PIN, speed);
        analogWrite(_PWM_B_PIN, LOW);
    }
}

void Controller::stop_motor()
{
    analogWrite(_PWM_A_PIN, LOW);
    analogWrite(_PWM_B_PIN, LOW);
}

void Controller::go_to_end_stop()
{
    drive_motor(0, _zeroing_command);
}