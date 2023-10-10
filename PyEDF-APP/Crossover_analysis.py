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

#channels_crossoverCz = ['Cz', 'F3', 'Fz', 'F4', 'C3', 'C4', 'P3', 'Pz', 'P4']
#channels_crossoverCz = ['Cz', 'F3', 'Fz', 'F4', 'C3']
channels_crossoverCz = ['Cz', 'C4', 'P3', 'Pz', 'P4']
channels_crossoverT7 = ['T7', 'F8', 'T8', 'P7']

# Time checkpoints where there is data.
# "Channel + amplitud": [start_time, end_time] seg

    # [start_time, end_time]: 
    #   Cz:     100uV [44, 51]seg, 50uV [82,88]seg, 25uV [122, 128]seg
    #   Others: 100uV [208, 214]seg, 50V [254, 261]seg

#crossoverCz_1Hz_signals = eeg_utils.generate_output_signal("CrossOver_1Hz_Cz", channels_crossoverCz) 
#signals_checkpoints = {"1Hz Cz = 100": [45,51], "1Hz Cz = 50": [82,88], "1Hz Cz = 25": [122,128], "1Hz alrededor de Cz a 100": [208,214], "1Hz alrededor de Cz a 50": [254,261],}

#crossoverCz_signals = eeg_utils.generate_output_signal("Crossover_5Hz_Cz", channels_crossoverCz)
#signals_checkpoints = {"5Hz Cz = 100": [26,32], "5Hz Cz = 50": [50,56], "5Hz Cz = 25": [81,87], "5Hz alrededor de Cz a 100": [124,130],  "5Hz alrededor de Cz a 50": [157,163],}

crossoverT7_signals = eeg_utils.generate_output_signal("Crossover_5Hz_T7", channels_crossoverT7)
signals_checkpoints = {"5Hz T7 = 100": [29,35], "5Hz T7 = 50": [54,60], "5Hz T7 = 25": [86,91], "5Hz alrededor de T7 a 100": [118,124],  "5Hz alrededor de T7 a 50": [146,152],}


crossover_signals = crossoverT7_signals


#crossover_signals = list(signal_and_header for signal_and_header in crossover_signals if (signal_and_header['Channel'] == 'T7') or (signal_and_header['Channel'] == 'P7'))

sample_rate = 200
time_step = 1/sample_rate

for key, time_checkpoint in signals_checkpoints.items():

    figure, axis = plt.subplots(len(crossover_signals), 1)
    figure.suptitle(f"Crossover para {key} uV")
    for i in range(0,len(crossover_signals)):
        signal, time_axis = eeg_utils.select_data_window_by_time(crossover_signals[i]['Signal'], sample_rate, start_time = time_checkpoint[0], end_time = time_checkpoint[1])
        #signal = crossover_signals[i]['Signal']
        axis[i].plot(time_axis, signal)
        axis[i].set_xlim([0, time_axis[-1]])
        axis[i].set_ylabel(f"{crossover_signals[i]['Channel']}\nTensión [uV]")
        axis[i].grid()
        if i == len(crossover_signals) - 1:
            axis[i].set_xlabel("Tiempo [seg]")
        #axis[i].legend()

    plt.show()
