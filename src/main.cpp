#include <Arduino.h>
#include "Finger.h"
#include "PinDefines.h"
#include "LoadCell.h"
#include "ForceMotor.h"

void log_object_position_and_force_data();

#define ENCODER_TEST
// #define OBJECT_ENCODER_TEST
// #define FORCE_MOTOR_TEST
// #define INPUT_TEST
// #define LOAD_CELL_CALIBRATION
// #define FORCE_VELOCITY_EXPERIMENT
// #define MAX_FORCE_EXPERIMENT
// #define PLOT
// #define LOG

// mass is 322 g (without carriage)

// state machine states
uint8_t SWITCH_TO_START = 0;
uint8_t RETRACT_MOTOR = 1;
uint8_t BACK_OFF_FINGER = 2;
uint8_t ZERO_LOAD_CELL = 3;
uint8_t APPLY_FORCE = 4;
uint8_t RUN_TEST = 5;
uint8_t STOP_TEST = 6;
uint8_t STATE = BACK_OFF_FINGER;
#if defined(FORCE_MOTOR_TEST)
STATE = SWITCH_TO_START;
#endif

elapsedMillis apply_force_timer;
uint32_t apply_force_time = 5000;
float apply_force_threshold = 0.25; // 250 mN
bool applied_force_valid = false;
elapsedMillis test_timer;
uint32_t test_timeout = 3000;

Finger finger = Finger(MOTOR_1_PWM_A, MOTOR_1_PWM_B, MOTOR_1_SLP,
                       MOTOR_2_PWM_A, MOTOR_2_PWM_B, MOTOR_2_SLP,
                       ENCODER_1_CHANNEL_NUM, ENCODER_1_CHANNEL_A, ENCODER_1_CHANNEL_B,
                       ENCODER_2_CHANNEL_NUM, ENCODER_2_CHANNEL_A, ENCODER_2_CHANNEL_B);

// object encoder
LinearEncoder object_encoder = LinearEncoder(ENCODER_3_CHANNEL_NUM, ENCODER_3_CHANNEL_A, ENCODER_3_CHANNEL_B);

// force motor
float target_force = -50; // N
float end_force = -30;    // N
float force_step = 10;    // N

// max force experiment stuff
uint32_t max_force_trial_timeout = 10000;             // ms
float max_force_successful_position_threshold = 12.0; // mm

ForceMotor force_motor = ForceMotor();

// load cell stuff
LoadCell load_cell;
float object_force = 0.0;
uint32_t force_timestamp = 0;

// stuff for logging data
elapsedMicros logging_timer;
unsigned long logging_period = 500; // log every 0.5 s

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
  load_cell.zero();

  // reset logging timer
  logging_timer = 0;

  force_motor.initialize(MOTOR_3_PWM_A, MOTOR_3_PWM_B, MOTOR_3_SLP);
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
  if (STATE == SWITCH_TO_START)
  {
    if (finger.power_switch())
    {
      STATE = RETRACT_MOTOR;
    }
  }
  else if (STATE == RETRACT_MOTOR)
  {
    force_motor.retract();

    if (!finger.power_switch())
    {
      force_motor.stop_motor();
      STATE = RUN_TEST;
    }
  }
  else if (STATE == RUN_TEST)
  {
    if (finger.power_switch())
    {
      force_motor.drive_motor(0, 500);
    }
    else
    {
      force_motor.stop_motor();
    }
    // load_cell.read_raw();
    delay(500);

    load_cell.read_non_blocking(object_force, force_timestamp);
    Serial.print("Force = ");
    Serial.print(object_force, 3);
    Serial.println(" N");
  }
#elif defined(FORCE_MOTOR_TEST)
  if (STATE == SWITCH_TO_START)
  {
    if (finger.power_switch())
    {
      STATE = RETRACT_MOTOR;
    }
  }
  else if (STATE == RETRACT_MOTOR)
  {
    force_motor.retract();

    if (!finger.power_switch())
    {
      force_motor.stop_motor();
      STATE = BACK_OFF_FINGER;
    }
  }
  else if (STATE == BACK_OFF_FINGER)
  {
    if (finger.power_switch())
    {
      delay(200);
      STATE = ZERO_LOAD_CELL;
    }
  }
  else if (STATE == ZERO_LOAD_CELL)
  {
    if (!finger.power_switch())
    {
      load_cell.zero();
      delay(200);
      STATE = RUN_TEST;
    }
  }
  else if (STATE == RUN_TEST)
  {
    load_cell.read_non_blocking_filtered(object_force, force_timestamp);
    force_motor.force_control(target_force, object_force);

    if (!applied_force_valid && abs(object_force - target_force) < apply_force_threshold)
    {
      apply_force_timer = 0;
      applied_force_valid = true;
    }
    else if (applied_force_valid && apply_force_timer > apply_force_time)
    {
      force_motor.stop_motor();
      test_timer = 0;
      STATE = STOP_TEST;
    }
    else if (abs(object_force - target_force) > apply_force_threshold)
    {
      apply_force_timer = 0;
      applied_force_valid = false;
    }
    if (print_timer > print_period)
    {
      print_timer = 0;
      Serial.println(object_force);
    }
  }
  else if (STATE == STOP_TEST)
  {
    force_motor.stop_motor();

    load_cell.read_non_blocking(object_force, force_timestamp);

    if (print_timer > print_period)
    {
      print_timer = 0;
      Serial.println(object_force);
    }
  }
