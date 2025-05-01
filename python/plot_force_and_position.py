import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def read_data(filename: str):
    logged_data = pd.read_csv(filename)
    position_timestamps = logged_data["position_timestamp"].to_numpy() / 1000000
    part_positions = logged_data["position"].to_numpy()
    force_timestamps = logged_data["force_timestamp"].to_numpy() / 1000000
    forces = logged_data["force"].to_numpy()

    return position_timestamps, part_positions, force_timestamps, forces


def plot_data(position_timestamps, part_positions, force_timestamps, forces):
    fig, ax_1 = plt.subplots()
    ax_1.set_xlabel("Time (s)")
    ax_1.set_ylabel("Position (mm)")
    ax_1.plot(position_timestamps, part_positions, 'r-', label="position", lw=2)

    ax_2 = ax_1.twinx()
    ax_2.set_ylabel("Force (N)")
    ax_2.plot(force_timestamps, forces, 'b-', label="force", lw=2)

    fig.tight_layout()
    plt.grid(True, which="both", ls="--")
    plt.show()


if __name__ == "__main__":
    filename = "sensor_data_log.csv"
    position_timestamps, part_positions, force_timestamps, forces = read_data(filename)
    plot_data(position_timestamps, part_positions, force_timestamps, forces)
