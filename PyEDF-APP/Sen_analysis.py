#!/usr/bin/python

import os
import resampy
import math
import numpy as np
from scipy.signal import butter, lfilter, spectrogram, periodogram, filtfilt, argrelextrema
from scipy.fft import fft, fftfreq
from scipy import stats
import yaml
from modules.EDFWorker import EDFWorker
import matplotlib.pyplot as plt
from modules.TestingSignals import TestingSignalsWorker



#print("freq is" + str(scipy.fftpack.fftfreq(sampled_data, dt )  ))
#As far as I know, THD=sqrt(sum of square magnitude of
#harmonics+noise)/Fundamental value (Is it correct?)So I'm
#just summing up square of all frequency data obtained from FFT,
#sqrt() them and dividing them with fundamental frequency value.

def thd(signal):
    abs_data = np.abs(fft(signal))
    sq_sum=0.0
    for r in range( len(abs_data)):
       sq_sum = sq_sum + (abs_data[r])**2

    sq_harmonics = sq_sum -(max(abs_data))**2.0
    thd = 100*sq_harmonics**0.5 / max(abs_data)

    return thd

    #print("Total Harmonic Distortion(in percent):")
    #print(thd(abs_yf[1:int(len(abs_yf)/2) ]))


# This value is the supposed offset consequence of the Data conversion to .EDF file
EEG_EDF_OFFSET = 187.538 # uV

# Parameters to correlate from a chunk of the received signal
SIGNAL_WINDOW_OFFSET = 12000
SIGNAL_WINDOW_SIZE = 4000

"""

======FILTERS======

"""
def butterworth_filter(data= [], btype='low', cutoff_freq = 1, fs = 1, order = 1):
    """ 
        Returns data filtered by butterworth filter

        data = one dimensional array
        btype = filter type {'low', 'high'}
        cutoff_freq: [Hz]
        fs = sample frequency
        order: [int]
    """
    # Get polynomials for IIR filter
    b, a = butter(order, cutoff_freq, fs = fs, btype = btype, analog = False)

    # Apply linear filter:
    y = lfilter(b, a, data)
    return y

def slew_rate_filter(data, slew_rate=10):
    """
    Filters so the difference between y_i - y_{i-1} does not exceed certain threshold
    slew rate: uV
    """

    index = np.arange(1,len(data)-1)

    for i in index:
        m = data[i]-data[i-1]

        if abs(m) < slew_rate:
            data[i] = data[i]
        else:
            data[i] = data[i-1] + slew_rate * m / abs(m)

        i = i + 1
    
    return data


def SMA_filter(data, window_size):
    """
    Apply Simple Moving Avarage on data
    """
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

    return np.array(moving_averages)

def get_optimized_window_size_for_SMA(input, output):

    window_sizes = list(range(10, 50))

    mse = 9999999
    for w_s in window_sizes:

        input_filt = SMA_filter(input, w_s)
        output_filt = SMA_filter(output, w_s)

        current_mse = get_mse(input_signal=input_filt,output_signal=output_filt)

        window_size = w_s 

        if current_mse < mse:
            mse = current_mse
            window_size = w_s

    return window_size

def normalize_min_max(y):
    """Scales the whole signal between y = [0:1]"""
    return (y-min(y))/(max(y)-min(y)); 

"""

======UTILITY FUNCTIONS======

"""
def readConfigFile():
    """
    Method to read the yaml configuration file and load it
    """
    with open('./config/device_params.yaml', 'r') as file:
        try:
            return yaml.safe_load(file)
        except Exception as e:
            print(f"Error: {e}")


def get_signal_and_edf_worker_from_edf(signal_filepath, channel, is_output = False):
    """ 
    If is_output = True, will get rid of signal offset
    """
    edf_worker = EDFWorker(readConfigFile())
    edf_worker.readEDF(signal_filepath)
    edf_worker.setSelectedChannels([channel])

    signal = None
    for tuple in edf_worker.signal_data_.physical_signals_and_channels:
        if (tuple[0] is channel):
            signal = tuple[1]

    if is_output:
        signal = (signal - EEG_EDF_OFFSET)

    return signal, edf_worker

