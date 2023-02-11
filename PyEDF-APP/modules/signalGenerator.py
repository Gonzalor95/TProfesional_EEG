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
    def timestamp (start, stop, step):
        t = [start]
        while t[-1] < stop:
            t.append(t[-1] + step)
        return t

    def _apply_function(self,t):
        return 0

    def generateSignal(self, start, stop, sample_rate):
        t = self.timestamp(start, stop, sample_rate)
        y = self._apply_function()

class PulseTrain(SignalToGenerate):

  def __init__(self, amplitude = 0,freq = 0,sample_rate = 0):
    super().__init__(amplitude,freq,sample_rate,signal_type_name= "Pulse Train")



if __name__ == '__main__':
    os.system('cls') ## Clear screen
