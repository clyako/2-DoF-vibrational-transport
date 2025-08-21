import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from scipy.signal import find_peaks
import pandas as pd
import numpy as np

sampling_frequency = 2000
waveform_frequency = 20    # Hz
waveform_period = 1 / waveform_frequency

lower_position_threshold = 5.056
upper_position_threshold = 10.644

position_reset = 1

calculate_velocity_using_peaks = True
use_colormap = True
cmap = plt.cm.BuPu
colors = cmap(np.linspace(0.35, 1.0, 4))


def varying_amax_analysis(plot: bool = False):
    target_forces = np.array([50, 48, 46, 44, 42, 40, 38, 36, 34, 32, 30])
    amax_values = [5, 10, 15, 20]

    for amax, c in zip(amax_values, colors):
        filename = "data/object_velocity_varying_amax_normal_force/frequency_20_amin_0.7_amax_" + str(amax) + ".csv"
        _, mean_velocities, std_velocities = read_data(filename, plot=plot)
        plt.plot(target_forces, mean_velocities, color=c, linestyle='-',
                 linewidth=4, label=r'$a_{{slip}} = {:.0f}\:g$'.format(amax))
        # Plot shaded region for standard deviation
        plt.fill_between(target_forces,
                         mean_velocities - std_velocities,
                         mean_velocities + std_velocities,
                         color=c, alpha=0.3)  # alpha controls transparency
    plt.xlabel(r"Target Force (N)", labelpad=15)
    plt.ylabel(r"Average Velocity (mm/s)", labelpad=15)
    plt.title(r"Average Part Velocity ($f = 20$ Hz, $a_{{stick}} = 0.3\:g$)", pad=15)
    plt.ylim(0)
    plt.tight_layout()
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=len(amax_values))
    plt.grid(color='grey', linestyle=':', linewidth=0.5)
    plt.show()

    _, ax = plt.subplots(constrained_layout=True)
    aspect_ratio = 1/4
    ax.set_aspect(aspect_ratio, adjustable='box')

    amax_values = [5, 10, 15, 20]

    n_series = len(amax_values)
    force_spacing = np.min(np.diff(np.sort(target_forces)))
    group_width = 0.9 * force_spacing   # still leave margin between groups

    gap_fraction = 0.1   # fraction of group width reserved for spaces
    usable_width = group_width * (1 - gap_fraction)
    bar_width = usable_width / n_series

    all_y = []  # collect all bar heights

    for i, (amax, c) in enumerate(zip(amax_values, colors)):
        filename = f"data/object_velocity_varying_amax_normal_force/frequency_20_amin_0.7_amax_" + str(amax) + ".csv"
        _, mean_velocities, std_velocities = read_data(filename, plot=plot, amax=True)

        x_positions = target_forces - group_width/2 + (i + 0.5) * (group_width / n_series)

        for j, (xi, yi) in enumerate(zip(x_positions, mean_velocities)):
            all_y.append(yi)
            # Make corner radius proportional to bar width
            if j == 0:
                rect_round = FancyBboxPatch(
                    (xi - bar_width/2, 0), bar_width, yi,
                    boxstyle=f"round,pad=0,rounding_size=0.09",
                    linewidth=0,
                    facecolor=c,
                    edgecolor=c,
                    label=r'$a_{{stick}} = {:.1f}\:g$'.format(amax),
                    mutation_aspect=1 / aspect_ratio
                )
            else:
                rect_round = FancyBboxPatch(
                    (xi - bar_width/2, 0), bar_width, yi,
                    boxstyle=f"round,pad=0,rounding_size=0.09",
                    linewidth=0,
                    facecolor=c,
                    edgecolor=c,
                    mutation_aspect=1 / aspect_ratio
                )
            rect_square = FancyBboxPatch(
                (xi - bar_width/2, 0), bar_width, yi / 2,
                boxstyle=f"round,pad=0,rounding_size=0.0",
                linewidth=0,
                facecolor=c,
                edgecolor=c,
            )

            ax.add_patch(rect_round)
            ax.add_patch(rect_square)

    # axis labels etc.
    ax.set_xlabel(r"Target Force (N)", labelpad=15)
    ax.set_ylabel(r"Average Part Velocity (mm/s)", labelpad=15)
    ax.set_title(r"$f = 20$ Hz, $a_{{stick}} = 0.3\:g$", pad=15)
    ax.set_xticks(target_forces)
    ax.set_xticklabels([str(f) for f in target_forces])

    # scale y-axis to show all bars fully
    ymax = max(all_y) * 1.1
    ax.set_ylim(0, ymax)

    # shrink x-limits to wrap bars tightly
    ax.set_xlim(target_forces[-1] - group_width/1.5,
                target_forces[0] + group_width/1.5)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=len(amax_values))
    ax.grid(color='grey', linestyle=':', linewidth=0.5)
    plt.show()


