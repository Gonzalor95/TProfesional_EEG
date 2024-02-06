import os
import resampy
import math
import numpy as np
from scipy.signal import (
    butter,
    lfilter,
    spectrogram,
    periodogram,
    filtfilt,
    argrelextrema,
)
from scipy.fft import fft, fftfreq
from scipy import stats
import yaml
from modules.EDFWorker import EDFWorker
import matplotlib.pyplot as plt
from modules.TestingSignals import TestingSignalsWorker
import analysis_utils as eeg_utils


class SNRAnalysis:
    def __init__(self, frequency = 5):

        self.frequency = frequency
        self.amplitudes = [199, 100, 50, 25, 10, 5, 2]
        self.window_size = 3*200
        

        self.correlated_signals = []
        self.correlated_sample_signals = []

        self.all_signals = []
        self.all_sample_signals = []

        self.amp_adjust = 1
        channel = "Fp1"
        if self.frequency == 1:
            self.amp_adjust = 1
            full_signal = eeg_utils.generate_output_signal("SNR_1Hz", [channel])
            self.all_signals.append(full_signal[9100:9841])#.append(full_signal[9050:9841])
            self.all_signals.append(full_signal[13650:14389])#.append(full_signal[13597:14389])
            self.all_signals.append(full_signal[19345:20102])#.append(full_signal[19294:20102])
            self.all_signals.append(full_signal[23727:24478])#.append(full_signal[23652:24478])
            self.all_signals.append(full_signal[28039:28788])#.append(full_signal[27966:28788])
            self.all_signals.append(full_signal[32842:33590])#.append(full_signal[32762:33590])
            self.all_signals.append(full_signal[38240:39001])#.append(full_signal[38147:39001])

        elif self.frequency == 5:
            self.amp_adjust = 199/150
            self.window_size = 400
            full_signal = eeg_utils.generate_output_signal("SNR_5Hz", [channel])
            self.all_signals.append(full_signal[3863:4742])#append(full_signal[3763:4742])
            self.all_signals.append(full_signal[8193:9077])#append(full_signal[8093:9077])
            self.all_signals.append(full_signal[12512:13371])#append(full_signal[12389:13371])
            self.all_signals.append(full_signal[16112:16918])#append(full_signal[16012:16918])
            self.all_signals.append(full_signal[21030:21654])#append(full_signal[20930:21654])
            self.all_signals.append(full_signal[25925:26547])#append(full_signal[25825:26547])
            self.all_signals.append(full_signal[30050:30549])#append(full_signal[29950:30549])

        elif self.frequency == 10:
            self.amp_adjust = 199/162
            self.window_size = 400
            full_signal = eeg_utils.generate_output_signal("SNR_10Hz", [channel])
            self.all_signals.append(full_signal[3800:4571])
            self.all_signals.append(full_signal[7156:7892])
            self.all_signals.append(full_signal[13095:13772])
            self.all_signals.append(full_signal[17735:18315])
            self.all_signals.append(full_signal[21987:22456])
            self.all_signals.append(full_signal[26582:27041])
            self.all_signals.append(full_signal[31976:32411])
        else:
            raise "Wrong frequency"

        self.all_sample_signals = self.generate_SNR_sample_signal()

        



    def plot_all_signals(self):
        for idx, signal in enumerate(self.correlated_signals):
            plt.plot(signal, label=f"Signal {idx}")
        plt.show()

    def plot_average_signal(self):
        plt.plot(self.data, label="Average signal")

    def correlate_all_signals(self):

        for idx, signal in enumerate(self.all_signals):
            offset = eeg_utils.get_correlation_offset(self.all_sample_signals[idx], signal) + 1
            if offset > 0:
                self.correlated_signals.append(signal[offset:])
                self.correlated_sample_signals.append(self.all_sample_signals[idx])
            else:
                self.correlated_signals.append(
                    np.concatenate((np.zeros(-offset), signal))
                )
                self.correlated_sample_signals.append(self.all_sample_signals[idx])

            self.correlated_signals[idx] = self.correlated_signals[idx][abs(offset):abs(offset)+self.window_size]
            self.correlated_sample_signals[idx] = self.correlated_sample_signals[idx][abs(offset):abs(offset)+self.window_size]
            
            print( f"Offset was: {offset}. Length of the correalted signal is: {len(self.correlated_signals[idx])}")
            #print(f"MSE = {eeg_utils.calculate_mse(self.correlated_signals[idx], self.correlated_sample_signals[idx])}")

    def generate_SNR_sample_signal(self):
        """ Freq: [Hz]"""


        sample_signal = []
        duration  = 6

        sample_rate = 200

        time = np.arange(0, duration, 1 / sample_rate)
        for amplitude in self.amplitudes:
            sample_signal.append(amplitude * np.sin(2*np.pi * self.frequency * time))

        return sample_signal

    def get_shortest_signal(self):
        return min(len(ls) for ls in self.correlated_signals)




