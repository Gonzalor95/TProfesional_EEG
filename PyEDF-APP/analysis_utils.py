#!/usr/bin/python

import os
import resampy
import math
import numpy as np
from scipy.signal import butter, lfilter, freqz
from scipy import stats
import yaml
from modules.EDFWorker import EDFWorker
import matplotlib.pyplot as plt
from modules.TestingSignals import TestingSignalsWorker

from typing import Sequence

from abc import ABC

# This value came up magically, right?
EEG_EDF_OFFSET = 187.538  # uV

# Parameters to correlate from a chunk of the received signal
SIGNAL_WINDOW_OFFSET = 12000
SIGNAL_WINDOW_SIZE = 4000


class Filter(ABC):
    def __init__(self, data=None, fs=None, order=None, cutoff=None, window_size=None):
        self.data = data
        self.fs = fs
        self.order = order
        self.cutoff = cutoff
        self.window_size = window_size

    def configure_filter(
        self, data=None, fs=None, order=None, cutoff=None, window_size=None
    ):
        """
        Keep any previous configuration. Re-set any non-set configuration
        """
        self.data = self.data if self.data else data
        self.fs = self.fs if self.fs else fs
        self.order = self.order if self.order else order
        self.cutoff = self.cutoff if self.cutoff else cutoff
        self.window_size = self.window_size if self.window_size else window_size

    def apply_filter(self):
        raise NotImplementedError()


class Butter(Filter):
    def __init__(self, data=None, fs=None, order=None, cutoff=None, high_pass=False):
        super().__init__(data, fs, order, cutoff)
        self.high_pass = high_pass

    def butter_(self):
        return butter(
            self.order,
            self.cutoff,
            fs=self.fs,
            btype="high" if self.high_pass else "low",
            analog=False,
        )

    def apply_filter(self):
        b, a = self.butter_()
        return lfilter(b, a, self.data)


class SMA(Filter):
    def __init__(self, data=None, window_size=None):
        super().__init__(data, window_size)

    def apply_filter(self):
        moving_averages = []
        i = 0
        # Loop through the array t o
        # consider every window of size 3
        while i < len(self.data) - self.window_size + 1:
            # Calculate the average of current window
            window_average = round(
                np.sum(self.data[i : i + self.window_size]) / self.window_size, 2
            )

            # Store the average of current
            # window in moving average list
            moving_averages.append(window_average)

            # Shift window to right by one position
            i += 1

        return moving_averages


def plot_signal_comparison(s1, s2, title, label_1=None, label_2=None, input_lag=0):
    """
    Plots 2 signals. Applies an input lag to correct time position of the 2nd one
    """
    input_time_axis = np.arange(0, len(s1))
    output_time_axis = np.arange(0, len(s2))
    plt.plot(input_time_axis, s1, "r", label="Input signal" if not label_1 else label_1)
    plt.plot(
        output_time_axis - input_lag,
        s2,
        "b--",
        label="Output signal" if not label_2 else label_2,
    )
    plt.grid(True)
    plt.title(title)
    plt.legend()
    plt.show()


def calculate_mse(s1, s2):
    return np.square(s1 - s2).mean(axis=None)

def calculate_snr(input, output):
    """Calcula SNR considerando Noise = abs(Input-Output)"""

    input_RMS = np.square(input).mean(axis=None)
    noise_RMS = np.square(input-output).mean(axis=None)
    return input_RMS/noise_RMS

def calculate_log_snr(input, output):
    """Calcula SNR considerando Noise = abs(Input-Output)"""

    
    return 10 * np.log10(calculate_snr(input=input,output=output))


def calculate_mse_for_signal_window(s1, s2, lag, window_size):
    s1 = s1[-lag : window_size - lag]
    mse = calculate_mse(s1, s2)
    print(f"Mean Square Error is: {mse}")
    return mse


def get_correlation_offset(input_signal, output_signal):
    Cmatrix = np.correlate(output_signal, input_signal, "full")
    Cmatrix = Cmatrix / max(Cmatrix)
    index = np.where(Cmatrix == 1)[0][0]

    return index - len(input_signal)


