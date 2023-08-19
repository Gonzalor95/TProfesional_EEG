#!/usr/bin/python

import os
import resampy
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

## testing_signal == 

edf_worker = EDFWorker(config)
testing_signals_worker = TestingSignalsWorker(config)
testing_signals_worker.generateTestingSignal(signal_name="Sinusoidal", frecuency=5, amplitude=199, sample_rate=500, duration=5)
testing_signals_worker.setSelectedChannels(['Fp1','Fp2'])
testing_signals_worker.setSelectedSimTime([0,5])
#testing_signals_worker.previewSignal()

original_signal = EDFWorker(config)
original_signal.readEDF("./edf_samples/common_mode_sample1.edf")
edf_worker.setSelectedChannels(['Fp1', 'Fp2'])

edf_worker.readEDF("./edf_samples/data_analysis/0000012.edf")

edf_worker.setSelectedChannels(['Fp1', 'Fp2'])



eeg_signals = edf_worker.getSimulationSignals()
test_signals = testing_signals_worker.getSimulationSignals()

print(f"edf_worker.getChannels() = {edf_worker.getChannels()}")
print(f"edf_worker.getSampleRate() = {edf_worker.getSampleRate()}")
print(f"edf_worker.signal_data_.physical_signals_and_channels = {edf_worker.signal_data_.physical_signals_and_channels}")
print(f"eeg_signals = {eeg_signals}")
#print(len(eeg_signals[0][1]))
print(f"test_signals = {test_signals}")

analyze_test_signal = False
#def OverlapSignals(edf_worker, testing_signals_worker):
if analyze_test_signal:
    time_axis_testing = np.arange(0,25, 1/testing_signals_worker.getSampleRate())
    time_axis_edf = np.arange(0,25, 1/edf_worker.getSampleRate())
    plt.plot(time_axis_edf, edf_worker.signal_data_.physical_signals_and_channels[0][1] - 200 , 'r--', time_axis_testing-0.055, testing_signals_worker.signal_data_.physical_signal)

    plt.show()

# Plot edf signal vs original edf signal
else:

    sr_orig = 50000.0
    sr_new = 20000.0
    original_resampled = resampy.resample(original_signal.signal_data_.physical_signals_and_channels[0][1], sr_orig, sr_new)

    original_signal_time_axis = np.arange(0, original_signal.getDuration(), 1/original_signal.getSampleRate())
    original_resampled_time_axis = np.arange(0, original_signal.getDuration(), 1/201)
    edf_signal_time_axis = np.arange(0, edf_worker.getDuration(), 1/edf_worker.getSampleRate())
    
    #plt.plot(edf_worker.signal_data_.physical_signals_and_channels[0][1])
    #plt.show()
    #plt.plot(edf_signal_time_axis, (edf_worker.signal_data_.physical_signals_and_channels[0][1]) - 186, 'r.', original_signal_time_axis + 12, original_signal.signal_data_.physical_signals_and_channels[0][1],'g.')

    #plt.show()



    y = edf_worker.signal_data_.physical_signals_and_channels[0][1]
    y = y[2680:6000]
    
    x = original_resampled#[0:(len(y) * 3)]
    

    print(len(x))
    print(len(y))
    print((len(x) - len(y)))

    y = np.append(y-186, np.zeros(len(x) - len(y)))
    y = y* (-1)
    Cmatrix = np.correlate(x,y,'same')
    
    Cmatrix = Cmatrix/max(Cmatrix)

    index = np.where(Cmatrix==1)[0][0]
    print(index)

    t_x = np.arange(0,len(x))
    t_y = np.arange(0,len(y))
    plt.plot(t_x, x,'r--',t_y+index, y, 'b')
    plt.grid(True)
    plt.show()