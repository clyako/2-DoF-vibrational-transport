import matplotlib.pyplot as plt
from typing import Tuple
from scipy.signal import find_peaks
import pandas as pd
import numpy as np


def read_data(filename: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    logged_data = pd.read_csv(filename)
    position_timestamps = logged_data["position_timestamp"].to_numpy() / 1e6
    position_timestamps -= position_timestamps[0]
    part_positions = logged_data["position"].to_numpy()
    force_timestamps = logged_data["force_timestamp"].to_numpy() / 1e6
    force_timestamps -= force_timestamps[0]
    forces = logged_data["force"].to_numpy() * -1

    return position_timestamps, part_positions, force_timestamps, forces


def get_peak_values(times: np.ndarray, positions: np.ndarray, plot: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    T = 1 / frequency
    sampling_rate = 2000
    peak_dist = sampling_rate * T

    peak_indices = find_peaks(positions, distance=peak_dist)[0]
    peak_times = []
    peak_positions = []
    for index in peak_indices:
        peak_times.append(times[index])
        peak_positions.append(positions[index])
        if plot:
            plt.scatter(peak_times[-1], peak_positions[-1], c='k')

    return peak_times, peak_positions


def calculate_average_velocity_all(position_timestamps: np.ndarray, part_positions: np.ndarray) -> float:
    T = 1 / frequency
    sampling_rate = 2000
    sample_distance = sampling_rate * T

    index = 0
    max_index = len(position_timestamps)

    velocities = []

    while index + sample_distance < max_index:
        delta_position = part_positions[int(index + sample_distance)] - part_positions[int(index)]
        velocities.append(delta_position / T)

        index += 1

    return np.mean(velocities)


def calculate_average_velocity(peak_times: np.ndarray, peak_positions: np.ndarray) -> float:
    velocity = np.polyfit(peak_times, peak_positions, 1)[0]
    return velocity


def plot_data_and_fit(position_timestamps: np.ndarray, part_positions: np.ndarray, force_timestamps: np.ndarray, forces: np.ndarray, cutoffs: bool = False) -> None:
    fig, ax_1 = plt.subplots()
    ax_2 = ax_1.twinx()

    plot_data(position_timestamps, part_positions, force_timestamps, forces, ax_1, ax_2)
    peak_times, peak_positions = get_peak_values(position_timestamps, part_positions)
    plot_velocity(peak_times, peak_positions, ax_1)

    fig.tight_layout()
    plt.grid(True, which="both", ls="--")

    lines_1, labels_1 = ax_1.get_legend_handles_labels()
    lines_2, labels_2 = ax_2.get_legend_handles_labels()
    fig.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', bbox_to_anchor=(0.12, 0.82))

    if cutoffs:
        ax_1.scatter(position_timestamps[lower_index], part_positions[lower_index], c="k")
        ax_1.scatter(position_timestamps[upper_index], part_positions[upper_index], c="k")


def plot_data(position_timestamps: np.ndarray, part_positions: np.ndarray, force_timestamps: np.ndarray, forces: np.ndarray, ax_1, ax_2) -> None:
    ax_1.set_xlabel("Time (s)")
    ax_1.set_ylabel("Position (mm)")
    ax_1.plot(position_timestamps, part_positions, 'r-', label="Position Data", lw=2)

    ax_2.set_ylabel("Force (N)")
    ax_2.plot(force_timestamps, forces, 'b-', label="Force Data", lw=2)
    ax_2.set_ylim(bottom=0, top=25)
    mean_force = np.mean(forces)
    ax_2.axhline(mean_force, color='b', linestyle='--', label="Average Force = {:.2f} N".format(mean_force))


def plot_velocity(peak_times: np.ndarray, peak_positions: np.ndarray, ax_1) -> None:
    ax_1.scatter(peak_times, peak_positions, c="red")
    coefs = np.polyfit(peak_times, peak_positions, 1)
    line_fit = np.poly1d(coefs)
    ax_1.plot(peak_times, line_fit(peak_times), 'r--', label="Velocity = {:.2f} mm/s".format(coefs[0]))

    print("Velocity = {:.2f} mm/s".format(coefs[0]))


def plot_fixed_waveform_varying_normal_force(a_min: float, a_max: float, forces: list):
    T = 1 / frequency
    average_velocities = []

    for force in forces:
        a_k = g + mu_k * force / m
        a_s = a_min

        velocity = 0
        if force > m / mu_s * (a_s + g):
            velocity = 1000 * T / 2 * ((a_s ** 2) * (a_max - a_k)) / ((a_s + a_max) * (a_s + a_k))

        average_velocities.append(velocity)

    plt.plot(forces, average_velocities, 'r--', lw=2, label="Theoretical")
    plt.ylim(bottom=0)


if __name__ == "__main__":
    # physical + waveform params
    g = 9.81
    mu_s = 1.2
    mu_k = 1.06
    m = 0.332

    # cutoff selection
    single_cutoff = True

    # calculations to perform
    CHECK_PEAKS = 1
    CHECK_CUTOFFS = 2
    PLOT_DATA = 3
    PLOT_ALL_VELOCITIES = 4
    ACTION = PLOT_DATA

    """
    10 HZ TRIALS
    """

    """ This one is good (single cutoff is better) """
    # foldername = "data/fixed_waveform_varying_normal_force/amin_0.3_amax_20.0_freq_10/"
    # normal_forces = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    # lower_time_masks = [0.9, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
    # upper_time_masks = [1.4, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9]
    # lower_position_for_mask = 3
    # upper_position_for_mask = 6
    # a_min = 0.3 * g
    # a_max = 20 * g
    # frequency = 10

    """ This one is good (single cutoff is better) """
    # foldername = "data/fixed_waveform_varying_normal_force/amin_0.3_amax_50.0_freq_10/"
    # normal_forces = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    # lower_time_masks = [0.0, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.4, 0.4, 1.0]
    # upper_time_masks = [3.0, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 2.0]
    # lower_position_for_mask = 3
    # upper_position_for_mask = 6
    # a_min = 0.3 * g
    # a_max = 50 * g
    # frequency = 10

    """
    15 HZ TRIALS
    """

    """ a_min might be too low """
    # foldername = "data/fixed_waveform_varying_normal_force/amin_0.4_amax_50.0_freq_15/"
    # normal_forces = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    # lower_time_masks = [1.0, 0.5, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.4]
    # upper_time_masks = [1.5, 0.9, 0.7, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]
    # lower_position_for_mask = 3
    # upper_position_for_mask = 6
    # a_min = 0.4 * g
    # a_max = 50 * g
    # frequency = 15

    """ a_min might be too low """
    # foldername = "data/fixed_waveform_varying_normal_force/amin_0.4_amax_20.0_freq_15/"
    # normal_forces = [3, 4, 5, 6, 7, 8, 9, 10, 11]
    # lower_time_masks = [1.0, 0.5, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
    # upper_time_masks = [1.5, 0.9, 0.7, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]
    # lower_position_for_mask = 4
    # upper_position_for_mask = 6
    # a_min = 0.4 * g
    # a_max = 20 * g
    # frequency = 15

    # foldername = "data/fixed_waveform_varying_normal_force/amin_0.8_amax_20.0_freq_15/"
    # normal_forces = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    # lower_position_for_mask = 4
    # upper_position_for_mask = 8
    # a_min = 0.8 * g
    # a_max = 20 * g
    # frequency = 15

    # foldername = "data/fixed_waveform_varying_normal_force/amin_0.8_amax_10.0_freq_15/"
    # normal_forces = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    # lower_position_for_mask = 3
    # upper_position_for_mask = 6
    # a_min = 0.8 * g
    # a_max = 10 * g
    # frequency = 15

    """
    20 HZ TRIALS
    """

    # foldername = "data/fixed_waveform_varying_normal_force/amin_0.6_amax_50.0_freq_20/"
    # normal_forces = [4, 5, 6, 7, 8, 9, 10, 11]
    # lower_position_for_mask = 3
    # upper_position_for_mask = 6
    # a_min = 0.6 * g
    # a_max = 50 * g
    # frequency = 20

    # foldername = "data/fixed_waveform_varying_normal_force/amin_1.0_amax_25.0_freq_20/"
    # normal_forces = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    # lower_position_for_mask = 4
    # upper_position_for_mask = 7
    # a_min = 1.0 * g
    # a_max = 25.0 * g
    # frequency = 20

    """ this is a good one """
    foldername = "data/fixed_waveform_varying_normal_force/amin_1.0_amax_50.0_freq_20/"
    normal_forces = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    lower_position_for_mask = 0
    upper_position_for_mask = 12
    a_min = 1.0 * g
    a_max = 50 * g
    frequency = 20

    # foldername = "data/fixed_waveform_varying_normal_force/amin_1.4_amax_20.0_freq_20/"
    # normal_forces = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
    # lower_position_for_mask = 3
    # upper_position_for_mask = 6
    # a_min = 1.4 * g
    # a_max = 20 * g
    # frequency = 20

    """
    30 HZ TRIALS
    """

    # foldername = "data/fixed_waveform_varying_normal_force/amin_1.5_amax_30.0_freq_30/"
    # normal_forces = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    # lower_position_for_mask = 3
    # upper_position_for_mask = 6
    # a_min = 1.5 * g
    # a_max = 30 * g
    # frequency = 30

    # foldername = "data/fixed_waveform_varying_normal_force/amin_2.5_amax_50.0_freq_30/"
    # normal_forces = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    # lower_position_for_mask = 3
    # upper_position_for_mask = 6
    # a_min = 2.5 * g
    # a_max = 50 * g
    # frequency = 30

    measured_forces = []
    velocities = []
    velocities_all = []

    # for normal_force, lower_time_mask, upper_time_mask in zip(normal_forces, lower_time_masks, upper_time_masks):
    for normal_force in normal_forces:
        for trial_num in [1, 2, 3]:
            filename = foldername + "force_" + str(normal_force) + "_" + str(trial_num) + ".csv"
            position_timestamps, part_positions, force_timestamps, forces = read_data(filename)

            # define cutoffs for data
            if single_cutoff:
                lower_index = np.argmax(part_positions > lower_position_for_mask)
                upper_index = (np.where(part_positions < upper_position_for_mask))[0][-1]
            # upper_index = np.argmin(part_positions < upper_position_for_mask)
            # if upper_index == 0:
            #     upper_index = (np.where(part_positions < upper_position_for_mask))[0][-1]
            else:
                lower_index = np.argmax(position_timestamps > lower_time_mask)
                upper_index = np.argmin(position_timestamps < upper_time_mask)
                if upper_index == 0:
                    upper_index = len(position_timestamps) - 1

            if ACTION == CHECK_CUTOFFS:
                plot_data_and_fit(position_timestamps, part_positions, force_timestamps, forces, cutoffs=True)
                plt.show()
            else:
                position_timestamps = position_timestamps[lower_index:upper_index]
                part_positions = part_positions[lower_index:upper_index]
                force_timestamps = force_timestamps[lower_index:upper_index]
                forces = forces[lower_index:upper_index]

                if ACTION == CHECK_PEAKS:
                    peak_times, peak_positions = get_peak_values(position_timestamps, part_positions, plot=True)
                    plt.plot(position_timestamps, part_positions, 'r-', lw=2, label="Object Position")
                    plt.xlabel("Time (s)")
                    plt.ylabel("Object Position (mm)")
                    plt.show()
                elif ACTION == PLOT_DATA:
                    plot_data_and_fit(position_timestamps, part_positions, force_timestamps, forces)
                    plt.show()
                elif ACTION == PLOT_ALL_VELOCITIES:
                    peak_times, peak_positions = get_peak_values(position_timestamps, part_positions)
                    # velocity = calculate_average_velocity(peak_times, peak_positions)
                    velocity = calculate_average_velocity_all(position_timestamps, part_positions)
                    print("Mean Velocity = {:.2f} mm/s".format(velocity))
                    velocities.append(velocity)
                    measured_forces.append(np.mean(forces))

                    # mean_velocity = calculate_average_velocity_all(position_timestamps, part_positions)
                    # velocities_all.append(mean_velocity)
                    # print("Mean Velocity Peaks = {:.2f} mm/s, Mean Velocity All = {:.2f} mm/s".format(velocity, mean_velocity))

    if ACTION == PLOT_ALL_VELOCITIES:
        measured_forces = np.asarray(measured_forces)
        velocities = np.asarray(velocities)
        measured_forces = np.mean(measured_forces.reshape(-1, 3), axis=1)
        velocities = np.mean(velocities.reshape(-1, 3), axis=1)
        plt.plot(measured_forces, velocities, 'r-', lw=2, marker='o', label="Measured")
        plot_fixed_waveform_varying_normal_force(a_min, a_max, measured_forces)
        plt.xlabel("Force (N)", fontsize=18)
        plt.ylabel("Average Part Velocity (mm/s)", fontsize=18)
        plt.tick_params(axis='both', labelsize=14)  # Tick label size
        plt.grid()
        plt.legend(fontsize=14)
        plt.show()
