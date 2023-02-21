#!/usr/bin/python

from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from modules.ChannelToIntProtocol import ProtocolDict

"""
Class to handle the testing signals
"""


# Structure type of class to hold the signal data
# Array lenghts should all be the same
class SignalData:
    signal_name = ""  # ["Square", "Sinusoidal", "Triangular"]
    signal = []
    frecuency = 0
    sample_rate = 0
    amplitude = 0
    duration = 0
    # Parsed channel names, may not be the same as the ones present in the signal headers
    channel_names = []


class TestingSignalsWorker():
    # List with all the channels selected for the simulator
    selected_channels_ = []
    # Selected simulation time
    selected_sim_time_ = ()
    # Possible testing signals
    testing_signals_ = ["Square", "Sinusoidal", "Triangular"]
    # Default values for the signal
    DEFAULT_FRECUENCY = 50  # Hz
    DEFAULT_AMPLITUD = 20  # uV
    DEFAULT_TIME_SPAN = 60  # sec
    DEFAULT_SAMPLE_RATE = 2048  # points per second

    def __init__(self, max_channels):
        self.max_channels_ = max_channels
        self.selected_channels_ = range(max_channels)
        self.selected_sim_time_ = ()
        self.signal_data_ = SignalData()
        print("Testing signals worker initialized")

    def getSignalInfo(self):
        """
        Returns a dictionary with the signal information:
        Currently returns: Number of channels, dimension, sample_rate.
        """
        signal_info_dict = {}
        signal_info_dict["Dimension"] = self.getSignalDimension()
        signal_info_dict["Number of channels"] = self.getNumberOfChannels()
        signal_info_dict["Duration [s]"] = self.getDuration()
        signal_info_dict["Frecuency [Hz]"] = self.getFrecuency()
        signal_info_dict["Amplitude [uV]"] = self.getAmplitud()
        signal_info_dict["Sample Rate [1/seg]"] = self.getSampleRate()
        return signal_info_dict

    def getNumberOfChannels(self):
        """
        Getter for the number of channels in the file
        """
        return self.max_channels_

    def getDuration(self):
        """
        Getter for the testing signal duration in seconds
        """
        return self.signal_data_.duration

    def getSignalDimension(self):
        """
        Getter for the signal unit dimension
        """
        return "uV"

    def getAmplitud(self):
        """
        Getter for the testing signal amplitud
        """
        return self.signal_data_.amplitude

    def getFrecuency(self):
        """
        Getter for the testing signal frecuency
        """
        return self.signal_data_.frecuency

    def getSampleRate(self):
        """
        Getter for the testing signal sample rate
        """
        return self.signal_data_.sample_rate

    def resetTestSignalWorker(self):
        """
        Method to re-initialize the testing signal module
        """
        self.signal_data_ = SignalData()
        self.selected_channels_ = []
        self.selected_sim_time_ = ()

    def setSelectedChannels(self, selected_channels):
        """
        Method to set the selected channels array
        param[in]: "selected_channels" Array of integers with the selected channels
        """
        if self.selected_testing_signal_:
            number_of_channels = self.getNumberOfChannels()
            # Check the size of the input array
            if len(selected_channels) < 0 or len(selected_channels) > number_of_channels:
                print("Invalid amount of selected channels")
                return False
            # Check that all channels are valid
            for channel_number in selected_channels:
                if (channel_number < 0) or (channel_number > number_of_channels - 1):
                    print("Selected channel out of bounds")
                    return False
            self.selected_channels_ = selected_channels
            return True
        else:
            print("Testing signal not loaded. Cannot select number of channels")
            return False

    def setSelectedSimTime(self, selected_sim_time):
        """
        Setter for the selected simulation time
        """
        self.selected_sim_time_ = selected_sim_time

    def previewSignal(self):
        """
        Method to plot a preview of the specified signal
        """
        if self.signal_data_.signal_name:
            self.plotSignal(self.signal_data_.signal)
        else:
            print("Testing signal not loaded, cannot preview signals")
            return False

    def generateTestingSignal(self, signal_name, frecuency, amplitude, sample_rate, duration):
        """
        Method to generate the selected signal
        """
        self.resetTestSignalWorker()
        if signal_name == self.testing_signals_[0]:
            self.signal_data_.signal = self.generateSquareSignal(frecuency, amplitude, sample_rate, duration)
        if signal_name == self.testing_signals_[1]:
            self.signal_data_.signal = self.generateSinSignal(frecuency, amplitude, sample_rate, duration)
        if signal_name == self.testing_signals_[2]:
            self.signal_data_.signal = self.generateTriangSignal(frecuency, amplitude, sample_rate, duration)
        self.signal_data_.signal_name = signal_name
        self.signal_data_.frecuency = frecuency
        self.signal_data_.amplitude = amplitude
        self.signal_data_.sample_rate = sample_rate
        self.signal_data_.duration = duration

    def generateSquareSignal(self, frecuency, amplitude, sample_rate, duration):
        """
        Method to generate a square signal
        """
        time = np.arange(0, duration, 1 / sample_rate)
        return amplitude * signal.square(2*np.pi * frecuency * time)

    def generateSinSignal(self, frecuency, amplitude, sample_rate, duration):
        """
        Method to generate a sinusoidal signal
        """
        time = np.arange(0, duration, 1 / sample_rate)
        return amplitude * np.sin(2*np.pi * frecuency * time)

    def generateTriangSignal(self, frecuency, amplitude, sample_rate, duration):
        """
        Method to generate a triangular signal
        """
        time = np.arange(0, duration, 1 / sample_rate)
        return amplitude * signal.sawtooth(2*np.pi * frecuency * time, 0.5)

    def plotSignal(self, signal):
        """
        Method to plot the physical signal to a graph. Plots only the selected channels
        """
        fig, axis = plt.subplots(1)
        start_time = self.selected_sim_time_[0] * int(self.getSampleRate())
        end_time = self.selected_sim_time_[1] * int(self.getSampleRate())
        time = np.arange(0, self.signal_data_.duration, 1 / self.signal_data_.sample_rate)
        axis.plot(time, signal[start_time:end_time], color=(
            [168/255, 193/255, 5/255]), linewidth=0.4)
        axis.set_ylabel("Amplitude [uV]", rotation=0, labelpad=30)
        axis.set_xlabel("Time [sec]", rotation=0, labelpad=30)
        plot_figure_manager = plt.get_current_fig_manager()
        plot_figure_manager.window.showMaximized()
        plt.show()
