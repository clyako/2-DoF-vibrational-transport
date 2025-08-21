import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

object_mass = 1.094
gravity = 9.81
test_nums = [3, 4, 5, 6, 7, 8]

tick_label_size = 18
axes_label_size = 22
title_label_size = 24
label_pad = 10

cmap = plt.cm.BuPu
colors = cmap(np.linspace(0.5, 1.0, 2))
static_color = colors[-1]
kinetic_color = colors[0]


def static_data_analysis(plot=True):
    static_friction_coefficients = []

    for test_num in test_nums:
        filename = "data/static/static_test_" + str(test_num) + "_motor_speed_700_mass_1094.csv"
        if test_num == 8:
            filename = "data/static/static_test_8_2_motor_speed_700_mass_1094.csv"

        position_timestamps, part_positions, force_timestamps, forces = read_data(filename)

        if plot:
            plot_data(position_timestamps, part_positions, force_timestamps, forces, static=True)

        static_friction_coefficients.append(np.max(forces) / (object_mass * gravity))

    print("\nStatic Coefficient of Friction = {:.2f} ± {:.2f}\n".format(
        np.mean(static_friction_coefficients), np.std(static_friction_coefficients)))

    # plt.scatter([test_num - 1 for test_num in test_nums], static_friction_coefficients, color='b')
    # plt.axhline(np.mean(static_friction_coefficients), color='b', linestyle='--',
    #             label=r"Average $\mu_s = {:.2f} \pm {:.2f}$".format(np.mean(static_friction_coefficients), np.std(static_friction_coefficients)))
    # plt.xlabel("Trial Number")
    # plt.ylabel("Coefficient of Static Friction")
    # plt.ylim(bottom=0, top=0.5)
    # plt.grid(linestyle=":", lw=0.5)
    # plt.legend()
    # plt.show()

    return static_friction_coefficients


def kinetic_data_analysis(plot=True):

    min_position = 1
    max_position = 10.644 / 2

    kinetic_friction_coefficients = []
    test_velocities = []

    for test_num in test_nums:
        filename = "data/kinetic/kinetic_test_" + str(test_num) + "_motor_speed_2000_mass_1094.csv"
        position_timestamps, part_positions, force_timestamps, forces = read_data(filename)
        min_idx = (np.where(part_positions > min_position)[0][0])
        max_idx = (np.where(part_positions < max_position)[0][-1])
        lower_limit = int(min_idx)
        upper_limit = int(max_idx)

        _, coeffs = best_line_fit(position_timestamps[lower_limit:upper_limit], part_positions[lower_limit:upper_limit])
        test_velocities.append(coeffs[0])

        if plot:
            plot_data(position_timestamps, part_positions, force_timestamps, forces, lower_limit, upper_limit)

        kinetic_friction_coefficients.append(np.mean(forces) / (object_mass * gravity))

    print("Kinetic Coefficient of Friction = {:.2f} ± {:.2f}\n".format(
        np.mean(kinetic_friction_coefficients), np.std(kinetic_friction_coefficients)))

    # plt.scatter([test_num - 1 for test_num in test_nums], kinetic_friction_coefficients, color='b')
    # plt.axhline(np.mean(kinetic_friction_coefficients), color='b', linestyle='--',
    #             label=r"Average $\mu_k = {:.2f} \pm {:.2f}$".format(np.mean(kinetic_friction_coefficients), np.std(kinetic_friction_coefficients)))
    # plt.xlabel("Trial Number")
    # plt.ylabel("Coefficient of Kinetic Friction")
    # plt.ylim(bottom=0, top=0.5)
    # plt.grid(linestyle=":", lw=0.5)
    # plt.legend()
    # plt.show()

    return kinetic_friction_coefficients


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


