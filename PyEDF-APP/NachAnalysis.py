#!/usr/bin/python

import os
import resampy
import numpy as np
from scipy.signal import butter, lfilter, freqz
import yaml
from modules.EDFWorker import EDFWorker
import matplotlib.pyplot as plt
from modules.TestingSignals import TestingSignalsWorker
import argparse


def butter_lowpass(cutoff, fs, order=5):
    return butter(order, cutoff, fs=fs, btype='low', analog=False)

def butter_highpass(cutoff, fs, order=5):
    return butter(order, cutoff, fs=fs, btype='high', analog=False)

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y



# This value came up magically, right?
EEG_EDF_OFFSET = 187.538 # uV

# Parameters to correlate from a chunk of the received signal
SIGNAL_WINDOW_OFFSET = 12000
SIGNAL_WINDOW_SIZE = 4000

def plot_signal_comparison(s1, s2, title, input_lag=0):
    input_time_axis = np.arange(0, len(s1))
    output_time_axis = np.arange(0, len(s2))
    plt.plot(input_time_axis, s1, 'r', label="Input signal") 
    plt.plot(output_time_axis - input_lag, s2, 'b--', label="Output signal")
    plt.grid(True)
    plt.title(title)
    plt.legend()
    plt.show()

def calculate_mse_for_signal_window(s1, s2, lag, window_size):
    s1 = s1[-lag:window_size-lag]
    mse = (np.square(s1 - s2)).mean(axis=None)
    print(f"Mean Square Error is: {mse}")
    return mse

def get_correlation_offset(input_signal, output_signal):
    """
    Correlate a chunk of the measured signal with the full input signal.
    Additionally plots a graph that shows where the chunk of signal fits the most.
    Calculates the MSE between the signals in the range of most correlation
    Returns the offset that places the chunk of measured signal where it correlates the most with the input one 
    """
    windowed_output_signal = output_signal[SIGNAL_WINDOW_OFFSET:SIGNAL_WINDOW_OFFSET+SIGNAL_WINDOW_SIZE]
    Cmatrix = np.correlate(windowed_output_signal, input_signal, 'full')
    Cmatrix = Cmatrix/max(Cmatrix)
    index = np.where(Cmatrix ==1)[0][0]

    Cmatrix[index] = max(input_signal)

    input_lag = index - len(input_signal)
    # Plot correlation analysis
    plot_signal_comparison(input_signal, windowed_output_signal, "Signal correlation analysis", input_lag)
    # Calculate MSE for current window with corresponding chunk of original signal
    calculate_mse_for_signal_window(input_signal_resampled, windowed_output_signal, input_lag, SIGNAL_WINDOW_SIZE)
    return input_lag
    
def pad_shortest_signal(s1, s2, padrange):
    if len(s1) > len(s2):
        s2 = np.pad(s2, (0, padrange), 'constant', constant_values=(0,0))
    else:
        s1 = np.pad(s1, (0, padrange), 'constant', constant_values=(0,0))
    return s1, s2

def readConfigFile():
    """
    Method to read the yaml configuration file and load it
    """
    with open('./config/device_params.yaml', 'r') as file:
        try:
            return yaml.safe_load(file)
        except Exception as e:
            print(f"Error: {e}")

parser = argparse.ArgumentParser(
                    prog='EEG_Analysis',
                    description='Tool to analyze and compare sent and measured signal using the PyEDF tool'
                    )
parser.add_argument('-i', '--input_signal', type=str, default="common_mode_sample1", help="Sample signal filename. Must be present in the 'edf_samples' directory")
parser.add_argument('-t','--test_signal', action="store_true", help="Use a sinusoidal test signal instead of a real EEG measurement")
parser.add_argument('-s', '--sample_rate', type=int, default=200, help="Set the sample rate at which the signals to be analyzed")
parser.add_argument('-c', '--channels', type=list, default=['Fp1', 'Fp2'], help="List of channels to show in the plot.")
parser.add_argument('-m', '--measured_signal', type=str, default="EEG_CommonSample1", help="Measured signal to be analyzed together with input signal")

args = parser.parse_args()

config = readConfigFile()

if args.test_signal and args.measured_signal == "EEG_CommonSample1":
    args.measured_signal = "Sen1Hz"

input_signal_filepath = os.path.join(".", "edf_samples", f"{args.input_signal}.edf")
output_signal_filepath = os.path.join(".", "edf_samples", "data_analysis", f"{args.measured_signal}.edf")

# Prepare signal workers
if args.test_signal:
    input_signal_worker = TestingSignalsWorker(config)
    input_signal_worker.generateTestingSignal("Sinusoidal", 10, 199, 500, 3)
    input_signal_worker.setSelectedSimTime([0,5])
    input_signal_worker.setSelectedChannels(args.channels)
else:
    input_signal_worker = EDFWorker(config)
    input_signal_worker.readEDF(input_signal_filepath)
    input_signal_worker.setSelectedChannels(args.channels)

output_signal_worker = EDFWorker(config)
output_signal_worker.readEDF(output_signal_filepath)
output_signal_worker.setSelectedChannels(args.channels)

# Keep first channel for EDF files and correct voltage offset
output_signal = output_signal_worker.signal_data_.physical_signals_and_channels[0][1] - EEG_EDF_OFFSET
input_signal = input_signal_worker.signal_data_.physical_signal if args.test_signal else input_signal_worker.signal_data_.physical_signals_and_channels[0][1]

print(f"Input signal original length = {len(input_signal)}")
print(f"Output signal original length = {len(output_signal)}")


# We can try to apply a filter to see if it improves
#input_signal = butter_lowpass_filter(input_signal, 50, input_signal_worker.getSampleRate(), order=5)
#input_signal = butter_highpass_filter(input_signal, 1, input_signal_worker.getSampleRate(), order=5)

input_signal_resampled = resampy.resample(input_signal, input_signal_worker.getSampleRate(), args.sample_rate)
output_signal_resampled = resampy.resample(output_signal, output_signal_worker.getSampleRate(), args.sample_rate)

print(f"Resampled input signal length = {len(input_signal_resampled)}")
print(f"Resampled Output signal length = {len(output_signal_resampled)}")

input_lag = get_correlation_offset(input_signal_resampled, output_signal_resampled)

output_time_axis = np.arange(0, len(output_signal_resampled)) #input_signal_worker.getDuration(), time_step)
input_time_axis = np.arange(0, len(input_signal_resampled))

print(f"Before plotting we have:\nInput time axis length: \t{len(input_time_axis)}\nOutput time axis length: \t{len(output_time_axis)}\nInput signal length: \t{len(input_signal_resampled)}\nOutput signal length: \t{len(output_signal_resampled)}\nInput lag: \t{input_lag}\n")

input_signal_name = args.input_signal if not args.test_signal else 'Test Signal'
plot_title = f"{input_signal_name} Vs {args.measured_signal}"

plot_signal_comparison(input_signal_resampled, output_signal_resampled, plot_title, input_lag+SIGNAL_WINDOW_OFFSET)
