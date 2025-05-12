import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

object_mass = 0.230
gravity = 9.81


def static_data_analysis(plot=True):
    speeds = [400, 500, 800]
    lower_limits = [800, 500, 2200]
    upper_limits = [0, 0, 0]

    static_friction_coefficients = []

    for speed, lower_limit, upper_limit in zip(speeds, lower_limits, upper_limits):
        filename = "data/static/static_test_motor_speed_" + str(speed) + "_mass_200.csv"
        position_timestamps, part_positions, force_timestamps, forces = read_data(filename)

        lower_index = lower_limit
        upper_index = len(position_timestamps) - upper_limit

        position_timestamps = position_timestamps[lower_index:upper_index]
        part_positions = part_positions[lower_index:upper_index]
        force_timestamps = force_timestamps[lower_index:upper_index]
        forces = forces[lower_index:upper_index]

        if plot:
            plot_data(position_timestamps, part_positions, force_timestamps, forces, static=True)

        static_friction_coefficients.append(np.max(forces) / (object_mass * gravity))

    print("\nStatic Coefficient of Friction = {:.2f} ± {:.2f}\n".format(
        np.mean(static_friction_coefficients), np.std(static_friction_coefficients)))


def kinetic_data_analysis(plot=True):
    speeds = [500, 1000, 1493, 2000, 4000]
    lower_limits = [200, 100, 100, 50, 45]
    upper_limits = [50, 50, 100, 50, 20]

    kinetic_friction_coefficients = []
    test_velocities = []

    for speed, lower_limit, upper_limit in zip(speeds, lower_limits, upper_limits):
        filename = "data/kinetic/kinetic_test_motor_speed_" + str(speed) + "_mass_200.csv"
        position_timestamps, part_positions, force_timestamps, forces = read_data(filename)

        lower_index = lower_limit
        upper_index = len(position_timestamps) - upper_limit

        position_timestamps = position_timestamps[lower_index:upper_index]
        part_positions = part_positions[lower_index:upper_index]
        force_timestamps = force_timestamps[lower_index:upper_index]
        forces = forces[lower_index:upper_index]

        _, coeffs = best_line_fit(position_timestamps, part_positions)
        test_velocities.append(coeffs[0])

        if plot:
            plot_data(position_timestamps, part_positions, force_timestamps, forces)

        print(np.mean(forces) / (object_mass * gravity))
        kinetic_friction_coefficients.append(np.mean(forces) / (object_mass * gravity))

    print("Kinetic Coefficient of Friction = {:.2f} ± {:.2f}\n".format(
        np.mean(kinetic_friction_coefficients), np.std(kinetic_friction_coefficients)))

    plt.scatter(test_velocities, kinetic_friction_coefficients, color='b')
    plt.axhline(np.mean(kinetic_friction_coefficients), color='b', linestyle='--',
                label="Average mu_k = {:.2f} N".format(np.mean(kinetic_friction_coefficients)))
    plt.xlabel("Test Velocity (mm/s)")
    plt.ylabel("Coefficient of Kinetic Friction")
    plt.ylim(bottom=0, top=1.3)
    plt.grid()
    plt.legend()
    plt.show()


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

    return y_fit, coeffs


def plot_data(position_timestamps, part_positions, force_timestamps, forces, static=False):
    fig, ax_1 = plt.subplots()
    ax_1.set_xlabel("Time (s)", fontsize=16)
    ax_1.set_ylabel("Position (mm)", fontsize=16)
    ax_1.plot(position_timestamps, part_positions, 'r-', label="Position Data", lw=2)
    y_fit_vals, coeffs = best_line_fit(position_timestamps, part_positions)
    ax_1.plot(position_timestamps, y_fit_vals, 'r--', label="Velocity = {:.2f} mm/s".format(coeffs[0]), lw=2)

    ax_2 = ax_1.twinx()
    ax_2.set_ylabel("Force (N)", fontsize=16)
    ax_2.plot(force_timestamps, forces, 'b-', label="Force Data", lw=2)
    ax_2.set_ylim(bottom=0)

    if not static:
        mean_force = np.mean(forces)
        ax_2.axhline(mean_force, color='b', linestyle='--', label="Average Force = {:.2f} N".format(mean_force))

    fig.tight_layout()
    plt.grid(True, which="both", ls="--")

    lines_1, labels_1 = ax_1.get_legend_handles_labels()
    lines_2, labels_2 = ax_2.get_legend_handles_labels()

    bbox_anchor = (0.11, 0.95)

    if not static:
        bbox_anchor = (0.11, 0.81)

    ax_1.tick_params(axis='x', labelsize=14)
    ax_1.tick_params(axis='y', labelsize=14)
    ax_2.tick_params(axis='x', labelsize=14)
    ax_2.tick_params(axis='y', labelsize=14)
    fig.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', bbox_to_anchor=bbox_anchor, fontsize=14)

    if static:
        plt.title("Static Coefficient of Friction = {:.2f}".format(
            np.max(forces) / (object_mass * gravity)), fontsize=16)
    else:
        plt.title("Kinetic Coefficient of Friction = {:.2f}".format(
            np.mean(forces) / (object_mass * gravity)), fontsize=16)

    plt.show()


if __name__ == "__main__":
    static_data_analysis(plot=False)
    kinetic_data_analysis(plot=True)
