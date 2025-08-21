#include <Arduino.h>
#include "Bounce2.h"
#include "ForceMotor.h"

#define POWER_PIN 4
#define DIRECTION_PIN 5
#define PWM_A_PIN 28
#define PWM_B_PIN 29
#define SPEED_PIN 22

Bounce power_rocker;
Bounce direction_rocker;

int analog_write_resolution = 12;
int pwm_frequency = 20000;
int debounce_time = 20;

void setup()
{
    Serial.begin(115200);
    analogWriteResolution(analog_write_resolution);
    analogWriteFrequency(PWM_A_PIN, pwm_frequency);
    analogWriteFrequency(PWM_B_PIN, pwm_frequency);

    pinMode(PWM_A_PIN, OUTPUT);
    pinMode(PWM_B_PIN, OUTPUT);
    digitalWrite(PWM_A_PIN, LOW);
    digitalWrite(PWM_B_PIN, LOW);

    power_rocker.attach(POWER_PIN, INPUT_PULLUP);
    power_rocker.interval(debounce_time);

    direction_rocker.attach(DIRECTION_PIN, INPUT_PULLUP);
    direction_rocker.interval(debounce_time);

    unsigned long start_time = millis();
    unsigned long end_time = 500;
    while (millis() - start_time < end_time)
    {
        power_rocker.update();
        direction_rocker.update();
    }
}

void loop()
{
    power_rocker.update();
    direction_rocker.update();

    if (power_rocker.read() == LOW)
    {
        int speed_pot_value = analogRead(SPEED_PIN);
        int direction = direction_rocker.read();

        if (direction == LOW)
        {
            analogWrite(PWM_A_PIN, LOW);
            analogWrite(PWM_B_PIN, speed_pot_value);
        }
        else
        {
            analogWrite(PWM_A_PIN, speed_pot_value);
            analogWrite(PWM_B_PIN, LOW);
        }
    }
    else
    {
        analogWrite(PWM_A_PIN, LOW);
        analogWrite(PWM_B_PIN, LOW);
    }
}