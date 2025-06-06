import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def read_data(filename: str):
    logged_data = pd.read_csv(filename)
    position_timestamps = logged_data["position_timestamp"].to_numpy() / 1e6
    position_timestamps -= position_timestamps[0]
    part_positions = logged_data["position"].to_numpy()
    force_timestamps = logged_data["force_timestamp"].to_numpy() / 1e6
    force_timestamps -= force_timestamps[0]
    forces = logged_data["force"].to_numpy() * -1

    return position_timestamps, part_positions, force_timestamps, forces


def best_line_fit(position_timestamps, part_positions):
    coeffs = np.polyfit(position_timestamps, part_positions, 1)
    y_fit = np.polyval(coeffs, position_timestamps)
    ss_res = np.sum((part_positions - y_fit) ** 2)
    ss_tot = np.sum((part_positions - np.mean(part_positions)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    print(coeffs)

    return y_fit


def plot_data(position_timestamps, part_positions, force_timestamps, forces):
    fig, ax_1 = plt.subplots()
    ax_1.set_xlabel("Time (s)")
    ax_1.set_ylabel("Position (mm)")
    ax_1.plot(position_timestamps, part_positions, 'r-', label="Position Data", lw=2)

    ax_2 = ax_1.twinx()
    ax_2.set_ylabel("Force (N)")
    ax_2.plot(force_timestamps, forces, 'b-', label="Force Data", lw=2)
    ax_2.set_ylim(bottom=0)
    mean_force = np.mean(forces)
    ax_2.axhline(mean_force, color='b', linestyle='--',
                 label="Average Force = {:.2f} ± {:.2f} N".format(mean_force, 2 * np.std(forces)))

    fig.tight_layout()
    plt.grid(True, which="both", ls="--")

    lines_1, labels_1 = ax_1.get_legend_handles_labels()
    lines_2, labels_2 = ax_2.get_legend_handles_labels()
    fig.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', bbox_to_anchor=(0.12, 0.82))

    plt.show()


if __name__ == "__main__":
    ############################################################
    ### Finding Maximum a_min for Maximum Waveform Amplitude ###
    ############################################################
    g = 9.81
    mu_s = 1.20
    force = 4.0
    m = 0.322
    frequency = 20
    T = 1 / frequency
    a_max = 50.0 * g
    max_waveform_amplitude = 3.0

    a_s = mu_s * force / (m * g) - 1
    print("Theoretical max a_min based on normal force: {:.2f} g".format(a_s))

    for a_min_g in np.linspace(0.01, 6.0, 1000):
        a_min = a_min_g * g
        t_1 = a_max / (a_min + a_max) * (T / 2)
        t_max = t_1 * (a_min / a_max + 1)
        waveform_amplitude = (a_min * t_1 * (t_max - 0.5 * t_1) + a_max *
                              (t_1 * t_max - 0.5 * t_max ** 2 - 0.5 * t_1 ** 2)) * 1000
        if waveform_amplitude >= max_waveform_amplitude:
            print("Max a_min limited by amplitude: {:.2f} g".format(a_min_g))
            break

    ############################################################
    ################ Plotting the capture data #################
    ############################################################

    lower_position_for_mask = 2.0
    upper_position_for_mask = 10.0

    filename = "data/fixed_waveform_varying_normal_force/sensor_data_log.csv"
    position_timestamps, part_positions, force_timestamps, forces = read_data(filename)

    # define cutoffs for data
    lower_index = np.argmax(part_positions > lower_position_for_mask)
    upper_index = (np.where(part_positions < upper_position_for_mask))[0][-1]

    position_timestamps = position_timestamps[lower_index:upper_index]
    part_positions = part_positions[lower_index:upper_index]
    force_timestamps = force_timestamps[lower_index:upper_index]
    forces = forces[lower_index:upper_index]

    plot_data(position_timestamps, part_positions, force_timestamps, forces)
