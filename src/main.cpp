#include <Arduino.h>
#include "Finger.h"
#include "PinDefines.h"
#include "LoadCell.h"

void log_object_position_and_force_data();

// #define ENCODER_TEST
// #define INPUT_TEST
// #define PLOT
#define LOG

Finger finger = Finger(MOTOR_1_PWM_A, MOTOR_1_PWM_B, MOTOR_1_SLP,
                       MOTOR_2_PWM_A, MOTOR_2_PWM_B, MOTOR_2_SLP,
                       ENCODER_1_CHANNEL_NUM, ENCODER_1_CHANNEL_A, ENCODER_1_CHANNEL_B,
                       ENCODER_2_CHANNEL_NUM, ENCODER_2_CHANNEL_A, ENCODER_2_CHANNEL_B);

// object encoder
LinearEncoder object_encoder = LinearEncoder(ENCODER_3_CHANNEL_NUM, ENCODER_3_CHANNEL_A, ENCODER_3_CHANNEL_B);
// load cell stuff
LoadCell load_cell;
float object_force = 0.0;
uint32_t force_timestamp = 0;

// stuff for logging data
elapsedMillis logging_timer;
unsigned long logging_period = 1000; // log every ms

void setup()
{
  Serial.begin(115200);
  finger.initialize();

#if defined(PLOT)
  finger.plotting = true;
#endif

  object_encoder.initialize();
  object_encoder.calibrate(); // will this zero it enough?

  load_cell.initialize();

  // reset logging timer
  logging_timer = 0;
}

void loop()
{
#if defined(ENCODER_TEST)
  finger.encoder_check();
#elif defined(INPUT_TEST)
  finger.input_check();
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
    unsigned long timestamp = millis();
    float object_position = object_encoder.read_position();
    load_cell.read_non_blocking(object_force, force_timestamp);

    Serial.write((byte *)&timestamp, 4);       // Send 4 bytes
    Serial.write((byte *)&object_position, 4); // Send 4 bytes
    Serial.write((byte *)&force_timestamp, 4); // Send 4 bytes
    Serial.write((byte *)&object_force, 4);    // Send 4 bytes
  }
}