#elif defined(FORCE_VELOCITY_EXPERIMENT)
  if (STATE == SWITCH_TO_START)
  {
    if (finger.power_switch())
    {
      STATE = RETRACT_MOTOR;
    }
  }
  else if (STATE == RETRACT_MOTOR)
  {
    force_motor.retract();

    if (!finger.power_switch())
    {
      force_motor.stop_motor();
      STATE = BACK_OFF_FINGER;
    }
  }
  else if (STATE == BACK_OFF_FINGER)
  {
    if (finger.power_switch())
    {
      delay(200);
      object_encoder.calibrate();
      STATE = ZERO_LOAD_CELL;
      finger.set_motor_gains(1000, 0.5);
    }
  }
  else if (STATE == ZERO_LOAD_CELL)
  {
    if (!finger.power_switch())
    {
      load_cell.zero();
      delay(200);
      STATE = APPLY_FORCE;
    }
  }
  else if (STATE == APPLY_FORCE)
  {
    load_cell.read_non_blocking_filtered(object_force, force_timestamp);
    force_motor.force_control(target_force, object_force);

    if (!applied_force_valid && abs(object_force - target_force) < apply_force_threshold)
    {
      apply_force_timer = 0;
      applied_force_valid = true;
    }
    else if (applied_force_valid && apply_force_timer > apply_force_time)
    {
      force_motor.stop_motor();
      test_timer = 0;
      STATE = RUN_TEST;
      finger.set_motor_gains(4500, 6.0);
    }
    else if (abs(object_force - target_force) > apply_force_threshold)
    {
      apply_force_timer = 0;
      applied_force_valid = false;
    }

    finger.move_to_center();
    // if (print_timer > print_period)
    // {
    //   print_timer = 0;
    //   Serial.println(object_force);
    // }
  }
  else if (STATE == RUN_TEST)
  {
    finger.run();

    // load_cell.read_non_blocking_filtered(object_force, force_timestamp);
    // force_motor.force_control(target_force, object_force);

#if defined(LOG)
    log_object_position_and_force_data();
#endif

    if (object_encoder.read_position() > 11.0 or test_timer > test_timeout)
    {
      STATE = STOP_TEST;
    }
  }
  else if (STATE == STOP_TEST)
  {
    finger.stop();
    if (!finger.power_switch())
    {
      force_motor.stop_motor();
      STATE = REMOVE_SPRING;
    }
    else
    {
      force_motor.retract();
    }
  }
  else
  {
    finger.stop();
    force_motor.stop_motor();
  }
#elif defined(MAX_FORCE_EXPERIMENT)
  if (STATE == BACK_OFF_FINGER)
  {
    force_motor.retract();
    if (finger.power_switch())
    {
      delay(200);
      force_motor.stop_motor();
      object_encoder.calibrate();
      STATE = ZERO_LOAD_CELL;
      finger.set_motor_gains(1000, 0.5); // lower gains to hold center position
    }
  }
  else if (STATE == ZERO_LOAD_CELL)
  {
    if (!finger.power_switch())
    {
      load_cell.zero();
      delay(200);
      STATE = APPLY_FORCE;
    }
  }
  else if (STATE == APPLY_FORCE)
  {
    load_cell.read_non_blocking_filtered(object_force, force_timestamp);
    force_motor.force_control(target_force, object_force);

    if (!applied_force_valid && abs(object_force - target_force) < apply_force_threshold)
    {
      apply_force_timer = 0;
      applied_force_valid = true;
    }
    else if (applied_force_valid && apply_force_timer > apply_force_time)
    {
      force_motor.stop_motor();
      test_timer = 0;
      STATE = RUN_TEST;
      finger.set_motor_gains(4500, 6.0);
      while (!finger.power_switch())
      {
      }
    }
    else if (abs(object_force - target_force) > apply_force_threshold)
    {
      apply_force_timer = 0;
      applied_force_valid = false;
    }

    finger.move_to_center();

    // if (print_timer > print_period)
    // {
    //   print_timer = 0;
    //   Serial.print("Current Force = ");
    //   Serial.print(object_force);
    //   Serial.println(" N");
    // }
  }
  else if (STATE == RUN_TEST)
  {
    finger.run();

#if defined(LOG)
    log_object_position_and_force_data();
#endif

    // if (object_encoder.read_position() > max_force_successful_position_threshold)
    // {
    //   load_cell.read_non_blocking_filtered(object_force, force_timestamp);
    //   // Serial.print("\n Experiment Complete\nMax Force = ");
    //   // Serial.print(object_force, 2);
    //   // Serial.println(" N");
    //   STATE = STOP_TEST;
    // }
    if (target_force > end_force)
    {
      STATE = STOP_TEST;
    }
    else if (object_encoder.read_position() > max_force_successful_position_threshold || test_timer > max_force_trial_timeout)
    {
      finger.stop();
      delay(1000);
      target_force += force_step;
      delay(500);
      finger.set_motor_gains(1000, 0.5);
      STATE = RETRACT_MOTOR;
    }
  }
  else if (STATE == RETRACT_MOTOR)
  {
    force_motor.retract();

    if (!finger.power_switch())
    {
      applied_force_valid = false;
      apply_force_timer = 0;
      STATE = APPLY_FORCE;
    }
  }
  else if (STATE == STOP_TEST)
  {
    finger.stop();
    if (!finger.power_switch())
    {
      force_motor.stop_motor();
      STATE = BACK_OFF_FINGER;
    }
  }
  else
  {
    finger.stop();
    force_motor.stop_motor();
  }
#else
  finger.run();

  load_cell.read_non_blocking(object_force, force_timestamp);

  if (print_timer > print_period)
  {
    print_timer = 0;
    Serial.println(object_force);
  }
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