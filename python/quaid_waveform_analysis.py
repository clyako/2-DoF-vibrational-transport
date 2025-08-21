import numpy as np
import matplotlib.pyplot as plt

"""
What I know:
• For a given force and a_max, you want to use the smallest possible value of a_min (i.e., a_min = mu_s * F_n / m - g)
    • The other way to think about it is for a given a_min and a_max, you want to apply the smallest allowable force: F_n = (m / mu_s) * (a_min + g)
• For a set of forces and waveforms where a_min is optimized, there exists an optimal combination of a_min and F_n between m * g / mu_s and F_n_max
• For a given a_max, there exists an optimal frequency given the amplitude constraints assuming the maximum value of a_min is being used
    • How to find optimal frequency?
        • Set a_max and physical parameters (m, mu_s, mu_k), as well as the maximum allowed amplitude
        • For each frequency, calculate a_s & a_k --> v_avg, waveform_amplitude
        • The peak velocity is min(v_avg at force_at_max_amplitude, v_avg)
        • Repeat for all frequencies
        • Plot to show optimal
    • How does the optimal frequency change with m, mu_s, mu_k, a_max, and maximum amplitude?
        • Mass, m, has no effect (mass always appears with F_n, and F_n is scaled according to m so there ratio is unchanged)
    • Analytical solution for frequency? set mu_s, mu_k, m, a_max, and maximum amplitude. Calculate forces --> determine a_s (and a_k)
        • We now have a 3D function that varies with the normal force and the frequency (z axis is average velocity)
        • The minimum required frequency is a function of the normal force and it a line on the above surface        
"""


def plot_fixed_waveform_varying_normal_force(a_min: float, a_max: float, frequency: float, max_amplitude: float = 6):
    forces = np.linspace(F_n_min, F_n_max, 200)
    T = 1 / frequency
    average_velocities = []

    for force in forces:
        a_k = g + mu_k * force / m
        a_s = a_min
        velocity = 1000 * T / 2 * ((a_s ** 2) * (a_max - a_k)) / ((a_s + a_max) * (a_s + a_k))

        t_1 = a_max / (a_s + a_max) * (T / 2)
        t_max = t_1 * (a_s / a_max + 1)
        waveform_amplitude = (a_s * t_1 * (t_max - 0.5 * t_1) + a_max *
                              (t_1 * t_max - 0.5 * t_max ** 2 - 0.5 * t_1 ** 2)) * 1000

        if waveform_amplitude < max_amplitude:
            average_velocities.append(velocity)
        else:
            average_velocities.append(0.0)

    plt.plot(forces, average_velocities, 'r', lw=2)
    plt.xlabel("Force (N)")
    plt.ylabel("Average Velocity (mm/s)")
    plt.ylim(bottom=0)
    plt.grid()
    plt.show()


def plot_optimal_a_min_varying_normal_force(a_max: float, frequency: float, max_amplitude: float = 6):
    forces = np.linspace(F_n_min, F_n_max, 100)
    T = 1 / frequency
    average_velocities = []
    force_at_max_amplitude = 0
    force_at_max_amplitude_set = False

    for force in forces:
        a_k = mu_k * force / m + g
        a_s = mu_s * force / m - g
        velocity = 1000 * T / 2 * ((a_s ** 2) * (a_max - a_k)) / ((a_s + a_max) * (a_s + a_k))
        average_velocities.append(velocity)

        t_1 = a_max / (a_s + a_max) * (T / 2)
        t_max = t_1 * (a_s / a_max + 1)
        waveform_amplitude = (a_s * t_1 * (t_max - 0.5 * t_1) + a_max *
                              (t_1 * t_max - 0.5 * t_max ** 2 - 0.5 * t_1 ** 2)) * 1000

        if waveform_amplitude > max_amplitude and not force_at_max_amplitude_set:
            force_at_max_amplitude = force
            force_at_max_amplitude_set = True

    plt.plot(forces, average_velocities, 'r', lw=2)
    plt.xlabel("Force (N)")
    plt.ylabel("Average Velocity (mm/s)")
    plt.ylim(bottom=0)
    # plt.axvline(x=force_at_max_amplitude, color='k', linestyle='--')
    plt.grid()
    plt.show()


def plot_frequency_dependence_optimal_a_min(f_min: float = 2, f_max: float = 100, max_amplitude: float = 6):
    frequencies = np.logspace(np.log10(f_min), np.log10(f_max), num=200)
    forces = np.linspace(m * g / mu_s, F_n_max, 10000)

    optimal_velocities = []

    for frequency in frequencies:
        T = 1 / frequency
        average_velocities = []
        force_at_max_amplitude = np.inf
        force_at_max_amplitude_set = False
        velocity_at_max_force = np.inf

        for force in forces:
            a_k = mu_k * force / m + g
            a_s = mu_s * force / m - g
            velocity = T / 2 * ((a_s ** 2) * (a_max - a_k)) / ((a_s + a_max) * (a_s + a_k))

            average_velocities.append(velocity)

            t_1 = a_max / (a_s + a_max) * (T / 2)
            t_max = t_1 * (a_s / a_max + 1)
            waveform_amplitude = (a_s * t_1 * (t_max - 0.5 * t_1) + a_max *
                                  (t_1 * t_max - 0.5 * t_max ** 2 - 0.5 * t_1 ** 2)) * 1000

            if waveform_amplitude > max_amplitude and not force_at_max_amplitude_set:
                force_at_max_amplitude = force
                force_at_max_amplitude_set = True

                a_k = g + mu_k * force_at_max_amplitude / m
                a_s = -g + mu_s * force_at_max_amplitude / m
                velocity_at_max_force = T / 2 * ((a_s ** 2) * (a_max - a_k)) / ((a_s + a_max) * (a_s + a_k))

        # print("Optimal Average Velocity = {:.2f}, Restricted Max Velocity = {:.2f}".format(
        #     max(average_velocities), velocity_at_max_force))

        unrestricted_max_velocity_force = forces[np.argmax(average_velocities)]
        if force_at_max_amplitude < unrestricted_max_velocity_force:
            optimal_velocity = velocity_at_max_force
        else:
            optimal_velocity = max(average_velocities)
        optimal_velocities.append(optimal_velocity * 1000)

    print("Best Frequency: {:.2f} Hz".format(frequencies[np.argmax(optimal_velocities)]))
    plt.plot(frequencies, optimal_velocities, 'r', lw=2)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Optimal Average Velocity (mm/s)")
    plt.grid()
    plt.show()


if __name__ == '__main__':
    g = 9.81                    # [m/s^2]
    a_min = 0.35 * g             # [m/s^2]
    a_max = 3.5 * g            # [m/s^2]
    f = 10                      # [Hz]
    mu_s = 0.22                  # []
    mu_k = 0.19                 # []
    m = 0.358                   # [kg]

    F_n_min = m * g / mu_s
    # F_n_min = m / mu_s * (a_min + g)
    F_n_max = m * (a_max - g) / mu_k

    print("Min Force = {:.2f} N, Max Force = {:.2f}".format(F_n_min, F_n_max))

    plot_fixed_waveform_varying_normal_force(a_min, a_max, f, max_amplitude=6)
    # plot_optimal_a_min_varying_normal_force(a_max=a_max, frequency=f, max_amplitude=6.0)
    # plot_frequency_dependence_optimal_a_min(max_amplitude=3)

    """
    Optimal a_min Varying F_n experiment:
    • Force range is 2.15 N to 46.25 N
    • Max amplitude is set to 3 mm
    • Frequency is 70 Hz
    • a_max is 20g
    
    """
