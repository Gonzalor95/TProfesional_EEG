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
    window_starts = np.arange(start = window_size, stop = len(input_signal) * time_step - window_size * 4, step = window_size)

    print(window_starts)
    mse = 9999999
    for window_start in window_starts:
        start_index = int(window_start) * sample_rate
        end_index= (int(window_start) + window_size) * 200

        selected_input_signal = select_data_window(input_signal, start_index= start_index, end_index= end_index)
        selected_output_signal, discard = get_correlated_input_signal(input_signal=output_signal, output_signal=selected_input_signal)

        current_mse = get_mse(input_signal=selected_input_signal,output_signal=selected_output_signal)

        if current_mse < mse:
            mse = current_mse
            print(f"mse = {mse} for window = [{window_start} - {window_start + window_size} ] seg")
            best_window_start = window_start

    print(f"#####################best window start = {best_window_start} with mse = {mse}")
    return best_window_start

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

    input_signal_duration = len(input_signal) / 200
    output_signal_duration = len(output_signal) / 200
    print(f"Input signal duration = {input_signal_duration}")
    print(f"Output signal duration = {output_signal_duration}")
    print(f"Correlation returned index = {index}")
    
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
    print(f"Latest mse = {mse} with saved_i = {saved_i}. ")
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

def general_analysis():
    """
    GENERAL ANALYSIS: Aca hago un analisis general
    """

    input_signal_file_name = "common_mode_sample1"
    output_signal_file_name = "EEG_CommonSample1"
    #output_signal_file_name = "Sen200uV"



    input_signal_filepath = os.path.join(".", "edf_samples", f"{input_signal_file_name}.edf")
    output_signal_filepath = os.path.join(".", "edf_samples", "data_analysis", f"{output_signal_file_name}.edf")

    channel = 'Fp1'
    #input_signal, input_edfworker = get_testing_signal(signal_type = 'Sinusoidal', frecuency = 5, amplitude = 200, sample_rate = 500, duration = 5*10)
    input_signal, input_edfworker = get_signal_and_edf_worker_from_edf(signal_filepath=input_signal_filepath, channel=channel, is_output=False)
    output_signal, output_edfworker  = get_signal_and_edf_worker_from_edf(signal_filepath=output_signal_filepath, channel=channel, is_output=True)



    ##
    ## PREVIEW SIGNALS BEFORE WORKING:

    time_step_output = 1/output_edfworker.getSampleRate()
    time_step_input = 1/input_edfworker.getSampleRate()
    t_output = np.arange(start = 0, stop = len(output_signal) * time_step_output, step = time_step_output)
    t_input = np.arange(start = 0, stop = len(input_signal) * time_step_input, step = time_step_input)
    figure, axis = plt.subplots(2, 1)

    axis[0].plot(t_input,input_signal, 'r', label="Input") 
    axis[0].set_title(f"Señal de Input completa - Canal Fp1")
    axis[0].set_xlim([0, t_input[-1]])
    axis[0].set_xlabel("Tiempo [seg]")
    axis[0].set_ylabel("Tensión [uV]")
    axis[0].legend()
    axis[0].grid()

    axis[1].plot(t_output,output_signal, 'b', label="Output") 
    axis[1].set_title(f"Señal de Output completa - Canal Fp1")
    axis[1].set_xlim([0, t_output[-1]])
    axis[1].set_xlabel("Tiempo [seg]")
    axis[1].set_ylabel("Tensión [uV]")
    axis[1].legend()
    axis[1].grid()

    plt.show()



    #############
    ############# FILTERS
    #input_signal = butterworth_filter(data=input_signal,btype = 'low', cutoff_freq = 30, fs = input_edfworker.getSampleRate(), order = 1)
    #input_signal = butterworth_filter(data=input_signal,btype = 'high', cutoff_freq = 0.8, fs = input_edfworker.getSampleRate(), order = 1)

    #input_signal = slew_rate_filter(input_signal, 10)

    #############
    ############# Resampling

    new_sample_rate = 200

    input_signal_resampled = resampy.resample(input_signal, input_edfworker.getSampleRate(), new_sample_rate)
    output_signal_resampled = output_signal#resampy.resample(output_signal, output_edfworker.getSampleRate(), new_sample_rate)


    ####
    #### BEST WINDOW:

    select_best_data_window(input_signal=input_signal_resampled,output_signal=output_signal_resampled,window_size=5)


    #############
    ############# Correlation

