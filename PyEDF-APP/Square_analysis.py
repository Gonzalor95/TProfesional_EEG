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

def readConfigFile():
    """
    Method to read the yaml configuration file and load it
    """
    with open('./config/device_params.yaml', 'r') as file:
        try:
            return yaml.safe_load(file)
        except Exception as e:
            print(f"Error: {e}")
def get_testing_signal(signal_type = 'Sinusoidal', frecuency = 5, amplitude = 200, sample_rate = 500, duration = 5):
    """ 
    Returns configured testing signal
    """
    edf_worker = TestingSignalsWorker(readConfigFile())
    edf_worker.generateTestingSignal(signal_name=signal_type, frecuency=frecuency, amplitude=amplitude, sample_rate=sample_rate, duration=duration)
    edf_worker.setSelectedSimTime([0,duration])

    signal = edf_worker.signal_data_.physical_signal

    return signal, edf_worker

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


channel = ['Fp1']
full_signal = eeg_utils.generate_output_signal("TestFilterSquare10Hz", channel)
testing_1Hz, testing_edf_10Hz = get_testing_signal(signal_type = 'Square', frecuency = 1, amplitude = 200, sample_rate = 200, duration = 2.5)
testing_10Hz, testing_edf_10Hz = get_testing_signal(signal_type = 'Square', frecuency = 10, amplitude = 200, sample_rate = 200, duration = 2.5)
testing_50Hz, testing_edf_10Hz = get_testing_signal(signal_type = 'Square', frecuency = 50, amplitude = 200, sample_rate = 200, duration = 2.5)


square_10Hz = full_signal[4886:6038]
square_50Hz = full_signal[20009:21240]
square_1Hz = full_signal[39035:41247]

#print(eeg_utils.get_correlation_offset(square_10Hz, square_50Hz))
#print(eeg_utils.get_correlation_offset(square_1Hz, square_50Hz))
print(eeg_utils.get_correlation_offset(square_10Hz, testing_10Hz ))

square_10Hz = square_10Hz[132:600]
square_50Hz = square_50Hz[132:600]
square_1Hz = square_1Hz[132:600]




time_step=1/200
time_axis  = np.arange(start = 0, stop = len(square_1Hz) * time_step, step = time_step)
time_axis_testing = np.arange(start = 0, stop = len(testing_10Hz) * time_step , step = time_step)

figure, axis = plt.subplots(2, 1)
figure.suptitle(f"Analisis de pulso")
##
######################### 1Hz
axis[0].set_title("Frecuencia = 1Hz")
axis[0].plot(time_axis, square_1Hz, 'r', label='Output')
axis[0].plot(time_axis_testing, testing_1Hz, 'b--', label='Input')
axis[0].set_ylabel("Tensión [uV]")
axis[0].grid()
axis[0].legend()
axis[0].set_xlim([0, time_axis[-1]])

######################### 10Hz
axis[1].set_title("Frecuencia = 10Hz")
axis[1].plot(time_axis, square_10Hz, 'r', label='Output')
axis[1].plot(time_axis_testing, testing_10Hz, 'b--', label='Input')
axis[1].set_ylabel("Tensión [uV]")
axis[1].grid()
axis[1].legend()
axis[1].set_xlim([0, time_axis[-1]])

######################### 50Hz
#axis[2].set_title("Frecuencia = 50Hz")
#axis[2].plot(time_axis, square_50Hz, 'r', label='Output')
#axis[2].plot(time_axis_testing, testing_50Hz, 'b--', label='Input')
#axis[2].set_ylabel("Tensión [uV]")
#axis[2].grid()
#axis[2].legend()
#axis[2].set_xlim([0, time_axis[-1]])

##
axis[1].set_xlabel("Tiempo [seg]")

plt.show()



testing_1Hz = butterworth_filter(data=testing_1Hz,btype = 'low', cutoff_freq = 30, fs = 200, order = 1)
testing_1Hz = butterworth_filter(data=testing_1Hz,btype = 'high', cutoff_freq = 0.8, fs = 200, order = 7)

plt.title("Detalle para Frecuencia = 1Hz. Aplicando el filtro pasabanda al input")
plt.plot(time_axis, square_1Hz, 'r', label='Output')
plt.plot(time_axis_testing, testing_1Hz, 'b--', label='Input (filtrada)')
plt.ylabel("Tensión [uV]")
plt.xlabel("Tiempo [seg]")
plt.xlim([0, time_axis[-1]])
plt.grid()
plt.legend()
plt.show()