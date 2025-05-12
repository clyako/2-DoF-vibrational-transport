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
    forces = logged_data["force"].to_numpy()

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
    ax_1.plot(position_timestamps, best_line_fit(position_timestamps, part_positions), 'r--', label="position fit", lw=2)

    ax_2 = ax_1.twinx()
    ax_2.set_ylabel("Force (N)")
    ax_2.plot(force_timestamps, forces, 'b-', label="Force Data", lw=2)
    ax_2.set_ylim(bottom=0)
    mean_force = np.mean(forces)
    ax_2.axhline(mean_force, color='b', linestyle='--', label="Average Force = {:.2f} N".format(mean_force))

    fig.tight_layout()
    plt.grid(True, which="both", ls="--")

    lines_1, labels_1 = ax_1.get_legend_handles_labels()
    lines_2, labels_2 = ax_2.get_legend_handles_labels()
    fig.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', bbox_to_anchor=(0.12, 0.82))

    plt.show()


if __name__ == "__main__":
    filename = "data/sensor_data_log.csv"
    position_timestamps, part_positions, force_timestamps, forces = read_data(filename)

    # define cutoffs for data
    lower_index = 200
    upper_index = len(position_timestamps) - 200

    position_timestamps = position_timestamps[lower_index:upper_index]
    part_positions = part_positions[lower_index:upper_index]
    force_timestamps = force_timestamps[lower_index:upper_index]
    forces = forces[lower_index:upper_index]

    """ Retrieving Values """
    object_mass = 0.230
    gravity = 9.81
    mean_force = np.mean(forces)
    mu_k_estimate = mean_force / (object_mass * gravity)
    mu_s_estimate = np.max(forces) / (object_mass * gravity)

    print("Mean Force = {:.2f} N".format(mean_force))
    print("Estimated Kinetic Coefficient of Friction = {:.2f}".format(mu_k_estimate))

    print("Peak Force = {:.2f} N".format(np.max(forces)))
    print("Estimated Static Coefficient of Friction = {:.2f}".format(mu_s_estimate))

    plot_data(position_timestamps, part_positions, force_timestamps, forces)
