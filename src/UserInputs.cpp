#include "UserInputs.h"

UserInputs::UserInputs() : power_rocker(), mode_rocker(), direction_rocker() {};

void UserInputs::initialize()
{
    power_rocker.attach(POWER_ROCKER_PIN, INPUT_PULLUP);
    direction_rocker.attach(DIRECTION_ROCKER_PIN, INPUT_PULLUP);
    mode_rocker.attach(MODE_ROCKER_PIN, INPUT_PULLUP);

    power_rocker.interval(_debounce_time);
    mode_rocker.interval(_debounce_time);
    direction_rocker.interval(_debounce_time);

    unsigned long start_time = millis();
    unsigned long end_time = 500;
    while (millis() - start_time < end_time)
    {
        update_switches();
    }
}

void UserInputs::update_switches()
{
    update_power_switch();
    update_direction_switch();
    update_mode_switch();
}

void UserInputs::update_power_switch()
{
    power_rocker.update();
    run_device = (power_rocker.read() == LOW) ? true : false;
}

void UserInputs::update_mode_switch()
{
    mode_rocker.update();
    mode = (mode_rocker.read() == LOW) ? Mode::Rotation : Mode::Translation;
}

void UserInputs::update_direction_switch()
{
    direction_rocker.update();
    direction = (direction_rocker.read() == LOW) ? Direction::Backward : Direction::Forward;
}
