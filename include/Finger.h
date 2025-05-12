#ifndef Finger_h
#define Finger_h
#include <Arduino.h>
#include "Controller.h"
#include "UserInputs.h"
#include "LinearEncoder.h"
#include "QuaidWaveform.h"
#include "QuaidWaveformSelector.h"

#define CONTROL_LOOP_PIN 39
#define CONTROL_LOOP_FREQUENCY 40000

class Finger
{
public:
    Finger(int motor_1_pwm_A, int motor_1_pwm_B, int motor_1_slp,
           int motor_2_pwm_A, int motor_2_pwm_B, int motor_2_slp,
           int encoder_1_channel_num, int encoder_1_channel_A, int encoder_1_channel_B,
           int encoder_2_channel_num, int encoder_2_channel_A, int encoder_2_channel_B,
           float sampling_rate = CONTROL_LOOP_FREQUENCY);
    void initialize();
    void run();
    void stop();
    void drive_motors(float _motor_1_position, float _motor_2_position);
    void get_target_positions(float &_motor_1_position, float &_motor_2_position);
    bool power_switch();
    void input_check(int num_times_to_flip_switch = 3);
    void encoder_check();

    bool plotting = false;

private:
    UserInputs _inputs;
    Controller _motor_1, _motor_2;
    LinearEncoder _encoder_1, _encoder_2;
    QuaidWaveform _waveform;

    float _motor_1_target_position;
    float _motor_2_target_position;
    int _motor_1_multiplier = 1;
    int _motor_2_multiplier = 1;
    int _motor_1_direction;
    int _motor_1_pwm;
    int _motor_2_direction;
    int _motor_2_pwm;

    int _motor_1_pwm_A;
    int _motor_1_pwm_B;
    int _motor_2_pwm_A;
    int _motor_2_pwm_B;

    int _motor_1_slp;
    int _motor_2_slp;

    // for control loop
    elapsedMicros _control_loop_timer;
    unsigned long _control_loop_period = (int)(1e6 / ((float)CONTROL_LOOP_FREQUENCY)); // 25 µs (40 kHz)

    // values for plotting
    unsigned long _plot_period = 1000; // 1 ms
    elapsedMicros _plot_timer;

    // toggling digital pin for control loop frequency verification
    // for verifying control loop speed
    void _toggle_pin();
    bool _control_pin_state = LOW;
};

#endif