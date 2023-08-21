#!/usr/bin/python

import os
import resampy
from scipy.signal import butter, lfilter, freqz
import numpy as np
import yaml
from modules.EDFWorker import EDFWorker
import matplotlib.pyplot as plt
from modules.TestingSignals import TestingSignalsWorker

"""Analisis de las señales.
Pasar lo leido por el EEG a formato EDF:
    1. Copian el archivo .eeg
    2. abren el EDFBrowser y en el panel superior elegir "Tools > Convert Binary/raw data to EDF"
    3. La configuracion tiene que ser:
        Samplefrequency = 200Hz
        Number of signals = 32 (dependera como se configuro el EEG ese dia)
        Sample size (16 bits (2 bytes))
        Offset = 0 (dejarlo asi, porque arruina la señal. Igual el cero pareciera estar en 187,538uV)
        Encoding 2's complement
        Endianness: little endian
        Data blocksize = 0
        Skip bytes = 1
        Physical maximun 3000uV
        Physical dimension uV
        sample type I16
    4. Para corregir el nombre de los canales, abrir el EDFBrowser y poner "Tools > Header editor repair" y cambiar los nombres
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


config = readConfigFile()


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



EEG_EDF_OFFSET = 187.538 # uV



test_signal_worker = TestingSignalsWorker(config)
test_signal_worker.generateTestingSignal("Sinusoidal", 5, 132, 500, 5)
test_signal_worker.setSelectedSimTime([0,5])
test_signal_worker.setSelectedChannels(['Fp1','Fp2'])


original_signal_worker = EDFWorker(config)
original_signal_worker.readEDF("./edf_samples/common_mode_sample1.edf")
original_signal_worker.setSelectedChannels(['Fp1', 'Fp2'])

eeg_measure_worker = EDFWorker(config)
eeg_measure_worker.readEDF("./edf_samples/data_analysis/EEG_CommonSample1.edf")
eeg_measure_worker.setSelectedChannels(['Fp1', 'Fp2'])

analyze_test_signal = False

if analyze_test_signal:

    eeg_signal = eeg_measure_worker.signal_data_.physical_signals_and_channels[0][1] - EEG_EDF_OFFSET
    test_signal = test_signal_worker.signal_data_.physical_signal

    sr_new = 200 * 100 # for some reason, need to multiply by '100'

    print(f"len eeg_signal = {len(eeg_signal)}")
    print(f"len test_signal = {len(test_signal)}")

    eeg_signal_resampled = resampy.resample(eeg_signal, eeg_measure_worker.getSampleRate() * 100, sr_new)
    test_signal_resampled = resampy.resample(test_signal, test_signal_worker.getSampleRate() * 100, sr_new)

    print(f"len eeg_signal_resampled = {len(eeg_signal_resampled)}")
    print(f"len test_signal_resampled = {len(test_signal_resampled)}")

    ## If not same size, we pad the shortest with zeros:

    padrange = int((len(eeg_signal_resampled) - len(test_signal_resampled))/2)

    #test_signal_resampled = np.pad(test_signal_resampled, (padrange,padrange),'constant', constant_values=(0,0))

    print(f"len eeg_signal_resampled = {len(eeg_signal_resampled)}")
    print(f"len test_signal_resampled padded = {len(test_signal_resampled)}")

    time_step = 1/(sr_new/100) # need to get rid of the 100
    time_axis = np.arange(0,eeg_measure_worker.getDuration(), time_step)

    Cmatrix = np.correlate(eeg_signal_resampled,test_signal_resampled,'full')
    Cmatrix = Cmatrix/max(Cmatrix)
    index = np.where(Cmatrix ==1)[0][0]

    Cmatrix[index] = max(test_signal_resampled)

    lag = (index - len(test_signal_resampled)) * time_step
    print(lag)

    test_signal_resampled = np.pad(test_signal_resampled, (0,padrange*2),'constant', constant_values=(0,0))

    plt.plot(time_axis+lag, test_signal_resampled, 'r', label="test_signal") 
    plt.plot(time_axis,eeg_signal_resampled, 'b--',label="eeg_measurement")
    plt.grid(True)
    plt.legend()
    plt.show()

# Plot edf signal vs original edf signal
else:

    eeg_signal = eeg_measure_worker.signal_data_.physical_signals_and_channels[0][1] - EEG_EDF_OFFSET
    original_signal = original_signal_worker.signal_data_.physical_signals_and_channels[0][1]

    sr_new = 200 * 100 # for some reason, need to multiply by '100'

    eeg_signal_resampled = resampy.resample(eeg_signal, eeg_measure_worker.getSampleRate() * 100, sr_new)
    original_signal_resampled = resampy.resample(original_signal, original_signal_worker.getSampleRate() * 100, sr_new)

    #original_signal_resampled = butter_lowpass_filter(original_signal_resampled, 50, 200, order=5)
    original_signal_resampled = butter_highpass_filter(original_signal_resampled, 1, 200, order=5)
    

    bck_up_eeg_signal_resampled = eeg_signal_resampled
    eeg_signal_resampled = eeg_signal_resampled#[17000:20000]

    padrange = int(abs(len(eeg_signal_resampled) - len(original_signal_resampled)))

    Cmatrix = np.correlate(eeg_signal_resampled,original_signal_resampled,'full')
    Cmatrix = Cmatrix/max(Cmatrix)
    index = np.where(Cmatrix ==1)[0][0]

    Cmatrix[index] = max(original_signal_resampled)

    time_step = 1/(sr_new/100)
    time_axis_or = np.arange(0,original_signal_worker.getDuration(), time_step)
    time_axis_eeg = np.arange(0,time_step*len(eeg_signal_resampled), time_step)
    lag = (index - len(eeg_signal_resampled)) * time_step
    print(lag)

    #eeg_signal_resampled = np.pad(eeg_signal_resampled, (0,padrange),'constant', constant_values=(0,0))


    print(f"len(original_signal_resampled) = {len(original_signal_resampled)}")
    print(f"len(time_axis) = {len(time_axis_eeg)}")
    plt.plot(time_axis_or+abs(lag)+10-1.0613, original_signal_resampled, 'r', label="test_signal") 
    plt.plot(time_axis_eeg,eeg_signal_resampled, 'b--',label="eeg_measurement")
    plt.grid(True)
    plt.legend()
    plt.show()