def get_correlation_offset_for_window(input_signal, output_signal):
    """
    Correlate a chunk of the measured signal with the full input signal.
    Additionally plots a graph that shows where the chunk of signal fits the most.
    Calculates the MSE between the signals in the range of most correlation
    Returns the offset that places the chunk of measured signal where it correlates the most with the input one
    """
    windowed_output_signal = output_signal[
        SIGNAL_WINDOW_OFFSET : SIGNAL_WINDOW_OFFSET + SIGNAL_WINDOW_SIZE
    ]
    input_lag = get_correlation_offset(input_signal, windowed_output_signal)
    # Plot correlation analysis
    plot_signal_comparison(
        input_signal, windowed_output_signal, "Signal correlation analysis", input_lag
    )
    # Calculate MSE for current window with corresponding chunk of original signal
    calculate_mse_for_signal_window(
        input_signal, windowed_output_signal, input_lag, SIGNAL_WINDOW_SIZE
    )
    return input_lag


def pad_shortest_signal(s1, s2, padrange):
    if len(s1) > len(s2):
        s2 = np.pad(s2, (0, padrange), "constant", constant_values=(0, 0))
    else:
        s1 = np.pad(s1, (0, padrange), "constant", constant_values=(0, 0))
    return s1, s2


def read_config_file(root_dir):
    """
    Read the yaml configuration file and load it
    """
    config_path = os.path.join(root_dir, "config", "device_params.yaml")
    with open(config_path, "r") as file:
        try:
            return yaml.safe_load(file)
        except Exception as e:
            print(f"Error: {e}")


def apply_filters(filters: Sequence[Filter], signal: Sequence[float]):
    for filter in filters:
        filter.configure_filter(data=signal)
        signal = filter.apply_filter()
    return signal


def generate_input_signal(
    input_signal: str,
    is_testing: bool,
    channels: list,
    t_signal_type="Sinusoidal",
    t_freq=1,
    t_amp=199,
    t_sr=500,
    t_dur=5,
    filters: Sequence[Filter] = [],
    resample=False,
):
    curr_script_dir = os.path.dirname(os.path.realpath(__file__))
    config = read_config_file(curr_script_dir)
    # Prepare signal workers
    if is_testing:
        # We generate a test sinusoidal signal of 10 Hz frequency, 199 uV amplitude, 500 Hz sample rate and 5 second duration
        input_signal_worker = TestingSignalsWorker(config)
        input_signal_worker.generateTestingSignal(
            t_signal_type, t_freq, t_amp, t_sr, t_dur
        )
        input_signal_worker.setSelectedSimTime([0, t_dur])
        input_signal_worker.setSelectedChannels(channels)
    else:
        input_signal_filepath = os.path.join(
            curr_script_dir, "edf_samples", f"{input_signal}.edf"
        )
        input_signal_worker = EDFWorker(config)
        input_signal_worker.readEDF(input_signal_filepath)
        input_signal_worker.setSelectedChannels(channels)
    # TODO: Make it so that we don't always use first channel ([0][1])
    input_signal = (
        input_signal_worker.signal_data_.physical_signal
        if is_testing
        else input_signal_worker.signal_data_.physical_signals_and_channels[0][1]
    )
    input_signal = apply_filters(filters, input_signal)
    if resample:
        input_signal = resampy.resample(
            input_signal, input_signal_worker.getSampleRate(), 200
        )
    return input_signal


def generate_output_signal(
    signal_filename, channels, filter: Filter = None, resample=False
):
    """ 
    Generates output signal. Returns single signal if channels is string or len(channels) == 1.
    Else returns list of dict as:
        ['Channel': <ch_name>, 'Signal': <ch_signal>]
    """
    curr_script_dir = os.path.dirname(os.path.realpath(__file__))
    config = read_config_file(curr_script_dir)

    output_signal_filepath = os.path.join(
        curr_script_dir, "edf_samples", "data_analysis", f"{signal_filename}.edf"
    )
    output_signal_worker = EDFWorker(config)
    output_signal_worker.readEDF(output_signal_filepath)
    output_signal_worker.setSelectedChannels(channels)

    output_signals_and_channels = []
    for tuple in output_signal_worker.signal_data_.physical_signals_and_channels:
        if (tuple[0] in channels):

            ch = tuple[0]
            output_signal = tuple[1]
            output_signal = (output_signal - EEG_EDF_OFFSET)

            if filter:
                filter.configure_filter(data=output_signal)
                output_signal = filter.apply_filter()
            if resample:
                output_signal = resampy.resample(
                    output_signal, output_signal_worker.getSampleRate(), 200
                )
            output_signals_and_channels.append({'Channel': ch, 'Signal': output_signal})


    return output_signals_and_channels if len(output_signals_and_channels) > 1 else output_signals_and_channels[0]['Signal'] 


