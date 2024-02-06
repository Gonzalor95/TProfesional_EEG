#!/usr/bin/python

from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from modules.utils import generate_sinusoidal_waves_matching_time
from scipy.fft import fft, fftfreq

import numpy as np


frequencies = [0.1, 0.2, 0.5, 0.8, 1, 2, 3, 5, 10, 15, 20, 22, 25, 28, 30, 32, 34, 37, 40, 50]


amplitude = 200
sample_rate = 800
duration = 10

print(len( np.linspace(0, duration, duration * sample_rate, endpoint=False)))

t, output = generate_sinusoidal_waves_matching_time(amplitude = 199, duration = duration, frequencies = frequencies, sample_rate = sample_rate)

plt.plot(t, output)
plt.show()


N = len(output)
T = 1/sample_rate
output_signal_f = fft(output)
xf = fftfreq(N, T)[:N//2]

plt.title("FFT de la señal Output")
plt.plot(xf,2.0/N * np.abs(output_signal_f[0:N//2]))

plt.show()


#s = output
#Fs = 200
#t = t
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