def varying_amin_analysis(plot: bool = False):
    _, ax = plt.subplots(constrained_layout=True)
    aspect_ratio = 1/3
    ax.set_aspect(aspect_ratio, adjustable='box')

    amin_values = [0.4, 0.6, 0.8, 1.0]
    # if use_colormap:
    #     colors = cmap(np.linspace(0.5, 1.0, 4))
    # else:
    #     colors = ['crimson', 'seagreen', 'darkorange', 'royalblue']

    target_forces = np.array([50, 40, 30])

    n_series = len(amin_values)
    group_width = 4.0   # total width allotted per force group
    bar_width = group_width / n_series * 0.9   # each bar's width

    all_y = []  # collect all bar heights

    for i, (amin, c) in enumerate(zip(amin_values, colors)):
        filename = f"data/object_velocity_varying_amin_normal_force/frequency_15_amin_{amin}_amax_10.csv"
        _, mean_velocities, _ = read_data(filename, plot=plot, amax=False)

        # x_positions = target_forces - group_width/2 + (i + 0.5) * bar_width
        x_positions = target_forces - group_width/2 + (i + 0.5) * (group_width / n_series)

        for j, (xi, yi) in enumerate(zip(x_positions, mean_velocities)):
            all_y.append(yi)
            # Make corner radius proportional to bar width
            if j == 0:
                rect_round = FancyBboxPatch(
                    (xi - bar_width/2, 0), bar_width, yi,
                    boxstyle=f"round,pad=0,rounding_size=0.2",
                    linewidth=0,
                    facecolor=c,
                    edgecolor=c,
                    label=r'$a_{{stick}} = {:.1f}\:g$'.format(amin),
                    mutation_aspect=1 / aspect_ratio
                )
            else:
                rect_round = FancyBboxPatch(
                    (xi - bar_width/2, 0), bar_width, yi,
                    boxstyle=f"round,pad=0,rounding_size=0.2",
                    linewidth=0,
                    facecolor=c,
                    edgecolor=c,
                    mutation_aspect=1 / aspect_ratio
                )
            rect_square = FancyBboxPatch(
                (xi - bar_width/2, 0), bar_width, yi / 2,
                boxstyle=f"round,pad=0,rounding_size=0.0",
                linewidth=0,
                facecolor=c,
                edgecolor=c,
            )

            ax.add_patch(rect_round)
            ax.add_patch(rect_square)

    # axis labels etc.
    ax.set_xlabel(r"Target Force (N)", labelpad=15)
    ax.set_ylabel(r"Average Part Velocity (mm/s)", labelpad=15)
    ax.set_title(r"$f = 15$ Hz, $a_{{slip}} = 10.0\:g$", pad=15)
    ax.set_xticks(target_forces)
    ax.set_xticklabels([str(f) for f in target_forces])

    # scale y-axis to show all bars fully
    ymax = max(all_y) * 1.1
    ax.set_ylim(0, ymax)

    # shrink x-limits to wrap bars tightly
    ax.set_xlim(target_forces[-1] - group_width/1.5,
                target_forces[0] + group_width/1.5)

    ax.legend()
    ax.grid(color='grey', linestyle=':', linewidth=0.5)
    plt.show()


