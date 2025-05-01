#include <Arduino.h>
#include "Finger.h"
#include "PinDefines.h"
#include "LoadCell.h"
#include "ForceMotor.h"

void log_object_position_and_force_data();

// #define ENCODER_TEST
#define OBJECT_ENCODER_TEST
// #define FORCE_MOTOR_TEST
// #define INPUT_TEST
// #define LOAD_CELL_CALIBRATION
// #define FORCE_VELOCITY_EXPERIMENT
// #define PLOT
// #define LOG

Finger finger = Finger(MOTOR_1_PWM_A, MOTOR_1_PWM_B, MOTOR_1_SLP,
                       MOTOR_2_PWM_A, MOTOR_2_PWM_B, MOTOR_2_SLP,
                       ENCODER_1_CHANNEL_NUM, ENCODER_1_CHANNEL_A, ENCODER_1_CHANNEL_B,
                       ENCODER_2_CHANNEL_NUM, ENCODER_2_CHANNEL_A, ENCODER_2_CHANNEL_B);

// object encoder
LinearEncoder object_encoder = LinearEncoder(ENCODER_3_CHANNEL_NUM, ENCODER_3_CHANNEL_A, ENCODER_3_CHANNEL_B);

// force motor
float target_force = -4.0; // N
ForceMotor force_motor = ForceMotor();

// load cell stuff
LoadCell load_cell;
float object_force = 0.0;
uint32_t force_timestamp = 0;
uint8_t load_cell_zeroed = false;

// stuff for logging data
elapsedMillis logging_timer;
unsigned long logging_period = 1000; // log every ms

elapsedMillis print_timer;
unsigned long print_period = 200;

void setup()
{
  Serial.begin(115200);
  finger.initialize();

#if defined(PLOT)
  finger.plotting = true;
#endif

  object_encoder.initialize();
  object_encoder.set_slope(-0.0025);
  object_encoder.end_stop_position = 0.0;
  object_encoder.calibrate(); // will this zero it enough?

  load_cell.initialize();

  // reset logging timer
  logging_timer = 0;

  force_motor.initialize(MOTOR_3_PWM_A, MOTOR_3_PWM_B, MOTOR_3_SLP);
  // force_motor.retract();

  load_cell.zero();
}

void loop()
{
#if defined(ENCODER_TEST)
  finger.encoder_check();
#elif defined(OBJECT_ENCODER_TEST)
  object_encoder.print_position_change(3);
#elif defined(INPUT_TEST)
  finger.input_check();
#elif defined(LOAD_CELL_CALIBRATION)
  // load_cell.read_raw();
  delay(500);
  load_cell.read_non_blocking(object_force, force_timestamp);
  Serial.println(object_force, 3);
#elif defined(FORCE_MOTOR_TEST)
  if (!load_cell_zeroed)
  {
    force_motor.zeroing_routine();
    delay(3000);
    load_cell.zero();
    load_cell_zeroed = true;
  }
  load_cell.read_non_blocking_filtered(object_force, force_timestamp);
  force_motor.force_control(target_force, object_force);

  if (print_timer > print_period)
  {
    print_timer = 0;
    Serial.println(object_force);
  }
#elif defined(FORCE_VELOCITY_EXPERIMENT)
  if (!load_cell_zeroed)
  {
    // change retract until the force is zero (need to uncompress the spring, can't go into tension)
    // need to change time and speed so this is always the case
    force_motor.zeroing_routine();
    delay(3000);
    load_cell.zero();
    load_cell_zeroed = true;
  }
  else
  {
    finger.run();
#if defined(LOG)
    log_object_position_and_force_data();
#endif
  }
#else
  finger.run();
#if defined(LOG)
  log_object_position_and_force_data();
#endif
#endif
}

void log_object_position_and_force_data()
{
  if (logging_timer > logging_period)
  {
    logging_timer = 0;

    // get object position and applied force
    unsigned long timestamp = micros();
    float object_position = object_encoder.read_position();
    load_cell.read_non_blocking(object_force, force_timestamp); // SHOULD THIS USE THE FILTERED VALUE?

    Serial.write((byte *)&timestamp, 4);       // Send 4 bytes
    Serial.write((byte *)&object_position, 4); // Send 4 bytes
    Serial.write((byte *)&force_timestamp, 4); // Send 4 bytes
    Serial.write((byte *)&object_force, 4);    // Send 4 bytes
  }
}