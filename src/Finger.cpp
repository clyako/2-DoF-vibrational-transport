#include "Finger.h"

Finger::Finger(int motor_1_pwm_A, int motor_1_pwm_B, int motor_1_slp,
               int motor_2_pwm_A, int motor_2_pwm_B, int motor_2_slp,
               int encoder_1_channel_num, int encoder_1_channel_A, int encoder_1_channel_B,
               int encoder_2_channel_num, int encoder_2_channel_A, int encoder_2_channel_B,
               float sampling_rate)
    : _inputs(),
      _motor_1(),
      _motor_2(),
      _encoder_1(encoder_1_channel_num, encoder_1_channel_A, encoder_1_channel_B),
      _encoder_2(encoder_2_channel_num, encoder_2_channel_A, encoder_2_channel_B),
      _waveform(quaid_frequency, min_acceleration_gs, max_acceleration_gs, sampling_rate)
{
    _motor_1_pwm_A = motor_1_pwm_A;
    _motor_1_pwm_B = motor_1_pwm_B;
    _motor_2_pwm_A = motor_2_pwm_A;
    _motor_2_pwm_B = motor_2_pwm_B;

    _motor_1_slp = motor_1_slp;
    _motor_2_slp = motor_2_slp;
};

/*
 * ONLY DO THIS IF IT CANNOT BE DONE IN THE CONSTRUCTOR (SPI must happen in setup not before)
 */
void Finger::initialize()
{
    _inputs.initialize();

    _motor_1.initialize(_motor_1_pwm_A, _motor_1_pwm_B, _motor_1_slp);
    _motor_2.initialize(_motor_2_pwm_A, _motor_2_pwm_B, _motor_2_slp);

    _encoder_1.initialize();
    _encoder_2.initialize();

    // calibrate encoders
    _motor_1.go_to_end_stop();
    _motor_2.go_to_end_stop();

    delay(1000);

    _encoder_1.calibrate();
    _encoder_2.calibrate();

    delay(100);

    // set gains
    // _motor_1.set_gains(2000, 3.7, (float)_control_loop_period); // right motor
    // _motor_2.set_gains(2000, 3.7, (float)_control_loop_period); // left motor

    _motor_1.set_gains(4500, 6.0, (float)_control_loop_period); // right motor
    _motor_2.set_gains(4500, 6.0, (float)_control_loop_period); // left motor

    _motor_1.stop_motor();
    _motor_2.stop_motor();
}

void Finger::run()
{
    _inputs.update_power_switch();
    if (_inputs.run_device)
    {
        if (_control_loop_timer > _control_loop_period)
        {
            _control_loop_timer = 0;
            // add interval timer
            get_target_positions(_motor_1_target_position, _motor_2_target_position);
            drive_motors(_motor_1_target_position, _motor_2_target_position);
        }
    }
    else
    {
        _motor_1.stop_motor();
        _motor_2.stop_motor();
    }
}

void Finger::drive_motors(float _motor_1_target_position, float _motor_2_target_position)
{
    unsigned long timestamp = millis();

    float _motor_1_current_position = _encoder_1.read_position();
    float _motor_2_current_position = _encoder_2.read_position();

    _motor_1.compute_control_signal(_motor_1_direction, _motor_1_pwm, _motor_1_target_position, _motor_1_current_position);
    _motor_2.compute_control_signal(_motor_2_direction, _motor_2_pwm, _motor_2_target_position, _motor_2_current_position);

    // want to drive the two motors at the same time, that's why the control signals are both computed first
    _motor_1.drive_motor(_motor_1_direction, _motor_1_pwm);
    _motor_2.drive_motor(_motor_2_direction, _motor_2_pwm);

    if (plotting && _plot_timer > _plot_period) // add printing period here as well
    {
        _plot_timer = 0;

        Serial.write((byte *)&timestamp, 4);                 // Send 4 bytes
        Serial.write((byte *)&_motor_1_target_position, 4);  // Send 4 bytes
        Serial.write((byte *)&_motor_1_current_position, 4); // Send 4 bytes
        Serial.write((byte *)&_motor_2_target_position, 4);  // Send 4 bytes
        Serial.write((byte *)&_motor_2_current_position, 4); // Send 4 bytes
    }

    _toggle_pin();
}

void Finger::get_target_positions(float &_motor_1_target_position, float &_motor_2_target_position)
{
    // get quaid position
    float position = _waveform.get_waveform_data();
    // read two switches to see if rotation or translation and direction
    _inputs.update_direction_switch();
    _inputs.update_mode_switch();

    if (_inputs.mode == Mode::Translation)
    {
        if (_inputs.direction == Direction::Forward)
        {
            _motor_1_multiplier = 1;
            _motor_2_multiplier = 1;
        }
        else
        {
            _motor_1_multiplier = -1;
            _motor_2_multiplier = -1;
        }
    }
    else
    { // Rotation
        if (_inputs.direction == Direction::Forward)
        {
            _motor_1_multiplier = 1;
            _motor_2_multiplier = -1;
        }
        else
        {
            _motor_1_multiplier = -1;
            _motor_2_multiplier = 1;
        }
    }

    _motor_1_target_position = position * _motor_1_multiplier;
    _motor_2_target_position = position * _motor_2_multiplier;
}

void Finger::input_check(int num_times_to_flip_switch)
{
    auto check_switch = [&](const char *label, auto update_func, auto &current_state, auto print_state)
    {
        update_func();
        auto prev_state = current_state;
        Serial.print(label);
        Serial.print(": ");
        print_state(prev_state);

        int count = 0;
        while (count < num_times_to_flip_switch)
        {
            update_func(); // Directly call the lambda function
            if (current_state != prev_state)
            {
                prev_state = current_state;
                Serial.print(label);
                Serial.print(": ");
                print_state(prev_state);
                count++;
            }
        }
    };

    check_switch("Run device", [&]()
                 { _inputs.update_power_switch(); }, _inputs.run_device, [](bool state)
                 { Serial.println(state ? "On" : "Off"); });

    check_switch("Direction", [&]()
                 { _inputs.update_direction_switch(); }, _inputs.direction, [](Direction state)
                 { Serial.println(state == Direction::Forward ? "Forward" : "Backward"); });

    check_switch("Mode", [&]()
                 { _inputs.update_mode_switch(); }, _inputs.mode, [](Mode state)
                 { Serial.println(state == Mode::Translation ? "Translation" : "Rotation"); });
}

void Finger::encoder_check()
{
    _encoder_1.print_position_change(1);
    // _encoder_2.print_position_change(2);
}

void Finger::_toggle_pin()
{
    _control_pin_state = !_control_pin_state;
    digitalWrite(CONTROL_LOOP_PIN, _control_pin_state);
}