def equalize_signal_lengths(s1, s2):
    min_len = min(len(s1), len(s2))
    return s1[:min_len], s2[:min_len]


snr_analysis = SNRAnalysis(frequency = 5)

snr_analysis.correlate_all_signals()




figure, axis = plt.subplots(3, 1)

time_step=1/200
time_axis = np.arange(start = 0, stop = len(snr_analysis.correlated_sample_signals[5]) * time_step, step = time_step)



for i in range(0,3):
    sample_signal = snr_analysis.correlated_sample_signals[i]
    signal = snr_analysis.correlated_signals[i] * snr_analysis.amp_adjust
    axis[i].set_title(f"Input vs Output ({snr_analysis.frequency}Hz) - SNR = {eeg_utils.calculate_log_snr(input=sample_signal, output=signal):.2f} dB")
    axis[i].plot(time_axis, sample_signal, 'b', label='Input')
    axis[i].plot(time_axis, signal, 'r', label='Output')
    axis[i].plot(time_axis, sample_signal- signal, 'g', label='Error=Input-Output')
    axis[i].set_xlim([0, time_axis[-1]])
    axis[i].set_ylabel("Tensión [uV]")
    if i == 2:
        axis[i].set_xlabel("Tiempo [seg]")            
    axis[i].grid()
    axis[i].legend()
    
plt.show()

figure, axis = plt.subplots(3, 1)
for i in range(3,6):
    sample_signal = snr_analysis.correlated_sample_signals[i]
    signal = snr_analysis.correlated_signals[i] * snr_analysis.amp_adjust

    axis[i-3].set_title(f"Input vs Output ({snr_analysis.frequency}Hz) - SNR = {eeg_utils.calculate_log_snr(input=sample_signal, output=signal):.2f} dB")
    axis[i-3].plot(time_axis, sample_signal, 'b', label='Input')
    axis[i-3].plot(time_axis, signal, 'r', label='Output')
    axis[i-3].plot(time_axis, sample_signal- signal, 'g', label='Error=Input-Output')
    axis[i-3].set_xlim([0, time_axis[-1]])
    axis[i-3].set_ylabel("Tensión [uV]")
    if (i-3) == 2:
        axis[i-3].set_xlabel("Tiempo [seg]")    
    axis[i-3].grid()
    axis[i-3].legend()
    
plt.show()


i= 6
sample_signal = snr_analysis.correlated_sample_signals[i]
signal = snr_analysis.correlated_signals[i] * snr_analysis.amp_adjust
plt.title(f"Input vs Output ({snr_analysis.frequency}Hz) - SNR = {eeg_utils.calculate_log_snr(input=sample_signal, output=signal):.2f} dB")
plt.plot(time_axis, sample_signal, 'b', label='Input')
plt.plot(time_axis, signal, 'r', label='Output')
plt.plot(time_axis, sample_signal- signal, 'g', label='Error=Input-Output')
plt.xlim([0, time_axis[-1]])
plt.ylabel("Tensión [uV]")
plt.xlabel("Tiempo [seg]")
plt.grid()
plt.legend()
    
plt.show()

