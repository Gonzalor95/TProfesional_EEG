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

import analysis_utils as eeg_utils

"""
Aca hago unos analisis en la respuesta en frecuencia
"""
output_FreqResponseSR1_file_name = "FreqResponseSR1" # hacer output_signal = output_signal[4777:]
output_FreqResponseSR1000_file_name = "FreqResponseSR1000" # hacer output_signal = output_signal[1000:]
# para la respuesta en frecuencia, hicimos 
frequencies = [0.1, 0.2, 0.5, 0.8, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 50, 100]
frequencies = [0.5, 1, 2.5, 4, 5, 10, 15, 25, 50, 75, 100, 125, 150, 175, 200, 250, 500]


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
plt.plot(time_axis, output_signal)
plt.xlim([0, time_axis[-1]])
plt.plot()

i = 0
duration = 5
amplitude = 180
for f in frequencies: 
    plt.annotate(f"{f*5}Hz", xy=(i*duration, amplitude + 0.01), xytext=(i*duration, amplitude + 0.02)
            #arrowprops=dict(facecolor='black', shrink=0.05),
            )
    i = i + 1
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

plt.plot(xf, 2.0/N * np.abs(output_signal_f[0:N//2]))
plt.show()