def get_testing_signal(signal_type = 'Sinusoidal', frecuency = 5, amplitude = 200, sample_rate = 500, duration = 5):
    """ 
    Returns configured testing signal
    """
    edf_worker = TestingSignalsWorker(readConfigFile())
    edf_worker.generateTestingSignal(signal_name=signal_type, frecuency=frecuency, amplitude=amplitude, sample_rate=sample_rate, duration=duration)
    edf_worker.setSelectedSimTime([0,duration])

    signal = edf_worker.signal_data_.physical_signal

    return signal, edf_worker


def select_data_window(data, start_index= 13000, end_index= 15000):
    data = data[start_index:end_index]
    return data

def select_best_data_window(input_signal, output_signal, window_size = 5):
    """
        Elige la ventana que menor le da error. Se supone que ambas señales ya estan ressampleadas a 200Hz
        Window_size en segundos
    """

    sample_rate = 200
    time_step = 1/sample_rate
    # start = window_size para evitar los bordes
    # Recorremos toda la input:
    window_starts = np.arange(start = window_size, stop = len(input_signal) * time_step - window_size, step = window_size)

    print(window_starts)
    mse = 9999999
    for window_start in window_starts:
        start_index = int(window_start) * sample_rate
        end_index= (int(window_start) + window_size) * 200

        selected_input_signal = select_data_window(input_signal, start_index= start_index, end_index= end_index)
        selected_output_signal, discard = get_correlated_input_signal(input_signal=output_signal, output_signal=selected_input_signal)

        current_mse = get_mse(input_signal=selected_input_signal,output_signal=selected_output_signal)

        if True:#current_mse < mse:
            mse = current_mse
            print(f"mse = {mse} = [{window_start} - {window_start + window_size} ] seg")
            best_window_start = window_start

    print(f"#####################best window start = {best_window_start} with mse = {mse}")
    return best_window_start

def get_correlated_input_signal(input_signal, output_signal):
    """

    We suppose input > output
    """

    #print("Started get_correlated_input_signal()...")
    
    # Find the correlation lag:

    Cmatrix = np.correlate(output_signal, input_signal, 'full')
    Cmatrix = Cmatrix/max(Cmatrix)

    index = np.where(Cmatrix ==1)[0][0]  # usando el +1, bajo de mse=19 a 16

    # Como a veces si hago index +- algun valor, busco el que da menor MSE:

    aux = list(range(-10, 10))

    input_signal_duration = len(input_signal) / 200
    output_signal_duration = len(output_signal) / 200
    #print(f"Input signal duration = {input_signal_duration}")
    #print(f"Output signal duration = {output_signal_duration}")
    #print(f"Correlation returned index = {index}")
    
    mse = 9999999999999
    for i in aux:
        #print(f"i = {i}")
        lag_index = (index + i)
        input_lag = (lag_index  - len(input_signal))

        # We keep the correlated window part
        aux_signal = input_signal[abs(input_lag):len(output_signal)+abs(input_lag)]

        current_mse = get_mse(input_signal=aux_signal,output_signal=output_signal)

        #print(f"mse = {current_mse} with input_lag = {input_lag}")

        if current_mse < mse:
            mse = current_mse
            best_input_lag = input_lag
            correlated_input_signal = aux_signal
            saved_i = i

    window_start_time = len(input_signal[0:abs(input_lag)])/200
    window = [window_start_time, window_start_time+ output_signal_duration]
    #print(f"Selected window of input: [{window[0]} - {window[1]}] seg")
    #print(f"Latest mse = {mse} with saved_i = {saved_i}. ")
    return correlated_input_signal, window

def get_mse(input_signal, output_signal):
    """
    We suppose lengths are equal.
    """
    return (np.square(input_signal - output_signal)).mean(axis=None)

