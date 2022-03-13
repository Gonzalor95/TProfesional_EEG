#!/usr/bin/python

from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

"""
Class to handle the testing signals
"""


class TestingSignalsWorker():
    # List with all the channels selected for the simulator
    selected_channels_ = []
    # Selected simulation time
    selected_sim_time_ = ()
    # Selected testing signal. If empty, no current testing signal is selected
    selected_testing_signal_ = ""
    # Possible testing signals
    testing_signals_ = ["Square", "Sinusoidal", "Triangular"]

    def __init__(self, max_channels):
        self.max_channels_ = max_channels
        self.selected_channels_ = range(max_channels)
        self.duration_ = 100  # Max duration in seconds
        self.amplitud_ = 1
        self.frecuency_ = 100  # In Hz
        self.sample_rate_ = 1000
        self.selected_sim_time_ = (0, self.duration_)
        print("Testing signals worker initialized")

    def listTestingSignals(self):
        """
        Method to create a list of all corresponding testing signals
        """
        return self.testing_signals_

    def getSignalInfo(self):
        """
        Returns a dictionary with the signal information:
        Currently returns: Number of channels, dimension, sample_rate.
        """
        signal_info_dict = {}
        signal_info_dict["Dimension"] = self.getSignalDimension()
        signal_info_dict["Number of channels"] = self.getNumberOfChannels()
        signal_info_dict["Duration [s]"] = self.getDuration()
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
        return self.duration_

    def getSignalDimension(self):
        """
        Getter for the signal unit dimension
        """
        return "uV"

    def getAmplitud(self):
        """
        Getter for the testing signal amplitud
        """
        return self.amplitud_

    def getFrecuency(self):
        """
        Getter for the testing signal frecuency
        """
        return self.frecuency_

    def getSampleRate(self):
        """
        Getter for the testing signal sample rate
        """
        return self.sample_rate_

    def selectTestingSignal(self, selected_signal):
        """
        TODO
        """
        self.resetTestSignalWorker()
        self.generateSignal(selected_signal)
        self.selected_testing_signal_ = selected_signal

    def resetTestSignalWorker(self):
        """
        TODO
        """
        self.selected_testing_signal_ = ""

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
        if self.selected_testing_signal_:
            self.plotSignal(self.signal_)
        else:
            print("Testing signal not loaded, cannot preview signals")
            return False

    def generateSignal(self, selected_signal):
        """
        Method to generate the selected signal
        """
        if selected_signal == self.testing_signals_[0]:
            self.signal_ = self.generateSquareSignal()
        if selected_signal == self.testing_signals_[1]:
            self.signal_ = self.generateSinSignal()
        # if selected_signal == self.testing_signals_[2]:
        #     self.signal_ = self.generateTriangSignal()

    def generateSquareSignal(self):
        """
        Method to generate a square signal
        """
        # Sampling rate 1000 hz / second
        t = np.linspace(0, self.duration_, self.getSampleRate(), endpoint=True)
        squarewave = signal.square(2 * np.pi * 5 * t)

        # Sampling rate 1000 hz / second
        t = np.linspace(0, 1, 1000, endpoint=True)
        # Plot the square wave signal
        plt.plot(t, signal.square(2 * np.pi * 5 * t))
        # Give a title for the square wave plot
        plt.title('Sqaure wave - 5 Hz sampled at 1000 Hz /second')
        # Give x axis label for the square wave plot
        plt.xlabel('Time')
        # Give y axis label for the square wave plot
        plt.ylabel('Amplitude')
        plt.grid(True, which='both')
        # Provide x axis and line color
        plt.axhline(y=0, color='k')
        # Set the max and min values for y axis
        plt.ylim(-2, 2)
        # Display the square wave drawn
        plt.show()

        return squarewave

    def generateSinSignal(self):
        """
        Method to generate a sinusoidal signal
        """
        time = np.arange(0, self.duration_, 1/self.getSampleRate())
        sinewave = self.getAmplitud() * np.sin(self.getFrecuency() * time)
        return sinewave

    # def generateTriangSignal(self):
    #     """
    #     Method to generate a triangular signal
    #     """

    def plotSignal(self, signal):
        """
        Method to plot the physical signal to a graph. Plots only the selected channels
        """
        fig, axis = plt.subplots(1)
        start_time = self.selected_sim_time_[0]*int(self.getSampleRate())
        end_time = self.selected_sim_time_[1]*int(self.getSampleRate())
        axis.plot(signal[start_time:end_time], color=(
            [168/255, 193/255, 5/255]), linewidth=0.4)
        # Hide axis values
        axis.set_yticklabels([])
        axis.set_xticklabels([])
        # Adjust axis range to better fit the signal
        axis.set_xlim(
            [0, end_time - start_time])
        plot_figure_manager = plt.get_current_fig_manager()
        plot_figure_manager.window.showMaximized()
        plt.show()
