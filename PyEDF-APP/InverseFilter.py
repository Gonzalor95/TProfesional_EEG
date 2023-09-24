#!/usr/bin/python

import os
import resampy
import math
import numpy as np
from scipy.signal import butter, lfilter, spectrogram, periodogram, filtfilt, sosfiltfilt, iirnotch, stft, deconvolve, freqs
from scipy import stats
import matplotlib.pyplot as plt

def inverse_filter(data = [], stopband = [0.8, 30], fs = 1):

    sos = butter(N = 1, Wn = stopband, fs = fs, btype = 'bandstop', analog = False, output='sos')
    bw = stopband[1] - stopband[0] # =  29.2
    w0 = stopband[0] + (stopband[1] - stopband[0])/2 # 0.8 + ( 14.6 ) = 15.4

    Q = w0/bw 
    b, a = iirnotch(w0 = w0, Q = Q, fs=fs)

    gain = 1.41 # 3db

    data = data * gain
    y = filtfilt(b, a, data) # Notch
    #y = sosfiltfilt(sos, data) # Butter bandstop

    return y

def deconvolve_from_butter(data = [], fs = 1):

    b, a = butter(N = 1, Wn = [0.8, 30], fs = fs, btype = 'bandpass', analog = False, output='ba')

    w, h = freqs(b, a)


    # Apply linear filter:
    signal_filtered = filtfilt(b,a, data)    

    xRecovered, xRemainder = deconvolve(signal = signal_filtered, divisor = a)
    return xRecovered


def generateSinSignal_(frecuency, amplitude, sample_rate, duration):
    """
    Method to generate a sinusoidal signal
    """
    time = np.arange(0, duration, 1 / sample_rate)
    return amplitude * np.sin(2*np.pi * frecuency * time)

def generate_sinusoidal_waves_matching_time(amplitude, duration, frequencies, sample_rate):
        """
        Generates a single signal that contains all frequencies. Each repeated for a duration specified by parameter.
        """
        t = np.linspace(0, duration*len(frequencies), duration * len(frequencies) * sample_rate, endpoint=False)
        signal = np.array([])

        for frequency in frequencies:
            cycle = amplitude*np.sin(10 * np.pi * frequency * np.linspace(0, duration, duration * sample_rate, endpoint=False))
            signal = np.append(signal, cycle)
        return t, signal

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
    #b, a = butter(order, cutoff_freq, fs = fs, btype = btype, analog = False)
    sos = butter(order, cutoff_freq, fs = fs, btype = btype, analog = False, output='sos')

    # Apply linear filter:
    y = sosfiltfilt(sos, data)
    return y



#frequencies = [0.003,0.008, 0.03, 0.08, 0.3, 0.8, 3, 8, 30, 80, 300, 800]
frequencies = [0.1, 0.2, 0.5, 0.8, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 50, 100]

amplitude = 10
sampling_rate = 2000
duration = 10

t, signal = generate_sinusoidal_waves_matching_time(amplitude, duration, frequencies, sampling_rate)

signal_inverse_filter = inverse_filter(data = signal, stopband = [0.8, 30], fs = sampling_rate)

signal_inverse_filter = signal_inverse_filter #+ signal

signal_filtered = signal
signal_filtered = butterworth_filter(signal_filtered, btype='high', cutoff_freq = 0.8, fs = sampling_rate, order = 1)
signal_filtered = butterworth_filter(signal_filtered, btype='low', cutoff_freq = 30, fs = sampling_rate, order = 1)


#signal_deconvolve = deconvolve_from_butter(data = signal, fs = sampling_rate)

fig, ax = plt.subplots()

ax.plot(t, signal, 'b', label='Input')
#ax.plot(t, signal_filtered, 'r', label='Filtered')
#ax.plot( signal_deconvolve, 'r', label='Deconvolve')
#ax.plot(t, signal_inverse_filter, 'g--', label='Inverse Filter')
#ax.plot(t, signal_reconstructed, 'y--', label='Reconstructed')

i = 0
for f in frequencies: 
    ax.annotate(f"{f*5}Hz", xy=(i*duration, amplitude + 0.01), xytext=(i*duration, amplitude + 0.02)
                #arrowprops=dict(facecolor='black', shrink=0.05),
                )
    i = i + 1

plt.legend()
plt.show()

f, t, Sxx = spectrogram(signal, fs=sampling_rate,scaling='density')

plt.pcolormesh(t, f, Sxx, shading='gouraud')
plt.title(f"Input")
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.show()