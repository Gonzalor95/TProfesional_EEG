#!/usr/bin/python

import os
import resampy
import math
import numpy as np
from scipy.signal import butter, lfilter
from scipy import stats
import yaml
from modules.EDFWorker import EDFWorker
import matplotlib.pyplot as plt
from modules.TestingSignals import TestingSignalsWorker

"""
--------Conversion a formato EDF:

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

--------Receta de como deberiamos analizar cada batch de datos:

    **Input = Esta señal siempre va a ser la que enviamos al EEG
    **Output = Esta señal es la que mide el EEG.


    1. Obtener la "Input" signal:
        a. Si es una señal de testing (senoidal, cuadrada, triangular), la tenemos que fabricar con el EDF worker de "TestingSignals.py"
        b. Si es una señal de EDF, tenemos que usar el EDFWorker y sacar la señal que queramos.

    2. Obtener la "Output" signal: 
        a. Se deberia obtener de PYEDF-APP/edf_samples/data_analysis/<file_name>.edf
        b. El canal seleccionado a analizar, se le tiene que aplicar el offset de 187,538uV.

    3. Aplicar el filtrado digital que queramos con el sample_rate original. Vimos que si reesampleamos y aplicamos el filtro despues del resampleo, empeora el error.

    4. Resamplear. Normalmente lo hacemos a 200Hz ya que es el sample_rate del EEG.

    5. De la "Output" lo mas seguro es que tengamos que plotear una vez y determinar una seccion donde analizar los datos, porque siempre pasa que en los bordes
    hay problemas. Determinamos los indices de dicha seccion y quedarnos con esa ventana:
        output = output[index:index+window_size]

    6. Usando la correlación cruzada, buscar esa ventana de "Output" en la "Input".
"""


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

    return moving_averages

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
        signal = signal - EEG_EDF_OFFSET

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
    start_index = 13000
    end_index = 15000
    window_size = end_index - start_index
    data = data[start_index:end_index]
    return data

def get_correlated_input_signal(input_signal, output_signal):
    """
    We suppose input > output
    """

    print("Started get_correlated_input_signal()...")
    # Find the correlation lag:
    Cmatrix = np.correlate(output_signal, input_signal, 'full')
    Cmatrix = Cmatrix/max(Cmatrix)

    index = np.where(Cmatrix ==1)[0][0]  # usando el +1, bajo de mse=19 a 16

    # Como a veces si hago index +- algun valor, busco el que da menor MSE:

    aux = list(range(-10, 10))

    print("Correlation returned index = {index}")
    
    mse = 9999999999999
    for i in aux:
        lag_index = (index + i)
        input_lag = (lag_index  - len(input_signal))

        # We keep the correlated window part
        aux_signal = input_signal[abs(input_lag):len(output_signal)+abs(input_lag)]

        current_mse = get_mse(input_signal=aux_signal,output_signal=output_signal)

        #print(f"mse = {current_mse} with input_lag = {input_lag}")

        if current_mse < mse:
            mse = current_mse
            correlated_input_signal = aux_signal
            saved_i = i

    print(f"Latest mse = {mse} with saved_i = {saved_i}")
    return correlated_input_signal

def get_mse(input_signal, output_signal):
    """
    We suppose lengths are equal.
    """
    return (np.square(input_signal - output_signal)).mean(axis=None)

"""
=================================================================================
====================================  MAIN   ====================================
=================================================================================
"""

input_signal_file_name = "common_mode_sample1"
output_signal_file_name = "EEG_CommonSample1"

input_signal_filepath = os.path.join(".", "edf_samples", f"{input_signal_file_name}.edf")
output_signal_filepath = os.path.join(".", "edf_samples", "data_analysis", f"{output_signal_file_name}.edf")

input_signal, input_edfworker = get_signal_and_edf_worker_from_edf(signal_filepath=input_signal_filepath, channel='Fp1', is_output=False)
output_signal, output_edfworker  = get_signal_and_edf_worker_from_edf(signal_filepath=output_signal_filepath, channel='Fp1', is_output=True)

##
## PREVIEW SIGNALS BEFORE WORKING:
plt.plot(input_signal)
plt.plot(output_signal)
plt.show()

#############
############# FILTERS
input_signal = butterworth_filter(data=input_signal,btype = 'low', cutoff_freq = 30, fs = input_edfworker.getSampleRate(), order = 1)
input_signal = butterworth_filter(data=input_signal,btype = 'high', cutoff_freq = 0.8, fs = input_edfworker.getSampleRate(), order = 1)

#input_signal = slew_rate_filter(input_signal, 10)

#############
############# Scaling

#input_signal = normalize_min_max(input_signal)
#output_signal = normalize_min_max(output_signal)

#############
############# Resampling

new_sample_rate = 200

input_signal_resampled = resampy.resample(input_signal, input_edfworker.getSampleRate(), new_sample_rate)
output_signal_resampled = resampy.resample(output_signal, output_edfworker.getSampleRate(), new_sample_rate)


#############
############# Correlation

# We select a window from the output signal to avoid parts that do not correspond to anything
output_signal_resampled = select_data_window(output_signal_resampled, start_index= 13000, end_index= 15000)
input_signal_resampled = get_correlated_input_signal(input_signal=input_signal_resampled, output_signal=output_signal_resampled)

#############
############# Calculations over signals:
mse = get_mse(input_signal=input_signal_resampled, output_signal=output_signal_resampled)

print(f"mse = {mse}")

rest = stats.ttest_ind(input_signal_resampled, output_signal_resampled)
print(rest)


#############
############# Plotting

plot_time_axis = True
time_step = 1/new_sample_rate if plot_time_axis else 1

time_axis_in  = np.arange(start = 0, stop = len(input_signal_resampled) * time_step, step = time_step)
time_axis_out = np.arange(start = 0, stop = len(input_signal_resampled) * time_step, step = time_step)

plt.plot(time_axis_in, input_signal_resampled, 'r', label="Input signal") 
plt.plot(time_axis_out, output_signal_resampled, 'b', label="Measured signal")

plt.grid(True)
plt.title(f"{input_signal_file_name} Vs {output_signal_file_name}")
plt.legend()
plt.show()

plt.title(f"Error")
plt.plot(abs(input_signal_resampled - output_signal_resampled),'g', label="Error")
plt.legend()
plt.show()




input_filtered = SMA_filter(input_signal_resampled, 100)
output_filtered = SMA_filter(output_signal_resampled, 100)

plt.plot(input_filtered, 'r', label="Input signal") 
plt.plot(output_filtered, 'b--', label="Measured signal")
plt.title(f"Input filtered with SMA Vs Output filtered with SMA")
plt.legend()
#plt.show()

#np.savetxt('input_signal_resampled_fitted.dat', input_signal_resampled)
#np.savetxt('output_signal_resampled_fitted.dat', output_signal_resampled)