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
from modules.utils import generate_sinusoidal_waves_matching_time

import analysis_utils as eeg_utils

"""
Aca hago unos analisis en la respuesta en frecuencia
"""
# para la respuesta en frecuencia, hicimos 
frequencies_a = [0.1, 0.2, 0.5, 0.8, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 50, 100]
frequencies = [0.5, 1, 2.5, 4, 5, 10, 15, 25, 50, 75, 100, 125, 150, 175, 200, 250, 500] ## Al final nos dimos cuenta que multiplicaba x5


time_axis_sample, signal_sample = generate_sinusoidal_waves_matching_time(amplitude=150, duration=5, frequencies=frequencies_a, sample_rate=1000)

channel = 'Cz'
sample_rate = 200
output_signal = eeg_utils.generate_output_signal("FreqResponseSR1", [channel])
#output_signal = eeg_utils.generate_output_signal("FreqResponseSR1000", [channel])

output_signal = output_signal[4777:22277] #SR1
#output_signal = output_signal[5777:] #SR1000

### 
### PREVIEW SIGNAL


time_step = 1/sample_rate
time_axis  = np.arange(start = 0, stop = len(output_signal) * time_step, step = time_step)

figure, axis = plt.subplots(2, 1)

axis[0].set_title("Señal Output")
axis[0].plot(time_axis, output_signal, 'b')

axis[0].set_xlim([0, time_axis[-1]])

i = 0
duration = 5
amplitude = 180
for f in frequencies: 
    axis[0].annotate(f"{f}Hz", xy=(i*duration, amplitude), xytext=(i*duration, amplitude + 0.02))
    axis[0].axvline(i*duration, color='k', linestyle='--' )
    axis[1].annotate(f"{f}Hz", xy=(i*duration, amplitude), xytext=(i*duration, amplitude + 0.02))
    axis[1].axvline(i*duration, color='k', linestyle='--' )
    i = i + 1

axis[0].set_xlabel("Tiempo [seg]")
axis[0].set_ylabel("Tensión [uV]")
axis[0].grid()



axis[1].set_title("Señal Input")
axis[1].plot(time_axis_sample, signal_sample, 'r')
axis[1].set_xlim([0, time_axis_sample[-1]])
axis[1].set_ylim([-155, 195])
axis[1].set_xlabel("Tiempo [seg]")
axis[1].set_ylabel("Tensión [uV]")
axis[1].grid()

plt.show()



N = len(output_signal)
T = 1/sample_rate
#x = np.linspace(0.0, N*T, N, endpoint=False)
output_signal_f = fft(output_signal)
xf = fftfreq(N, T)[:N//2]
# for local maxima
local_maxs = argrelextrema(2.0/N * np.abs(output_signal_f[0:N//2]), np.greater)
print("local_maxs:")
for max in local_maxs:
    print(f"freq = {xf[max]}")
# for local minima
local_mins = argrelextrema(2.0/N * np.abs(output_signal_f[0:N//2]), np.less)
print(local_mins)




plt.title("FFT de la señal Output")
plt.plot(xf,2.0/N * np.abs(output_signal_f[0:N//2]))

frequencies = [1, 2.5, 4, 5, 10, 15, 25]
dbs = [3.35, 10, 8.52, 8.71, 8.88, 8.03, 6.56, 50, 75, 100, 125, 150, 175, 200, 250, 500]
for idx, f in enumerate(frequencies):
    plt.annotate(f"{dbs[idx]}db", xy=(f, dbs[idx]), xytext=(f-0.5, dbs[idx] + 0.05))

plt.xlim([0,35])
plt.ylim([0,11])
plt.xlabel("Frecuencia [Hz]")
plt.ylabel("Amplitud [db]")
plt.grid()
plt.show()

