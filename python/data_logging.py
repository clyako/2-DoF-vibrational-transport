import sys
import time
from PyQt5.QtCore import QThread
import serial
import struct


class LogThread(QThread):
    # def __init__(self, port="/dev/cu.usbmodem150120301", log_filename="data/static/static_test_8_2_motor_speed_700_mass_1094.csv", baudrate=115200):
        # def __init__(self, port="/dev/cu.usbmodem150120301", log_filename="data/kinetic/kinetic_test_8_motor_speed_2000_mass_1094.csv",    baudrate=115200):
        # def __init__(self, port="/dev/cu.usbmodem150120301", log_filename="data/object_velocity_varying_amax_normal_force/frequency_20_amin_0.7_amax_5.csv", baudrate=115200):
        # def __init__(self, port="/dev/cu.usbmodem150120301", log_filename="data/object_velocity_varying_amin_normal_force/frequency_15_amin_1.0_amax_10.csv", baudrate=115200):
        super().__init__()
        self.ser = serial.Serial(port, baudrate, timeout=0)
        self.log_filename = log_filename
        self.num_bytes_to_read = 16
        self.running = True
        self.buffer = []
        self.buffer_size = 500

    def run(self):
        try:
            with open(self.log_filename, 'w') as logfile:
                logfile.write("position_timestamp,position,force_timestamp,force\n")

                while self.running:
                    if self.ser.in_waiting >= self.num_bytes_to_read:
                        data = self.ser.read(self.num_bytes_to_read)
                        if len(data) == self.num_bytes_to_read:
                            position_timestamp, position, force_timestamp, force = struct.unpack('<IfIf', data)
                            line = f"{position_timestamp},{position},{force_timestamp},{force}\n"
                            print(line)
                            self.buffer.append(line)

                            if len(self.buffer) >= self.buffer_size:
                                logfile.writelines(self.buffer)
                                logfile.flush()
                                self.buffer.clear()

                if self.buffer:
                    logfile.writelines(self.buffer)
                    logfile.flush()

            self.ser.close()
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def stop(self):
        self.running = False


if __name__ == "__main__":
    try:
        log_thread = LogThread()
        log_thread.start()

        print("Logging started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping logging...")
        log_thread.stop()
        log_thread.wait()
        sys.exit(0)
