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

# Files
# "CrossOver_1Hz_Cz.edf", "Crossover_5Hz_Cz.edf", "Crossover_5Hz_T7.edf"

channels_crossoverCz = ['Cz', 'F3', 'Fz', 'F4', 'C3', 'C4', 'P3', 'Pz', 'P4']
channels_crossoverT7 = ['T7', 'F8', 'T8', 'P7']
crossoverCz_1Hz_signals = eeg_utils.generate_output_signal("CrossOver_1Hz_Cz", channels_crossoverCz)
#crossoverCz_signals = eeg_utils.generate_output_signal("Crossover_5Hz_Cz", channels_crossoverCz)
#crossoverT7_signals = eeg_utils.generate_output_signal("Crossover_5Hz_T7", channels_crossoverT7)


print(crossoverCz_1Hz_signals)

#figure, axis = plt.subplots(len(channels_crossoverCz), 1)

#for i in range(0,len(channels_crossoverCz)):
#    axis[i].set_title(f"Signal{channels_crossoverCz[i]}")
#    axis[i].plot(crossoverCz_signals)
#    axis[i].plot(time_ax
#    axis[i].plot(time_ax
#    axis[i].set_xlim([0,
#    axis[i].set_ylabel("
#    axis[i].grid()
#    axis[i].legend()
