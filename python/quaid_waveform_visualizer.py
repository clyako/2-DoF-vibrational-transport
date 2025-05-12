import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from numpy import zeros, linspace, ndarray


class QuaidWaveform:
    def __init__(self, freq: float = 5, a_min: float = 0.02, a_max: float = 0.10):
        self.freq = freq
        self.period_us = 1 / self.freq * 1e6
        self.a_min = a_min * 9.81 / 1e9
        self.a_max = a_max * 9.81 / 1e9
        self.t1 = (a_max / (a_max + a_min)) * self.period_us / 2
        self.t2 = self.period_us - self.t1

    def get_waveform_data(self, num_points=10000) -> (ndarray, ndarray, ndarray, ndarray):
        max_time_us = self.period_us * self.num_periods
        times = linspace(0, max_time_us, num_points)
        positions = zeros((len(times),))
        velocities = zeros((len(times),))
        accelerations = zeros((len(times),))

        for idx, t in enumerate(times):
            periodic_t = t % self.period_us

            if idx == len(positions):
                break

            if (periodic_t <= self.t1):
                positions[idx] = 0.5 * self.a_min * (periodic_t ** 2)
                velocities[idx] = self.a_min * periodic_t
                accelerations[idx] = self.a_min
            elif (self.t1 < periodic_t and periodic_t <= self.t2):
                positions[idx] = self.a_min * self.t1 * (periodic_t - 0.5 * self.t1) + self.a_max * \
                    (self.t1 * periodic_t - 0.5 * (periodic_t ** 2) - 0.5 * (self.t1 ** 2))
                velocities[idx] = self.a_min * self.t1 - self.a_max * (periodic_t - self.t1)
                accelerations[idx] = -self.a_max
            elif (periodic_t <= self.period_us):
                positions[idx] = self.a_min * (0.5 * (periodic_t ** 2) - self.period_us *
                                               periodic_t + 0.5 * self.period_us ** 2)
                velocities[idx] = self.a_min * (periodic_t - self.period_us)
                accelerations[idx] = self.a_min

            velocities[idx] = velocities[idx] * 1000
            accelerations[idx] = accelerations[idx] * (1000 ** 3)

        if len(times) != len(positions):
            if len(times) > len(positions):
                times = times[:len(positions)]
            else:
                positions = positions[:len(times)]
                velocities = velocities[:len(times)]
                accelerations = accelerations[:len(times)]

        return times, positions, velocities, accelerations

    def get_control_efforts(self, positions, velocities, accelerations, m=0.093, b=64, k=195):
        stiffness_term = abs(positions) / 1000 * k
        damping_term = abs(velocities) * b
        inertia_term = abs(accelerations) * m

        return stiffness_term, damping_term, inertia_term

    def interactive_quaid_waveform_plot(self, num_periods: int = 1):
        self.num_periods = num_periods

        self.plot_waveform()
        self.add_sliders()

        self.a_min_slider.on_changed(self.update_plot)
        self.a_max_slider.on_changed(self.update_plot)
        self.freq_slider.on_changed(self.update_plot)

        plt.show()

    def plot_waveform(self) -> None:
        times, positions, velocities, accelerations = self.get_waveform_data()
        stiffness_efforts, damping_efforts, inertial_efforts = self.get_control_efforts(
            positions, velocities, accelerations)

        self.fig, (self.ax_pos, self.ax_vel, self.ax_acc, self.ax_ctrl) = plt.subplots(4, 1)

        self.quaid_waveform_position_line, = self.ax_pos.plot(times / 1e6, positions, 'r-', lw=2)
        self.ax_pos.set_ylabel("Position (mm)")
        self.ax_pos.grid(color='grey', linestyle=':', linewidth=0.5)
        self.ax_pos.set_ylim(0, 6.5)

        self.quaid_waveform_velocity_line, = self.ax_vel.plot(times / 1e6, velocities, 'r-', lw=2)
        self.ax_vel.set_ylabel("Velocity (m / s)")
        self.ax_vel.grid(color='grey', linestyle=':', linewidth=0.5)

        self.quaid_waveform_acceleration_line, = self.ax_acc.plot(times / 1e6, accelerations, 'r-', lw=2)
        # self.ax_acc.set_xlabel("Time (s)")
        self.ax_acc.set_ylabel("Acceleration (m / s^2)")
        self.ax_acc.grid(color='grey', linestyle=':', linewidth=0.5)

        self.stiffness_line, = self.ax_ctrl.plot(times / 1e6, stiffness_efforts, 'r', lw=2, label='stiffness effort')
        self.damping_line, = self.ax_ctrl.plot(times / 1e6, damping_efforts, 'b', lw=2, label='damping effort')
        self.inertial_line, = self.ax_ctrl.plot(times / 1e6, inertial_efforts, 'g', lw=2, label='inertial effort')
        self.ax_ctrl.set_xlabel("Time (s)")
        self.ax_ctrl.set_ylabel("Control Effort (N)")
        self.ax_ctrl.legend()
        self.ax_acc.grid(color='grey', linestyle=':', linewidth=0.5)

    def add_sliders(self) -> None:
        self.fig.subplots_adjust(bottom=0.25)
        # horizontal slider to adjust a_min
        self.ax_a_min = self.fig.add_axes([0.35, 0.16, 0.35, 0.03])
        self.a_min_slider = Slider(ax=self.ax_a_min, label='Min Acceleration (g)', valmin=0.001,
                                   valmax=10, valinit=self.a_min * 1e9 / 9.81, valfmt='%.4f', color='grey')
        # horizontal slider to adjust a_max
        self.ax_a_max = self.fig.add_axes([0.35, 0.10, 0.35, 0.03])
        self.a_max_slider = Slider(ax=self.ax_a_max, label='Max Acceleration (g)', valmin=0.001,
                                   valmax=300.0, valinit=self.a_max * 1e9 / 9.81, valfmt='%.4f', color='grey')
        # horizontal slider to adjust freq
        self.ax_freq = self.fig.add_axes([0.35, 0.04, 0.35, 0.03])
        self.freq_slider = Slider(ax=self.ax_freq, label='Frequency (Hz)', valmin=0.1,
                                  valmax=100, valinit=self.freq, valfmt='%.2f', color='grey')

    def update_plot(self, val) -> None:
        a_min = self.a_min_slider.val
        a_max = self.a_max_slider.val
        freq = self.freq_slider.val

        if a_min > a_max:
            a_min = a_max

        self.a_min = a_min * 9.81 / (1e9)
        self.a_max = a_max * 9.81 / (1e9)
        self.period_us = 1 / freq * (1e6)
        self.t1 = (self.a_max / (self.a_max + self.a_min)) * self.period_us / 2
        self.t2 = self.period_us - self.t1

        times, positions, velocities, accelerations = self.get_waveform_data()
        stiffness_efforts, damping_efforts, inertial_efforts = self.get_control_efforts(
            positions, velocities, accelerations)

        self.quaid_waveform_position_line.set_xdata(times / 1e6)
        self.quaid_waveform_position_line.set_ydata(positions)

        self.quaid_waveform_velocity_line.set_xdata(times / 1e6)
        self.quaid_waveform_velocity_line.set_ydata(velocities)

        self.quaid_waveform_acceleration_line.set_xdata(times / 1e6)
        self.quaid_waveform_acceleration_line.set_ydata(accelerations)

        self.stiffness_line.set_xdata(times / 1e6)
        self.stiffness_line.set_ydata(stiffness_efforts)

        self.damping_line.set_xdata(times / 1e6)
        self.damping_line.set_ydata(damping_efforts)

        self.inertial_line.set_xdata(times / 1e6)
        self.inertial_line.set_ydata(inertial_efforts)

        self.ax_pos.relim()
        self.ax_vel.relim()
        self.ax_acc.relim()
        self.ax_ctrl.relim()
        self.ax_pos.autoscale_view()
        self.ax_vel.autoscale_view()
        self.ax_acc.autoscale_view()
        self.ax_ctrl.autoscale_view()
        self.fig.canvas.draw_idle()


if __name__ == '__main__':
    quaid_waveform = QuaidWaveform()
    quaid_waveform.interactive_quaid_waveform_plot(num_periods=2)
