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


## CONSTS:

# This value came up magically, right?
EEG_EDF_OFFSET = 187.538 # uV

# Parameters to correlate from a chunk of the received signal
SIGNAL_WINDOW_OFFSET = 12000
SIGNAL_WINDOW_SIZE = 4000

def readConfigFile(root_dir):
    """
    Method to read the yaml configuration file and load it
    """
    config_path = os.path.join( root_dir, "..", "config", "device_params.yaml")
    with open(config_path, 'r') as file:
        try:
            return yaml.safe_load(file)
        except Exception as e:
            print(f"Error: {e}")


curr_script_dir = os.path.dirname(os.path.realpath(__file__))
config = readConfigFile(curr_script_dir)

##### FILTERS:



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

def SMA_filter(data, window_size):
    moving_averages = []
    i=0
    # Loop through the array t o
    #consider every window of size 3
    while i < len(data) - window_size + 1:
    
        # Calculate the average of current window
        window_average = round(np.sum(data[i:i+window_size]) / window_size, 2)
        
        # Store the average of current
        # window in moving average list
        moving_averages.append(window_average)
        
        # Shift window to right by one position
        i += 1

    return moving_averages



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
    Returns the offset that places the chunk of measured signal where it correlates the most with the input one 
    """
    Cmatrix = np.correlate(output_signal, input_signal, 'full')
    Cmatrix = Cmatrix/max(Cmatrix)
    index = np.where(Cmatrix ==1)[0][0]

    lag = index - len(output_signal)

    print(f"Correlation lag is = {lag}")

    return lag
    
def pad_shortest_signal(s1, s2, padrange):
    if len(s1) > len(s2):
        s2 = np.pad(s2, (0, padrange), 'constant', constant_values=(0,0))
    else:
        s1 = np.pad(s1, (0, padrange), 'constant', constant_values=(0,0))
    return s1, s2

def getTestingSignal(sig_type="Sinusoidal", frecuency=5, amplitude=200, sample_rate=500, duration=5, resample = None, **filters):
    """
        Gives you the testing signal from the EDF worker. If need to resample using "resampy", use "resample"

        sig_type = ["Square", "Sinusoidal", "Triangular"]
        frecuency: Hz
        amplitude: uV
        sample_rate: sample/sec
        duration: sec
        resample: Hz

    """
    test_signal_worker = TestingSignalsWorker(config)
    test_signal_worker.generateTestingSignal(sig_type, frecuency, amplitude, sample_rate, duration)
    test_signal_worker.setSelectedSimTime([0,duration])

    signal = test_signal_worker.signal_data_.physical_signal

    if resample:
        print(f"Resample testing signal from {sample_rate} to {resample}")
        signal = resampy.resample(signal, test_signal_worker.getSampleRate(), resample)

    return signal

def getOutputSignal(edf_file_name="TestEachBatchChannels"):

    output_signal_filepath = os.path.join(curr_script_dir, "edf_samples", "data_analysis", f"{args.measured_signal}.edf")

    eeg_measure_worker = EDFWorker(config)
    eeg_measure_worker.readEDF("./edf_samples/data_analysis/TestEachBatchChannels.edf")
    eeg_measure_worker.setSelectedChannels(['Fp1', 'Fp2'])




##########################=====================================
def generate_input_signal(input_signal: str, is_testing: bool, channels: list, t_signal_type= "Sinusoidal", t_freq=1, t_amp=199, t_sr=500, t_dur=5):
    curr_script_dir = os.path.dirname(os.path.realpath(__file__))
    config = readConfigFile(curr_script_dir)
    # Prepare signal workers
    if is_testing:
        # We generate a test sinusoidal signal of 10 Hz frequency, 199 uV amplitude, 500 Hz sample rate and 5 second duration
        input_signal_worker = TestingSignalsWorker(config)
        input_signal_worker.generateTestingSignal(t_signal_type, t_freq, t_amp, t_sr, t_dur)
        input_signal_worker.setSelectedSimTime([0, t_dur])
        input_signal_worker.setSelectedChannels(channels)
    else:
        input_signal_filepath = os.path.join(curr_script_dir, "edf_samples", f"{input_signal}.edf")
        input_signal_worker = EDFWorker(config)
        input_signal_worker.readEDF(input_signal_filepath)
        input_signal_worker.setSelectedChannels(channels)
    return  input_signal_worker.signal_data_.physical_signal if is_testing else input_signal_worker.signal_data_.physical_signals_and_channels[0][1]

def generate_output_signal(signal_filepath, channels):
    curr_script_dir = os.path.dirname(os.path.realpath(__file__))
    config = readConfigFile(curr_script_dir)

    output_signal_filepath = os.path.join(curr_script_dir,"..", "edf_samples", "data_analysis", f"{signal_filepath}.edf")

    output_signal_worker = EDFWorker(config)
    output_signal_worker.readEDF(output_signal_filepath)
    output_signal_worker.setSelectedChannels(channels)
    return output_signal_worker.signal_data_.physical_signals_and_channels[0][1] - EEG_EDF_OFFSET