# # We can try to apply a filter to see if it improves
# input_signal = butter_lowpass_filter(input_signal, 30, input_signal_worker.getSampleRate(), order=2)
# #output_signal = butter_lowpass_filter(output_signal, 70, output_signal_worker.getSampleRate(), order=5)

# input_signal = butter_highpass_filter(input_signal, 0.8, input_signal_worker.getSampleRate(), order=2)
# #output_signal = butter_highpass_filter(output_signal, 0.1, output_signal_worker.getSampleRate(), order=5)

# input_signal_resampled = resampy.resample(input_signal, input_signal_worker.getSampleRate(), args.sample_rate)
# output_signal_resampled = resampy.resample(output_signal, output_signal_worker.getSampleRate(), args.sample_rate)

# if not args.test_signal:
#     output_signal_resampled = output_signal_resampled[13000:15000]

# plt.plot(output_signal_resampled)
# plt.show()

# print(f"Resampled input signal length = {len(input_signal_resampled)}")
# print(f"Resampled Output signal length = {len(output_signal_resampled)}")

# input_lag = get_correlation_offset(input_signal_resampled, output_signal_resampled)

# output_time_axis = np.arange(0, len(output_signal_resampled)) #input_signal_worker.getDuration(), time_step)
# input_time_axis = np.arange(0, len(input_signal_resampled))
# print(f"Before plotting we have:\nInput time axis length: \t{len(input_time_axis)}\nOutput time axis length: \t{len(output_time_axis)}\nInput signal length: \t{len(input_signal_resampled)}\nOutput signal length: \t{len(output_signal_resampled)}\n")#Input lag: \t{input_lag}\n")

# input_signal_name = args.input_signal if not args.test_signal else 'Test Signal'
# plot_title = f"{input_signal_name} Vs {args.measured_signal}"

# Cmatrix = np.correlate(output_signal_resampled, input_signal_resampled, 'full')
# Cmatrix = Cmatrix/max(Cmatrix)
# index = np.where(Cmatrix ==1)[0][0]

# Cmatrix[index] = max(input_signal_resampled)

# time_step = 1/args.sample_rate # need to get rid of the 100

# # input_lag = (index - len(input_signal_resampled))# * time_step
# # output_lag = (index - len(output_signal_resampled))# * time_step
# # print(f"Input lag is: {input_lag}. Output lag is: {output_lag}")

# #print(f"Before plotting we have:\nTime axis length: \t{len(time_axis)}\nInput signal length: \t{len(input_signal_resampled)}\nOutput signal length: \t{len(output_signal_resampled)}\nInput lag: \t{input_lag}\nOutput lag: \t{output_lag}\n")

# input_signal_resampled = input_signal_resampled[abs(input_lag):2000+abs(input_lag)]

# time_axis_in = np.arange(0,len(input_signal_resampled)) #* time_step, time_step )#input_signal_worker.getDuration(), time_step)
# time_axis_out = np.arange(0,len(output_signal_resampled))#  *time_step, time_step )#output_signal_worker.getDuration(), time_step)

# plt.plot(time_axis_in, input_signal_resampled, 'r', label="Input signal")
# plt.plot(time_axis_out, output_signal_resampled, 'b', label="Measured signal")
# plt.plot(abs(input_signal_resampled-output_signal_resampled),'g', label="Error")
# mse = (np.square(input_signal_resampled - output_signal_resampled)).mean(axis=None)


# pctError = abs(np.mean(100 * abs(input_signal_resampled - output_signal_resampled) / input_signal_resampled))


# print(f"mse = {mse}")
# print(f"rmse = {math.sqrt(mse)}")
# print(f"pctError = {pctError} %")

# plt.grid(True)
# plt.title(f"{input_signal_name} Vs {args.measured_signal}")
# plt.legend()
# plt.show()


# rest =stats.ttest_ind(input_signal_resampled, output_signal_resampled)
# print(rest)


# input_filtered = SMA_filter(input_signal_resampled, 100)
# output_filtered = SMA_filter(output_signal_resampled, 100)

# plt.plot(input_filtered, 'r', label="Input signal")
# plt.plot(output_filtered, 'b--', label="Measured signal")
# plt.title(f"Input filtered with SMA Vs Output filtered with SMA")
# plt.legend()
# plt.show()

# #np.savetxt('input_signal_resampled_fitted.dat', input_signal_resampled)
# #np.savetxt('output_signal_resampled_fitted.dat', output_signal_resampled)