import os
import random
import numpy
import matplotlib.pyplot as plt
from scipy import signal

"""
Class to create required signals like:
- pulse train
- sine wave
- triangular wave
"""
"""
Codigo de señales tuki

import numpy as np
from scipy import signal
import matplotlib.pyplot as plot

def get_sin_wave(amplitude, frecuency, time_span, sample_rate):
    time = np.arange(0, time_span, time_span / sample_rate)
    return time, amplitude * np.sin(2*np.pi * frecuency * time)

def get_square_wave(amplitude, frecuency, time_span, sample_rate):
    time = np.arange(0, time_span, time_span / sample_rate)
    return time, amplitude *  signal.square(2*np.pi * frecuency * time)

def get_triangular_wave(amplitude, frecuency, time_span, sample_rate):
    time = np.arange(0, time_span, time_span / sample_rate)
    return time, amplitude *  signal.sawtooth(2*np.pi * frecuency * time, 0.5)

amplitude = 1
frecuency = 100
time_span = 1
sample_rate = 10000
# time, wave = get_sin_wave(amplitude, frecuency, time_span, sample_rate)
# time, wave = get_square_wave(amplitude, frecuency, time_span, sample_rate)
time, wave = get_triangular_wave(amplitude, frecuency, time_span, sample_rate)

# When frecuency >= sample rate I'm getting a weird behavior I cannot explain
# When sending the signal to the microcontroller we should do it following the same frecuency used to create the signals

plot.plot(time, wave)
plot.show()


"""

    
class SignalToGenerate():

    amplitude = 0
    freq = 0
    sample_rate = 0
    signal_type_name = None

    def __init__(self, amplitude = 0,freq = 0,sample_rate = 0,signal_type_name = None):

        amplitude = amplitude
        freq = freq
        sample_rate = sample_rate
        signal_type_name = signal_type_name

    def __str__(self):
        return f"Signal: {self.signal_type_name}"

    """
    Generator for timestamp
    """
    def timestamp (self, start, stop):
        t = [start]
        while t[-1] < stop:
            t.append(t[-1] + self.sample_rate)
        return t

    def _apply_function(self,t):
        return 0

    def generateSignal(self, start, stop):
        t = self.timestamp(start=start, stop=stop)
        y = self._apply_function()

class PulseTrain(SignalToGenerate):

    def __init__(self, amplitude = 0,freq = 0,sample_rate = 0):
        super().__init__(amplitude,freq,sample_rate,signal_type_name= "Pulse Train")

    def _apply_function(self, t):
        return t +5

if __name__ == '__main__':
    os.system('cls') ## Clear screen

    pulseTrain = PulseTrain(amplitude=1,freq=3,sample_rate=5)
    y = pulseTrain.generateSignal(start=0,stop=4)
    plt.plot(y)
    plt.show()
