import os
import resampy
import math
import numpy as np
from scipy.signal import (
    butter,
    lfilter,
    spectrogram,
    periodogram,
    filtfilt,
    argrelextrema,
)
from scipy.fft import fft, fftfreq
from scipy import stats
import yaml
from modules.EDFWorker import EDFWorker
import matplotlib.pyplot as plt
from modules.TestingSignals import TestingSignalsWorker
import analysis_utils as eeg_utils


class CommonModeAverageSignal:
    def __init__(self):
        self.signals = []
        self.correlated_signals = []
        self.offset = 0
        self.data = None

    def add_new_signal(self, signal):
        self.signals.append(signal)

    def plot_all_signals(self):
        for idx, signal in enumerate(self.correlated_signals):
            plt.plot(signal, label=f"Signal {idx}")

    def plot_average_signal(self):
        plt.plot(self.data, label="Average signal")

    def correlate_all_signals(self, sample_signal):
        for idx, signal in enumerate(self.signals):
            offset = eeg_utils.get_correlation_offset(sample_signal, signal)
            if offset > 0:
                self.correlated_signals.append(signal[offset:])
            else:
                self.correlated_signals.append(
                    np.concatenate((np.zeros(-offset), signal))
                )
            print(
                f"Offset was: {offset}. Length of the correalted signal is: {len(self.correlated_signals[idx])}"
            )

    def get_shortest_signal(self):
        return min(len(ls) for ls in self.correlated_signals)

    def get_average_signal(self):
        self.data = [
            sum(signal[i] for signal in self.correlated_signals)
            / len(self.correlated_signals)
            for i in range(self.get_shortest_signal())
        ]


def equalize_signal_lengths(s1, s2):
    min_len = min(len(s1), len(s2))
    return s1[:min_len], s2[:min_len]


def plot_interval(
    axis, s1, s2, title, s1_label, s2_label, time_step, from_t=None, to_t=None
):
    if from_t is not None and to_t is not None:
        s1 = s1[from_t:to_t]
        s2 = s2[from_t:to_t]
    a, b = equalize_signal_lengths(s1, s2)
    time_axis = np.arange(start=0, stop=len(a) * time_step, step=time_step)
    axis[0].plot(time_axis, b, "r", label=s1_label)
    axis[0].plot(time_axis, a, "b--", label=s2_label)
    axis[0].set_title(title)
    axis[0].set_xlabel("Tiempo [seg]")
    axis[0].set_ylabel("Tensión [uV]")
    axis[0].legend()
    axis[0].grid()

    mse = eeg_utils.calculate_mse(a, b)
    axis[1].plot(time_axis, a - b, "g", label="Error [Input - Output]")
    axis[1].set_title(f"ECM = {mse:.2f}")
    axis[1].set_xlabel("Tiempo [seg]")
    axis[1].set_ylabel("Tensión [uV]")
    axis[1].legend()
    axis[1].grid()

    return axis


filters = [
    eeg_utils.Butter(high_pass=False, fs=200, order=2, cutoff=30),
    eeg_utils.Butter(high_pass=True, fs=200, order=2, cutoff=0.8),
]

sample_signal = eeg_utils.generate_input_signal(
    "common_mode_sample1", False, ["Fp1"], resample=True
)
filtered_sample_signal = eeg_utils.apply_filters(filters, sample_signal)
full_signal = eeg_utils.generate_output_signal("Promediado4Veces", ["Fp1"])

use_filter = True
if use_filter:
    sample_signal = filtered_sample_signal[15 * 200 : 85 * 200]
    filter_epilogue = "con filtro"
else:
    sample_signal = sample_signal[15 * 200 : 85 * 200]
    filter_epilogue = "sin filtro"

avg_signal = CommonModeAverageSignal()
avg_signal.add_new_signal(full_signal[3400:17900])
avg_signal.add_new_signal(full_signal[18000:32500])
avg_signal.add_new_signal(full_signal[32600:46720])
avg_signal.add_new_signal(full_signal[46750:61200])

avg_signal.correlate_all_signals(sample_signal)
avg_signal.get_average_signal()