####################################################
    ############## NOTA IMPORTANTE: Tuve que dar vuelta la input y output aca porque asi obtenia la ventana que estabamos seleccionando con referencia a input
    #######################
    # We select a window from the output signal to avoid parts that do not correspond to anything

    sample_window_duration = 5 # seg
    # Muestra A
    #selected_start_window = 15 # seg
    # Muestra B
    #selected_start_window = 60 # seg
    # Muestra C
    selected_start_window = 150 # seg

    window = [selected_start_window, selected_start_window + sample_window_duration]
    start_index = selected_start_window * 200
    end_index= (selected_start_window + sample_window_duration) * 200



    #window = [start_index / input_edfworker.getSampleRate(), end_index / input_edfworker.getSampleRate()]
    #print(f"Tomamos la ventana de tiempo entre {window[0]} y {window[1]} segundos ")
    input_signal_resampled = select_data_window(input_signal_resampled, start_index= start_index, end_index= end_index)
    


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
    figure, axis = plt.subplots(2, 1)

    #figure.suptitle(f"{input_signal_file_name} Vs {output_signal_file_name}")

    axis[0].plot(time_axis,input_signal_resampled, 'r', label="Input") 
    axis[0].plot(time_axis, output_signal_resampled, 'b--', label="Output")
    #axis[0].set_title(f"{input_signal_file_name} Vs {output_signal_file_name}")
    axis[0].set_title(f"Señal de Prueba Vs Señal Medida. Muestra entre [{window[0]} - {window[1]}] segs. Canal = {channel}")
    axis[0].set_xlim([0, time_axis[-1]])
    axis[0].set_xlabel("Tiempo [seg]")
    axis[0].set_ylabel("Tensión [uV]")
    axis[0].legend()
    axis[0].grid()


    axis[1].plot(time_axis, input_signal_resampled - output_signal_resampled,'g', label="Error= Input - Output")
    axis[1].set_title(f"ECM = {mse:.2f}")
    axis[1].set_xlim([0, time_axis[-1]])
    axis[1].set_xlabel("Tiempo [seg]")
    axis[1].set_ylabel("Tensión [uV]")
    axis[1].legend()
    axis[1].grid()

    plt.show()


    #############
    ############# SMA Filtering:


#    SMA_sample_count = get_optimized_window_size_for_SMA(input_signal_resampled, output_signal_resampled)
#    input_filtered = SMA_filter(input_signal_resampled, SMA_sample_count)
#    output_filtered = SMA_filter(output_signal_resampled, SMA_sample_count)
#
#    mse = get_mse(input_signal=input_filtered, output_signal=output_filtered)
#
#    time_axis = np.arange(start = 0, stop = len(input_filtered) * time_step, step = time_step)
#
#    figure, axis = plt.subplots(2, 1)
#
#    axis[0].plot(time_axis, input_filtered, 'r', label="Input") 
#    axis[0].plot(time_axis, output_filtered, 'b--', label="Output")
#    axis[0].set_title(f"Señal de Prueba Vs Señal Medida (utilizando filtro SMA de {SMA_sample_count} puntos)")
#    axis[0].set_xlim([0, time_axis[-1]])
#    axis[0].set_xlabel("Tiempo [seg]")
#    axis[0].set_ylabel("Tensión [uV]")
#    axis[0].legend()
#    axis[0].grid()
#
#
#    axis[1].plot(time_axis, [input_filtered[i] - output_filtered[i] for i in range(len(input_filtered))], 'g', label="Error")
#    axis[1].set_xlim([0, time_axis[-1]])
#    axis[1].set_title(f"ECM = {mse:.2f}")
#    axis[1].set_xlabel("Tiempo [seg]")
#    axis[1].set_ylabel("Tensión [uV]")
#    axis[1].legend()
#    axis[1].grid()
#
#    plt.show()
    #############
    ############# Saving Signals

    #np.savetxt('input_signal_resampled_fitted.dat', input_signal_resampled)
    #np.savetxt('output_signal_resampled_fitted.dat', output_signal_resampled)



    #############
    ############# Frequency analysis



    #f_i, t_i, Sxx_i = spectrogram(input_signal_resampled, fs=new_sample_rate,scaling='density')
    #f_o, t_o, Sxx_o = spectrogram(output_signal_resampled, fs=new_sample_rate,scaling='density')#

    #Sxx = Sxx_i - Sxx_o

    #plt.pcolormesh(t_i, f_i, Sxx_i, shading='gouraud')
    #plt.title(f"Input")
    #plt.ylabel('Frequency [Hz]')
    #plt.xlabel('Time [sec]')
    #plt.show()


    #f, Pxx_den_i = periodogram(input_signal_resampled, fs=new_sample_rate,)
    #f, Pxx_den_o = periodogram(output_signal_resampled, fs=new_sample_rate,)

    #plt.semilogy(f, Pxx_den_i,'r-', label="Input")
    #plt.semilogy(f, Pxx_den_o,'b', label="Output")
    #plt.ylim([1e-7, 1e2])
    #plt.xlabel('frequency [Hz]')
    #plt.ylabel('PSD [V**2/Hz]')
    #plt.legend()
    #plt.show()


