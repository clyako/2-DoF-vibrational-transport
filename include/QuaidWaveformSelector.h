#include <Arduino.h>

// #define FREQ_2_HZ
// #define FREQ_5_HZ
// #define FREQ_10_HZ
#define FREQ_15_HZ
// #define FREQ_20_HZ
// #define FREQ_30_HZ
// #define FREQ_40_HZ
// #define FREQ_60_HZ
// #define FREQ_70_HZ
// #define FREQ_80_HZ
// #define FREQ_100_HZ // DANGEROUS

#if defined(FREQ_2_HZ)
constexpr float quaid_frequency = 2;          // Hz
constexpr float min_acceleration_gs = 0.0085; // gs (1 mm)
// constexpr float min_acceleration_gs = 0.0120; // gs (3 mm)
constexpr float max_acceleration_gs = 0.18; // gs

#elif defined(FREQ_5_HZ)
constexpr float quaid_frequency = 5;        // Hz
constexpr float min_acceleration_gs = 0.05; // gs
constexpr float max_acceleration_gs = 0.5;  // gs

#elif defined(FREQ_10_HZ)
constexpr float quaid_frequency = 10; // Hz
// constexpr float min_acceleration_gs = 0.08; // gs (1 mm)
constexpr float min_acceleration_gs = 0.18; // gs (3 mm)
constexpr float max_acceleration_gs = 50.0; // gs

#elif defined(FREQ_15_HZ)
constexpr float quaid_frequency = 15; // Hz
// constexpr float min_acceleration_gs = 0.08; // gs (1 mm)
constexpr float min_acceleration_gs = 0.8;  // gs (3 mm) // 0.8
constexpr float max_acceleration_gs = 20.0; // gs

#elif defined(FREQ_20_HZ)
constexpr float quaid_frequency = 20;       // Hz
constexpr float min_acceleration_gs = 1.0;  // gs
constexpr float max_acceleration_gs = 25.0; // gs

#elif defined(FREQ_30_HZ)
constexpr float quaid_frequency = 30;       // Hz
constexpr float min_acceleration_gs = 0.75; // gs (1 mm)
// constexpr float min_acceleration_gs = 2.5;  // gs (3 mm)
constexpr float max_acceleration_gs = 50.0; // gs

#elif defined(FREQ_40_HZ)
constexpr float quaid_frequency = 40; // Hz
// constexpr float min_acceleration_gs = 1.5; // gs
constexpr float min_acceleration_gs = 3.5;   // gs
constexpr float max_acceleration_gs = 100.0; // gs

#elif defined(FREQ_60_HZ)
constexpr float quaid_frequency = 60;      // Hz
constexpr float min_acceleration_gs = 2.7; // gs (1 mm)
// constexpr float min_acceleration_gs = 5.0;  // gs (3mm)
constexpr float max_acceleration_gs = 50.0; // gs

#elif defined(FREQ_70_HZ)
constexpr float quaid_frequency = 70;         // Hz
constexpr float min_acceleration_gs = 5.9767; // gs (1 mm)
// constexpr float min_acceleration_gs = 5.0;   // gs (3mm)
constexpr float max_acceleration_gs = 20.0; // gs

#elif defined(FREQ_80_HZ)
constexpr float quaid_frequency = 80;        // Hz
constexpr float min_acceleration_gs = 5.0;   // gs
constexpr float max_acceleration_gs = 250.0; // gs

#elif defined(FREQ_100_HZ)
constexpr float quaid_frequency = 80;        // Hz
constexpr float min_acceleration_gs = 10.0;  // gs
constexpr float max_acceleration_gs = 100.0; // gs

#endif