def read_data(filename: str, plot: bool = False, amax: bool = True):
    mean_forces = []
    mean_velocities = []
    std_velocities = []

    logged_data = pd.read_csv(filename)
    reset_indices = logged_data.index[logged_data['position'].diff() < -position_reset].tolist()

    # # Add start and end indices to define experiment segments
    exp_indices = [0] + reset_indices + [len(logged_data)]

    experiments = []
    for i in range(len(exp_indices) - 1):
        start, end = exp_indices[i], exp_indices[i+1]
        experiments.append(logged_data.iloc[int(start):int(end)].reset_index(drop=True))

    if amax:
        experiments = experiments[:11]
    else:
        experiments = experiments[:3]

    for i, exp in enumerate(experiments, 1):
        # Time in seconds (relative)
        exp['position_timestamp'] -= exp['position_timestamp'].iloc[0]
        exp['force_timestamp'] -= exp['force_timestamp'].iloc[0]

        # Average force
        avg_force = -exp['force'].mean()

        # --- Step 3: Peak detection ---
        # Find first index where position crosses lower threshold
        lower_mask = exp['position'] >= lower_position_threshold
        if lower_mask.any():
            first_lower_idx = lower_mask.idxmax()  # first True index
        else:
            first_lower_idx = 0

        # Find first index where position crosses upper threshold
        upper_mask = exp['position'] >= upper_position_threshold
        if upper_mask.any():
            first_upper_idx = upper_mask.idxmax()  # first True index
        else:
            first_upper_idx = len(exp['position'])

        # Extract subset between these indices
        subset = exp.loc[first_lower_idx:first_upper_idx]

        t = subset['position_timestamp'] * 1e-6
        x = subset['position']

        if calculate_velocity_using_peaks:
            peak_indices, _ = find_peaks(x, distance=sampling_frequency / waveform_frequency)

            if len(peak_indices) < 2:
                raise ValueError("Not enough peaks found to compute velocities.")

            # --- per-cycle velocities between consecutive peaks ---
            t_peaks = t.iloc[peak_indices]
            x_peaks = x.iloc[peak_indices]
            dt = np.diff(t_peaks)        # s between peaks
            dx = np.diff(x_peaks)        # mm rise between peaks
            velocities = dx / dt                 # mm/s for each cycle
        else:
            # Loop through each point
            for j in range(len(t)):
                # Find the index of the point period ahead
                target_time = t.iloc[j] + waveform_period
                # Find the closest index
                k = np.searchsorted(t, target_time)
                if k < len(t):
                    # Velocity estimate
                    v = (x.iloc[k] - x.iloc[j]) / (t.iloc[k] - t.iloc[j])
                    velocities.append(v)

        velocities = np.array(velocities)

        # Compute mean and standard deviation
        avg_velocity = np.mean(velocities)
        std_velocity = np.std(velocities)

        # print("Average velocity: {:.2f} ± {:.2f} mm/s".format(avg_velocity, std_velocity))
        # print("Average velocity: {:.2f} mm/s".format(avg_velocity))

        mean_forces.append(avg_force)
        mean_velocities.append(avg_velocity)
        std_velocities.append(std_velocity)

        if plot:
            plot_data(t, x, exp, i, peak_indices)

    return np.asarray(mean_forces), np.asarray(mean_velocities), np.asarray(std_velocities)

    # return position_timestamps, part_positions, force_timestamps, forces


def plot_data(t, x, exp, i, peak_indices):
    # --- Plot ---
    _, ax1 = plt.subplots(figsize=(7, 4))

    # Position (left y-axis)
    ax1.plot(t, x, 'b-', label="Position (mm)")
    ax1.plot(exp['position_timestamp'] * 1e-6, exp['position'], 'b-', alpha=0.3, label="Position (mm)")
    ax1.scatter(t.iloc[peak_indices], x.iloc[peak_indices], c='k')
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Position (mm)", color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Force (right y-axis)
    avg_force = -exp['force'].mean()
    ax2 = ax1.twinx()
    ax2.plot(exp['force_timestamp'] * 1e-6, -exp['force'], 'r-', label="Force (N)")
    ax2.axhline(avg_force, color='r', linestyle='--',
                label=f"Avg Force = {avg_force:.2f}")
    ax2.set_ylabel("Force (N)", color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.set_ylim(0, 55)

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right")

    plt.title(f"Experiment {i}: Position & Force")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # mean_forces, mean_velocities, std_velocities = read_data(
    #     "data/object_velocity_varying_amax/frequency_20_amin_0.7_amax_10.csv", plot=True)
    plt.rcParams["text.usetex"] = True
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams.update({'font.size': 22})

    varying_amax_analysis(plot=False)
    varying_amin_analysis(plot=False)