def freq_response_analysis():
    """
    Aca hago unos analisis en la respuesta en frecuencia
    """
    output_FreqResponseSR1_file_name = "FreqResponseSR1" # hacer output_signal = output_signal[4777:]
    output_FreqResponseSR1000_file_name = "FreqResponseSR1000" # hacer output_signal = output_signal[1000:]
    # para la respuesta en frecuencia, hicimos 
    frequencies = [0.1, 0.2, 0.5, 0.8, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 50, 100]
    
    

    output_SR1_filepath = os.path.join(".", "edf_samples", "data_analysis", f"{output_FreqResponseSR1_file_name}.edf")
    output_SR1000_filepath = os.path.join(".", "edf_samples", "data_analysis", f"{output_FreqResponseSR1000_file_name}.edf")

    output_SR1, output_edfworker_SR1  = get_signal_and_edf_worker_from_edf(signal_filepath=output_SR1_filepath, channel='Fp1', is_output=True)
    output_SR1000, output_edfworker_SR1000  = get_signal_and_edf_worker_from_edf(signal_filepath=output_SR1000_filepath, channel='Fp1', is_output=True)

    output_SR1 = output_SR1[4777:]
    output_SR1000 = output_SR1000[5777:]
    ### Preview Signal:
    time_step = 1/output_edfworker_SR1.getSampleRate()
    time_axis_SR1  = np.arange(start = 0, stop = len(output_SR1) * time_step, step = time_step)
    time_axis_SR1000  = np.arange(start = 0, stop = len(output_SR1000) * time_step, step = time_step)
    #plt.plot(time_axis_SR1, output_SR1)
    plt.plot(time_axis_SR1000, output_SR1000)
    plt.plot()
    i = 0
    duration = 5
    amplitude = 200
    for f in frequencies: 
        plt.annotate(f"{f*5}Hz", xy=(i*duration, amplitude + 0.01), xytext=(i*duration, amplitude + 0.02)
                #arrowprops=dict(facecolor='black', shrink=0.05),
                )
        i = i + 1
    plt.show()

    N = len(output_SR1)
    T = 1/output_edfworker_SR1.getSampleRate()
    #x = np.linspace(0.0, N*T, N, endpoint=False)

    output_signal_f = fft(output_SR1)
    xf = fftfreq(N, T)[:N//2]


    # for local maxima
    local_maxs = argrelextrema(2.0/N * np.abs(output_signal_f[0:N//2]), np.greater)

    print("local_maxs:")
    for max in local_maxs:
        print(f"freq = {xf[max]}")

    # for local minima
    local_mins = argrelextrema(2.0/N * np.abs(output_signal_f[0:N//2]), np.less)
    print(local_mins)
    
    plt.plot(xf, 2.0/N * np.abs(output_signal_f[0:N//2]))
    plt.show()



"""
=================================================================================
====================================  Main   ====================================
=================================================================================
"""

general_analysis()
#freq_response_analysis()