def check_gain_for_output(input_signal, output_signal):
    """
    Get gain that reduces mse
    """

    gains = np.arange(start = 0.5, stop = 1.5, step = 0.0001)
    
    mse = get_mse(input_signal, output_signal)
    for gain in gains:
        aux = output_signal * gain

        current_mse = get_mse(input_signal, aux)

        if current_mse < mse:
            #print(f"best gain = {gain} with mse = {current_mse}")
            best_gain = gain
            mse = current_mse

    return best_gain



"""
=================================================================================
====================================  ANALYSIS FUNCTIONS   ====================================
=================================================================================
"""


"""
GENERAL ANALYSIS: Aca hago un analisis general
"""
#input_signal_file_name = "common_mode_sample1"
#output_signal_file_name = "EEG_CommonSample1"
output_signal_file_name = "Sen200uV"
#input_signal_filepath = os.path.join(".", "edf_samples", f"{input_signal_file_name}.edf")
output_signal_filepath = os.path.join(".", "edf_samples", "data_analysis", f"{output_signal_file_name}.edf")
channel = 'Fp1'
input_signal, input_edfworker = get_testing_signal(signal_type = 'Sinusoidal', frecuency = 5, amplitude = 200, sample_rate = 500, duration = 5*10)
#input_signal, input_edfworker = get_signal_and_edf_worker_from_edf(signal_filepath=input_signal_filepath, channel=channel, is_output=False)
output_signal, output_edfworker  = get_signal_and_edf_worker_from_edf(signal_filepath=output_signal_filepath, channel=channel, is_output=True)
#output_signal = output_signal[11000:22000]
output_signal = output_signal * 1.02 
##

## PREVIEW SIGNALS BEFORE WORKING:
#time_step_output = 1/output_edfworker.getSampleRate()
#time_step_input = 1/input_edfworker.getSampleRate()
#t_output = np.arange(start = 0, stop = len(output_signal) * time_step_output, step = time_step_output)
#t_input = np.arange(start = 0, stop = len(input_signal) * time_step_input, step = time_step_input)
#figure, axis = plt.subplots(2, 1)
#axis[0].plot(t_input,input_signal, 'r', label="Input") 
#axis[0].set_title(f"Señal de Input completa - Canal Fp1")
#axis[0].set_xlim([0, t_input[-1]])
#axis[0].set_xlabel("Tiempo [seg]")
#axis[0].set_ylabel("Tensión [uV]")
#axis[0].legend()
#axis[0].grid()
#axis[1].plot(t_output,output_signal, 'b', label="Output") 
#axis[1].set_title(f"Señal de Output completa - Canal Fp1")
#axis[1].set_xlim([0, t_output[-1]])
#axis[1].set_xlabel("Tiempo [seg]")
#axis[1].set_ylabel("Tensión [uV]")
#axis[1].legend()
#axis[1].grid()
#plt.show()
#############
############# FILTERS
input_signal_original = input_signal
#input_signal = butterworth_filter(data=input_signal,btype = 'low', cutoff_freq = 30, fs = input_edfworker.getSampleRate(), order = 1)
#input_signal = butterworth_filter(data=input_signal,btype = 'high', cutoff_freq = 0.8, fs = input_edfworker.getSampleRate(), order = 1)
#input_signal = slew_rate_filter(input_signal, 10)
#############
############# Resampling
new_sample_rate = 200
input_signal_original_resampled = resampy.resample(input_signal_original, input_edfworker.getSampleRate(), new_sample_rate)
input_signal_resampled = resampy.resample(input_signal, input_edfworker.getSampleRate(), new_sample_rate)
output_signal_resampled = output_signal#resampy.resample(output_signal, output_edfworker.getSampleRate(), new_sample_rate)
####
#### BEST WINDOW:
select_best_data_window(input_signal=input_signal_resampled,output_signal=output_signal_resampled,window_size=5)
#############
############# Correlation
################################################
############## NOTA IMPORTANTE: Tuve que dar vuelta la input y output aca porque asi obtenia la ventana que estabamos seleccionando con referencia a input
#######################
# We select a window from the output signal to avoid parts that do not correspond to anything
sample_window_duration = 1 # seg
# Muestra A
#selected_start_window = 15 # seg
# Muestra B
#selected_start_window = 60 # seg
# Muestra C
selected_start_window = 3 # seg
window = [selected_start_window, selected_start_window + sample_window_duration]
start_index = selected_start_window * 200
end_index= (selected_start_window + sample_window_duration) * 200