mse = eeg_utils.calculate_mse(*equalize_signal_lengths(sample_signal, avg_signal.data))
time_step = 1.0 / 200.0
## Plot comparison
errors_title = []
figure, axis = plt.subplots(2, 1)
for idx, signal in enumerate(avg_signal.correlated_signals):
    time_axis = np.arange(start=0, stop=len(signal) * time_step, step=time_step)
    time_axis, signal = equalize_signal_lengths(time_axis, signal)
    axis[0].plot(
        time_axis,
        signal,
        "--",
        label=f"Señal n°: {idx+1}",
    )
    reshaped_signal, reshaped_sample = equalize_signal_lengths(signal, sample_signal)
    axis[1].plot(
        np.arange(start=0, stop=len(reshaped_sample) * time_step, step=time_step),
        reshaped_sample - reshaped_signal,
        label=f"Error señal n°: {idx+1}",
    )
    print(
        f"Error for full signal {idx+1} is: {eeg_utils.calculate_mse(reshaped_signal, reshaped_sample):.2f}"
    )
    errors_title.append(
        f"Error {idx+1}: {eeg_utils.calculate_mse(reshaped_signal, reshaped_sample):.2f}"
    )
time_axis = np.arange(start=0, stop=len(sample_signal) * time_step, step=time_step)
axis[0].plot(time_axis, sample_signal, "b--", label="Sample signal")
axis[0].set_title(
    f"{len(avg_signal.correlated_signals)} señales common_mode vs señal EEG original {filter_epilogue}"
)
axis[0].set_xlabel("Tiempo [seg]")
axis[0].set_ylabel("Tensión [uV]")
axis[0].legend()
axis[0].grid()

axis[1].set_title(
    "\n".join(
        [
            " ".join(pair)
            for pair in [
                errors_title[i : i + 2] for i in range(0, len(errors_title), 2)
            ]
        ]
    )
)
axis[1].set_xlabel("Tiempo [seg]")
axis[1].set_ylabel("Tensión [uV]")
axis[1].legend()
axis[1].grid()

plt.show()


### Plot average signal in the whole interval
figure, axis = plt.subplots(2, 1)
axis = plot_interval(
    axis,
    sample_signal,
    avg_signal.data,
    f"Señal promedio vs sample {filter_epilogue}.",
    "Señal promedio",
    "Sample signal",
    time_step,
)
plt.show()


### Plot 4 signals in a smaller interval

from_t = 15 * 200
to_t = 20 * 200


figure, axis = plt.subplots(2, 1)
errors_title = []
interval_sample_signal = sample_signal[from_t:to_t]
interval_time_axis = np.arange(
    start=0, stop=len(interval_sample_signal) * time_step, step=time_step
)

for idx, signal in enumerate(avg_signal.correlated_signals):
    signal = signal[from_t:to_t]
    time_axis_2 = np.arange(start=0, stop=len(signal) * time_step, step=time_step)
    time_axis_2, signal = equalize_signal_lengths(time_axis_2, signal)
    axis[0].plot(
        time_axis_2,
        signal,
        "--",
        label=f"Señal n°: {idx+1}",
    )
    reshaped_signal, reshaped_sample = equalize_signal_lengths(
        signal, interval_sample_signal
    )
    axis[1].plot(
        np.arange(start=0, stop=len(reshaped_sample) * time_step, step=time_step),
        reshaped_sample - reshaped_signal,
        label=f"Error señal n°: {idx+1}",
    )
    print(
        f"Error for interval [{from_t}]-[{to_t}] signal {idx+1} is: {eeg_utils.calculate_mse(reshaped_signal, reshaped_sample):.2f}"
    )
    errors_title.append(
        f"Error {idx+1}: {eeg_utils.calculate_mse(reshaped_signal, reshaped_sample):.2f}"
    )

axis[0].plot(interval_time_axis, interval_sample_signal, "b--", label="Sample signal")
axis[0].set_title(
    f"{len(avg_signal.correlated_signals)} señales common_mode vs señal EEG original {filter_epilogue} en intervalo {from_t/200}-{to_t/200}s"
)
axis[0].set_xlabel("Tiempo [seg]")
axis[0].set_ylabel("Tensión [uV]")
axis[0].legend()
axis[0].grid()
axis[1].set_title(
    "\n".join(
        [
            " ".join(pair)
            for pair in [
                errors_title[i : i + 2] for i in range(0, len(errors_title), 2)
            ]
        ]
    )
)
axis[1].set_xlabel("Tiempo [seg]")
axis[1].set_ylabel("Tensión [uV]")
axis[1].legend()
axis[1].grid()

plt.show()

## Average signal in a smaller interval

figure, axis = plt.subplots(2, 1)
axis = plot_interval(
    axis,
    sample_signal,
    avg_signal.data,
    f"Señal promedio vs sample {filter_epilogue} en intervalo {from_t/200}-{to_t/200}s.",
    "Señal promedio",
    "Sample signal",
    time_step,
    from_t,
    to_t,
)
plt.show()
