#include <Arduino.h>
#include "PinDefines.h"
#include "LoadCell.h"
#include "ForceMotor.h"
#include "LinearEncoder.h"
#include "UserInputs.h"

void log_position_and_force_data();

// #define LOAD_CELL_CALIBRATION
// #define MOTOR_TEST
#define ENCODER_TEST
// #define TEST
// #define STATIC
// #define KINETIC

// load cell stuff
LoadCell load_cell;
float object_force = 0.0;
uint32_t force_timestamp = 0;

elapsedMillis print_timer;
unsigned long print_period = 200;

// values for each test
unsigned long static_test_timeout = 10000000;
int static_motor_speed = 700;
unsigned long kinetic_test_timeout = 10000000;
int kinetic_motor_speed = 2000;
float kinetic_test_multiplier = 1;

elapsedMicros test_timer;
unsigned long test_timeout;

// force motor
ForceMotor force_motor = ForceMotor();
int motor_speed;

// encoder
LinearEncoder encoder = LinearEncoder(ENCODER_3_CHANNEL_NUM, ENCODER_3_CHANNEL_A, ENCODER_3_CHANNEL_B);

// input switch
UserInputs inputs = UserInputs();

// stuff for logging data
elapsedMillis logging_timer;
unsigned long logging_period = 1; // log every ms

// state machine states
uint8_t REMOVE_MASS_AND_HOLDER = 0;
uint8_t ZERO_LOAD_CELL = 1;
uint8_t ADD_MASS_AND_HOLDER = 2;
uint8_t RUN_TEST = 3;
uint8_t STOP_TEST = 4;
uint8_t STATE = REMOVE_MASS_AND_HOLDER;

void setup()
{
    Serial.begin(115200);

    encoder.initialize();
    encoder.set_slope(-0.005);
    encoder.end_stop_position = 0.0;
    encoder.calibrate();

    load_cell.initialize();

    force_motor.initialize(MOTOR_3_PWM_A, MOTOR_3_PWM_B, MOTOR_3_SLP);

    inputs.initialize();

#if defined(TEST)
#if defined(STATIC)
    test_timeout = static_test_timeout;
    motor_speed = static_motor_speed;
#elif defined(KINETIC)
    test_timeout = kinetic_test_timeout * kinetic_test_multiplier;
    motor_speed = kinetic_motor_speed / kinetic_test_multiplier;
#endif
#endif
    test_timer = 0;
}

void loop()
{
#if defined(LOAD_CELL_CALIBRATION)
    // load_cell.read_raw();
    delay(500);
    load_cell.read_non_blocking(object_force, force_timestamp);
    Serial.print("Force = ");
    Serial.print(object_force, 3);
    Serial.println(" N");
    // Serial.print("Grams = ");
    // Serial.print(object_force / 9.81 * 1000, 3);
    // Serial.println(" g");
#elif defined(MOTOR_TEST)
    force_motor.drive_motor(0, 1000);
    delay(4000);
    force_motor.stop_motor();
    delay(20000);
#elif defined(ENCODER_TEST)
    test_timer = 0;
    while (test_timer < 5000000)
    {
        force_motor.drive_motor(1, 4000);
        Serial.print("Position: ");
        Serial.println(encoder.read_position(), 2);
    }
    test_timer = 0;
    while (test_timer < 5000000)
    {
        force_motor.drive_motor(0, 4000);
        Serial.print("Position: ");
        Serial.println(encoder.read_position(), 2);
    }
#elif defined(TEST)
    if (STATE == REMOVE_MASS_AND_HOLDER)
    {
        inputs.update_power_switch();
        if (inputs.run_device)
        {
            delay(200);
            STATE = ZERO_LOAD_CELL;
        }
    }
    else if (STATE == ZERO_LOAD_CELL)
    {
        load_cell.zero();
        delay(200);
        STATE = ADD_MASS_AND_HOLDER;
    }
    else if (STATE == ADD_MASS_AND_HOLDER)
    {
        inputs.update_power_switch();
        if (!inputs.run_device)
        {
            delay(200);
            test_timer = 0;
            STATE = RUN_TEST;
        }
    }
    else if (STATE == RUN_TEST)
    {
        inputs.update_power_switch();
        // if (test_timer > test_timeout)
        if (inputs.run_device)
        {
            delay(1000);
            test_timer = 0;
            STATE = STOP_TEST;
        }

        force_motor.drive_motor(1, motor_speed);

        log_position_and_force_data();
    }
    else if (STATE == STOP_TEST)
    {
        inputs.update_power_switch();
        // if (test_timer > test_timeout)
        if (!inputs.run_device)
        {
            force_motor.stop_motor();
        }
        else
        {
            force_motor.drive_motor(0, 4000);
        }
    }
    else
    {
        force_motor.stop_motor();
    }
#endif
}

void log_position_and_force_data()
{
    if (logging_timer > logging_period)
    {
        logging_timer = 0;

        // get object position and applied force
        unsigned long timestamp = micros();
        float object_position = encoder.read_position();
        load_cell.read_non_blocking(object_force, force_timestamp); // SHOULD THIS USE THE FILTERED VALUE?

        Serial.write((byte *)&timestamp, 4);       // Send 4 bytes
        Serial.write((byte *)&object_position, 4); // Send 4 bytes
        Serial.write((byte *)&force_timestamp, 4); // Send 4 bytes
        Serial.write((byte *)&object_force, 4);    // Send 4 bytes
    }
}