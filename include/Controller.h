#ifndef Controller_h
#define Controller_h
#include <Arduino.h>
#include "LinearEncoder.h"

#define PWM_FREQ_35000
// #define PWM_FREQ_120000

class Controller
{
public:
    Controller();
    void initialize(int PWM_A_PIN, int PWM_B_PIN, int SLP);
    void compute_control_signal(int &direction, int &motor_pwm, float target_position, float current_position);
    void set_gains(float kp, float kd, float closed_loop_sample_time);
    void drive_motor(int direction, int speed);
    void stop_motor();
    void go_to_end_stop();

    int pwm_frequency;
    int num_bits;
    int max_read_val;

private:
    // for driving motor
    int _PWM_A_PIN;
    int _PWM_B_PIN;

    // calibrating encoder
    int _zeroing_command = 100;

    // open loop variables
    float _control_voltage; // voltage to send in open loop mode

    // position control
    float _prev_error = 0;
    float _kp = 0;
    float _kd = 0;

    // values for printing to the console
    unsigned long _print_period = 1000; // 1 ms
    elapsedMicros _print_timer;
};

#endif