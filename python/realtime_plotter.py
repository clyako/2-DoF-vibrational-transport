import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from collections import deque
import serial.tools.list_ports
import serial
import sys
import struct
import numpy as np


def listports():
    # List available serial ports
    ports = serial.tools.list_ports.comports()
    print("Available serial ports:")
    for port in ports:
        print(f"  {port.device}")


listports()

# ser = serial.Serial("/dev/cu.usbmodem90392301", 115200, timeout=1)  # Spatula
# ser = serial.Serial("/dev/cu.usbmodem150120301", 115200, timeout=1)  # Transmission
ser = serial.Serial("/dev/cu.usbmodem153385601", 115200, timeout=1)  # 2 DoF
num_bytes_to_read = 20
teensy_send_data_rate = 1   # ms
time_window_size = 0.25        # s
y_axis_max = 2.0
num_data_points = int(time_window_size / (teensy_send_data_rate / 1000))
refresh_rate = 1           # ms


class ReadThread(QThread):
    update_plot_signal = pyqtSignal(float, float, float, float, float)

    def run(self):
        while True:
            try:
                if ser.in_waiting > 0:
                    data = ser.read(num_bytes_to_read)
                    if len(data) == num_bytes_to_read:
                        timestamp, motor_1_target_position, motor_1_actual_position, motor_2_target_position, motor_2_actual_position = struct.unpack(
                            '<Iffff', data)  # Little-endian (Arduino is little-endian)
                        timestamp /= 1000
                        self.update_plot_signal.emit(
                            timestamp, motor_1_target_position, motor_1_actual_position,
                            motor_2_target_position, motor_2_actual_position)
            except ValueError:
                pass
            except IndexError:
                pass
            except UnboundLocalError:
                pass


class RealTimePlot(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.setLayout(self.layout)

        self.plot_widget.setTitle("Real-time Sensor Data")
        self.plot_widget.setLabel('left', 'Position (mm)')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.setYRange(-y_axis_max, y_axis_max, padding=0.1)
        self.plot_widget.addLegend()

        self.time_window = time_window_size  # 2 seconds

        self.timestamps = deque(maxlen=num_data_points)
        self.motor_1_target_positions = deque(maxlen=num_data_points)
        self.motor_1_actual_positions = deque(maxlen=num_data_points)
        self.motor_2_target_positions = deque(maxlen=num_data_points)
        self.motor_2_actual_positions = deque(maxlen=num_data_points)

        self.line1 = self.plot_widget.plot([], [], pen=pg.mkPen(
            color='y', width=3, style=Qt.SolidLine), name="Motor 1 Target")
        self.line2 = self.plot_widget.plot([], [], pen=pg.mkPen(
            color='y', width=3, style=Qt.DashLine), name="Motor 1 Actual")
        self.line3 = self.plot_widget.plot([], [], pen=pg.mkPen(
            color='g', width=3, style=Qt.SolidLine), name="Motor 2 Target")
        self.line4 = self.plot_widget.plot([], [], pen=pg.mkPen(
            color='g', width=3, style=Qt.DashLine), name="Motor 2 Actual")

        self.worker_thread = ReadThread()
        self.worker_thread.update_plot_signal.connect(self.update_plot)
        self.worker_thread.start()

        # Set up a timer to update the plot
        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(refresh_rate)  # Update every 10 ms
        self.refresh_timer.timeout.connect(self.refresh_plot)
        self.refresh_timer.start()

    def update_plot(self, timestamp, value1, value2, value3, value4):
        self.timestamps.append(timestamp)
        self.motor_1_target_positions.append(value1)
        self.motor_1_actual_positions.append(value2)
        self.motor_2_target_positions.append(value3)
        self.motor_2_actual_positions.append(value4)

        if len(self.timestamps) > 1:
            start_time = self.timestamps[0]
            self.plot_widget.setXRange(start_time, start_time + self.time_window, padding=0)

    def refresh_plot(self):
        self.line1.setData(self.timestamps, self.motor_1_target_positions)
        self.line2.setData(self.timestamps, self.motor_1_actual_positions)
        self.line3.setData(self.timestamps, self.motor_2_target_positions)
        self.line4.setData(self.timestamps, self.motor_2_actual_positions)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec_())
