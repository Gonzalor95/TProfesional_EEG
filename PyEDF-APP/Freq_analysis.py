#!/usr/bin/python

import os
import resampy
import math
import numpy as np
from scipy.signal import butter, lfilter, spectrogram, periodogram, filtfilt, argrelextrema
from scipy.interpolate import interp1d, make_interp_spline, CubicSpline, PchipInterpolator
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
frequencies = [0.1, 0.2, 0.5, 0.8, 1, 2, 3, 5, 10, 15, 20, 25, 28, 30, 35, 40, 50, 66,77,88] 

time_axis_sample, signal_sample = generate_sinusoidal_waves_matching_time(amplitude=150, duration=5, frequencies=frequencies_a, sample_rate=1000)

channel = 'Fp2'
sample_rate = 200
output_signal = eeg_utils.generate_output_signal("0000056", [channel])
#output_signal = eeg_utils.generate_output_signal("FreqResponseSR1000", [channel])
#output_signal = eeg_utils.generate_output_signal("EEG_CommonSample1", [channel])

#output_signal = output_signal[4777:22277] #SR1
#output_signal = output_signal[5777:] #SR1000

### 
### PREVIEW SIGNAL


time_step = 1/sample_rate
time_axis  = np.arange(start = 0, stop = len(output_signal) * time_step, step = time_step)

figure, axis = plt.subplots(2, 1)

axis[0].set_title("Señal Output")
axis[0].plot(time_axis, output_signal, 'b')

axis[0].set_xlim([0, time_axis[-1]])

# i = 0
# duration = 5
# amplitude = 180
# for f in frequencies: 
#     axis[0].annotate(f"{f}Hz", xy=(i*duration, amplitude), xytext=(i*duration, amplitude + 0.02))
#     axis[0].axvline(i*duration, color='k', linestyle='--' )
#     axis[1].annotate(f"{f}Hz", xy=(i*duration, amplitude), xytext=(i*duration, amplitude + 0.02))
#     axis[1].axvline(i*duration, color='k', linestyle='--' )
#     i = i + 1

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



frequencies = frequencies[5:15]

N = len(output_signal)
T = 1/sample_rate
#x = np.linspace(0.0, N*T, N, endpoint=False)
output_signal_f = fft(output_signal)
xf = fftfreq(N, T)[:N//2]


for idx, value in enumerate(output_signal_f):
    if value < 1.2:
        output_signal_f[idx] = 0

plt.title("FFT de la señal Output")
output_signal_f = 2.0/N * np.abs(output_signal_f[0:N//2])
plt.plot(xf,output_signal_f)

aux = output_signal_f[0:int(len(xf))]
print(f"xf len = {len(xf)}")
print(f"output_signal_f len = {len(aux)}")
dbs = []
for idx, value in enumerate(xf):
    for freq in frequencies:
        if float(value) == float(freq):

            freq_value = max(aux[idx-3:idx+3])
            dbs.append(float(f'{freq_value:.1f}'))

#dbs = [3.35, 10, 8.52, 8.71, 8.88, 8.03, 6.56, 50, 75, 100, 125, 150, 175, 200, 250, 500]
for idx, f in enumerate(frequencies):
    plt.annotate(f"{dbs[idx]}db", xy=(f, dbs[idx]), xytext=(f-0.5, dbs[idx] + 0.5))

plt.xlim([0,40])
plt.ylim([0,10])
plt.xticks(np.arange(0, 40+1, 2.5))
plt.xlabel("Frecuencia [Hz]")
plt.ylabel("Amplitud [db]")
plt.grid()
plt.show()


#s = output_signal
#Fs = 200
#t = time_axis
#
#fig = plt.figure(figsize=(7, 7), layout='constrained')
#axs = fig.subplot_mosaic([["signal", "signal"],
#                          ["magnitude", "log_magnitude"],
#                          ["phase", "angle"]])
#
## plot time signal:
#axs["signal"].set_title("Signal")
#axs["signal"].plot(t, s, color='C0')
#axs["signal"].set_xlabel("Time (s)")
#axs["signal"].set_ylabel("Amplitude")
#
## plot different spectrum types:
#axs["magnitude"].set_title("Magnitude Spectrum")
#axs["magnitude"].magnitude_spectrum(s, Fs=Fs, color='C1')
#
#axs["log_magnitude"].set_title("Log. Magnitude Spectrum")
#axs["log_magnitude"].magnitude_spectrum(s, Fs=Fs, scale='dB', color='C1')
#
#axs["phase"].set_title("Phase Spectrum ")
#axs["phase"].phase_spectrum(s, Fs=Fs, color='C2')
#
#axs["angle"].set_title("Angle Spectrum")
#axs["angle"].angle_spectrum(s, Fs=Fs, color='C2')
#
#plt.show()

#dbs[0] = 7.5
#dbs[1] = 8
#dbs[2] = 7.5
#dbs[3] = 6.2 #5.9db
#dbs[3] = 5.5 #4.9db 

func = interp1d(frequencies, dbs,
                axis=0,  # interpolate along columns
                bounds_error=False,
                kind='cubic',
                fill_value="extrapolate")

func = make_interp_spline(frequencies, dbs, k=3, t=None, bc_type=None, axis=0, check_finite=True)

xnew = np.linspace(0, 30, 100)
ynew = func(xnew)

plt.plot(xnew, ynew)
#plt.plot(xf,2.0/N * np.abs(output_signal_f[0:N//2]))
plt.axvline(x = 0.8, color = 'y', label = '0.8Hz')

plt.xlabel("Frecuencia [Hz]")
plt.ylabel("Amplitud [db]")
plt.xlim([1,37.2])
plt.ylim([4, 9])
plt.grid()
plt.show()