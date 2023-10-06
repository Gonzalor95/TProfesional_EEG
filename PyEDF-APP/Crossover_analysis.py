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


crossover_signals = crossoverCz_1Hz_signals

sample_rate = 200
time_step = 200

time_axis = np.arange(start = 0, stop = len(crossover_signals[0]['Signal']) * time_step, step = time_step)

figure, axis = plt.subplots(len(crossover_signals), 1)

for i in range(0,len(crossover_signals)):
    #axis[i].set_title(f"Signal {crossover_signals[i]['Channel']}")
    axis[i].plot(time_axis, crossover_signals[i]['Signal'])
    axis[i].set_xlim([0, time_axis[-1]])
    axis[i].set_ylabel(f"{crossover_signals[i]['Channel']}")
    axis[i].grid()
    #axis[i].legend()

plt.show()
