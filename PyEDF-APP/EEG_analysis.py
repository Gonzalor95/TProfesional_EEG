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

EEG_EDF_OFFSET = 187.538 # uV



test_signal_worker = TestingSignalsWorker(config)
test_signal_worker.generateTestingSignal("Sinusoidal", 5, 132, 500, 5)
test_signal_worker.setSelectedSimTime([0,5])
test_signal_worker.setSelectedChannels(['Fp1','Fp2'])


original_signal_worker = EDFWorker(config)
original_signal_worker.readEDF("./edf_samples/common_mode_sample1.edf")
original_signal_worker.setSelectedChannels(['Fp1', 'Fp2'])

eeg_measure_worker = EDFWorker(config)
eeg_measure_worker.readEDF("./edf_samples/data_analysis/TestEachBatchChannels.edf")
eeg_measure_worker.setSelectedChannels(['Fp1', 'Fp2'])

analyze_test_signal = True

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

    sr_orig = 50000.0
    sr_new = 20000.0
    original_resampled = resampy.resample(original_signal_worker.signal_data_.physical_signals_and_channels[0][1], sr_orig, sr_new)

    original_signal_worker_time_axis = np.arange(0, original_signal_worker.getDuration(), 1/original_signal_worker.getSampleRate())
    original_resampled_time_axis = np.arange(0, original_signal_worker.getDuration(), 1/201)
    edf_signal_time_axis = np.arange(0, eeg_measure_worker.getDuration(), 1/eeg_measure_worker.getSampleRate())
    
    #plt.plot(eeg_measure_worker.signal_data_.physical_signals_and_channels[0][1])
    #plt.show()
    #plt.plot(edf_signal_time_axis, (eeg_measure_worker.signal_data_.physical_signals_and_channels[0][1]) - 186, 'r.', original_signal_worker_time_axis + 12, original_signal_worker.signal_data_.physical_signals_and_channels[0][1],'g.')

    #plt.show()



    y = eeg_measure_worker.signal_data_.physical_signals_and_channels[0][1]
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