def plot_data(position_timestamps, part_positions, force_timestamps, forces, lower_limit=0, upper_limit=-1, static=False):
    if not static:
        force_timestamps_subset = force_timestamps[lower_limit:upper_limit]
        forces_subset = forces[lower_limit:upper_limit]
        alpha = 0.3
    else:
        alpha = 1.0

    fig, ax_1 = plt.subplots()
    ax_1.set_xlabel(r"Time (s)", labelpad=label_pad, fontsize=axes_label_size)
    ax_1.set_ylabel(r"Position (mm)", color='r', labelpad=label_pad, fontsize=axes_label_size)
    ax_1.plot(position_timestamps, part_positions, 'r-', label=r"Position Data", lw=2)
    y_fit_vals, coeffs = best_line_fit(position_timestamps, part_positions)
    ax_1.plot(position_timestamps, y_fit_vals, 'r--', label=r"Velocity = {:.2f} mm/s".format(coeffs[0]), lw=2)

    ax_2 = ax_1.twinx()
    ax_2.set_ylabel(r"Force (N)", color='b', labelpad=label_pad, fontsize=axes_label_size)
    ax_2.set_ylim(bottom=0)

    if not static:
        mean_force = np.mean(forces_subset)
        ax_2.axhline(mean_force, color='b', linestyle='--', label=r"Average Force = {:.2f} N".format(mean_force))
        ax_2.plot(force_timestamps, forces, 'b-', lw=2, alpha=alpha)
        ax_2.plot(force_timestamps_subset, forces_subset, 'b-', label=r"Force Data", lw=2)
    else:
        ax_2.plot(force_timestamps, forces, 'b-', label=r"Force Data", lw=2, alpha=alpha)

    fig.tight_layout()
    ax_2.set_ylim(0, 5.5)

    lines_1, labels_1 = ax_1.get_legend_handles_labels()
    lines_2, labels_2 = ax_2.get_legend_handles_labels()

    bbox_anchor = (0.20, 0.90) if static else (0.86, 0.2)
    location = 'upper left' if static else 'lower right'

    ax_1.tick_params(axis='x', labelsize=tick_label_size)
    ax_1.tick_params(axis='y', colors='r', labelsize=tick_label_size)
    ax_1.spines['left'].set_color('r')
    ax_1.spines['right'].set_visible(False)
    ax_2.tick_params(axis='x', labelsize=tick_label_size)
    ax_2.tick_params(axis='y', colors='b', labelsize=tick_label_size)
    ax_2.spines['right'].set_color('b')
    ax_2.spines['left'].set_visible(False)
    fig.legend(lines_1 + lines_2, labels_1 + labels_2, loc=location,
               bbox_to_anchor=bbox_anchor, fontsize=tick_label_size)

    if static:
        plt.title(r"Static Coefficient of Friction, $\mu_s = {:.2f}$".format(
            np.max(forces) / (object_mass * gravity)), fontsize=title_label_size)
    else:
        plt.title(r"Kinetic Coefficient of Friction, $\mu_s = {:.2f}$".format(
            np.mean(forces) / (object_mass * gravity)), fontsize=title_label_size)

    ax_1.grid(True, which="both", axis='both', ls=":")
    plt.show()


if __name__ == "__main__":

    plt.rcParams["text.usetex"] = True
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams.update({'font.size': 22})
    static_friction_coefficients = static_data_analysis(plot=False)
    kinetic_friction_coefficients = kinetic_data_analysis(plot=False)

    plt.scatter([test_num - 2 for test_num in test_nums], static_friction_coefficients,
                color=static_color, lw=3, marker='o', s=80)
    plt.axhline(np.mean(static_friction_coefficients), color=static_color, linestyle='--', lw=3,
                label=r"$\mu_s = {:.2f} \pm {:.2f}$".format(np.mean(static_friction_coefficients), np.std(static_friction_coefficients)))

    plt.scatter([test_num - 2 for test_num in test_nums], kinetic_friction_coefficients,
                color=kinetic_color, lw=3, marker='o', s=80)
    plt.axhline(np.mean(kinetic_friction_coefficients), color=kinetic_color, linestyle='--', lw=3,
                label=r"$\mu_k = {:.2f} \pm {:.2f}$".format(np.mean(kinetic_friction_coefficients), np.std(kinetic_friction_coefficients)))

    plt.xlabel("Trial Number", labelpad=15)
    plt.ylabel("Coefficient of Friction", labelpad=15)
    plt.ylim(bottom=0, top=0.5)
    plt.grid(linestyle=":", lw=0.5)
    plt.legend()
    plt.show()