input_signal_resampled = select_data_window(input_signal_resampled, start_index= start_index, end_index= end_index)
input_signal_original_resampled = select_data_window(input_signal_original_resampled, start_index= start_index, end_index= end_index)

#############
############# Scaling:
## Tiene que ser despues de select_data_window() porque sino agarra los picos raros que se toman en los extremos
#input_signal_resampled = normalize_min_max(input_signal_resampled)
#output_signal_resampled = normalize_min_max(output_signal_resampled)



output_signal_resampled, discard = get_correlated_input_signal(input_signal=output_signal_resampled, output_signal=input_signal_resampled)
#############
############# Calculations over signals:
#gain = check_gain_for_output(input_signal=input_signal_resampled, output_signal=output_signal_resampled)
#output_signal_resampled = output_signal_resampled * gain
mse = get_mse(input_signal=input_signal_resampled, output_signal=output_signal_resampled)
print(f"mse = {mse}")
#print(f"gain = {mse}")
# Just curiosity:
# rest = stats.ttest_ind(input_signal_resampled, output_signal_resampled)
#print(rest)

error_signal = input_signal_resampled - output_signal_resampled
#############
############# Plotting
### Time Axis:
plot_time_axis = True
time_step = 1/new_sample_rate if plot_time_axis else 1
xlabel = 'Time [seg]' if plot_time_axis else ''
#time_axis_in  = np.arange(start = 0, stop = len(input_signal_resampled) * time_step, step = time_step)
#time_axis_out = np.arange(start = 0, stop = len(input_signal_resampled) * time_step, step = time_step)
### Plot:
time_axis = np.arange(start = 0, stop = len(input_signal_resampled) * time_step, step = time_step)

plt.plot(time_axis,input_signal_resampled, 'r', label="Input") 
plt.plot(time_axis, output_signal_resampled, 'b--', label="Output")
plt.plot(time_axis, error_signal,'g', label="Error = Input - Output")
plt.xlim([0, time_axis[-1]])
plt.ylim([-200, 200])
plt.ylabel("Tensión [uV]")
plt.xlabel("Tiempo [seg]")
plt.legend(loc='upper right')
plt.grid()

print(f"max Error = {max(error_signal)}")
print(f"min Error = {min(error_signal)}")
print(f"Error absoluto = {max([abs(max(error_signal)), abs(min(error_signal)) ]):.2f} uV")


plt.show()



print(thd(output_signal_resampled[1:int(len(output_signal_resampled)/2) ]))

s = output_signal_resampled
Fs = 200
t = time_axis

fig = plt.figure(figsize=(7, 7), layout='constrained')
axs = fig.subplot_mosaic([["signal", "signal"],
                          ["magnitude", "log_magnitude"],
                          ["phase", "angle"]])

# plot time signal:
axs["signal"].set_title("Signal")
axs["signal"].plot(t, s, color='C0')
axs["signal"].set_xlabel("Time (s)")
axs["signal"].set_ylabel("Amplitude")

# plot different spectrum types:
axs["magnitude"].set_title("Magnitude Spectrum")
axs["magnitude"].magnitude_spectrum(s, Fs=Fs, color='C1')

axs["log_magnitude"].set_title("Log. Magnitude Spectrum")
axs["log_magnitude"].magnitude_spectrum(s, Fs=Fs, scale='dB', color='C1')

axs["phase"].set_title("Phase Spectrum ")
axs["phase"].phase_spectrum(s, Fs=Fs, color='C2')

axs["angle"].set_title("Angle Spectrum")
axs["angle"].angle_spectrum(s, Fs=Fs, color='C2')

plt.show()
