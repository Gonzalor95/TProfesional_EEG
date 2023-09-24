#!/usr/bin/python

from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from modules.ChannelToIntProtocol import ProtocolDict
from modules.utils import generate_sinusoidal_waves_matching_time


class SignalData:
    """
    Structure type of class to hold the signal data

    Array lenghts should all be the same
    """
    signal_name = ""  # ["Square", "Sinusoidal", "Triangular"]
    physical_signal = []
    digital_signal = []
    frecuency = 0
    sample_rate = 0
    amplitude = 0
    duration = 0


class TestingSignalsWorker():
    """
    Class to handle the testing signals
    """
    # List with all the channels selected for the simulator
    selected_channels_ = []
    # Selected simulation time
    selected_sim_time_ = ()
    # Possible testing signals
    testing_signals_ = ["Square", "Sinusoidal", "Triangular"]

    def __init__(self, config):
        self.config_params_ = config
        self.selected_channels_ = range(self.config_params_["max_channels"])
        self.selected_sim_time_ = ()
        self.signal_data_ = SignalData()
        print("Testing signals worker initialized")

    def getSignalInfo(self):
        """
        Returns a dictionary with the testing signal information
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
        Getter for the number of channels
        """
        return len(self.selected_channels_)

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

        param[in]: "selected_channels" Array with the selected channels
        """
        self.selected_channels_ = selected_channels

    def getChannels(self):
        """
        TODO
        """
        return ProtocolDict.channel_enum_dict_.keys()

    def setSelectedSimTime(self, selected_sim_time):
        """
        Setter for the selected simulation time
        """
        # Re-generate signal if selected time is longer than original
        if selected_sim_time[1] > self.signal_data_.duration:
            self.generateTestingSignal(self.signal_data_.signal_name, self.signal_data_.frecuency, self.signal_data_.amplitude,
                                       self.signal_data_.sample_rate, selected_sim_time[1])
        self.selected_sim_time_ = selected_sim_time

    def generateTestingSignal(self, signal_name, frecuency, amplitude, sample_rate, duration):
        """
        Method to generate the selected signal
        """
        self.resetTestSignalWorker()
        if signal_name == self.testing_signals_[0]:
            self.signal_data_.physical_signal = self.generateSquareSignal_(frecuency, amplitude, sample_rate, duration)
        if signal_name == self.testing_signals_[1]:
            self.signal_data_.physical_signal = self.generateSinSignal_(frecuency, amplitude, sample_rate, duration)
        if signal_name == self.testing_signals_[2]:
            self.signal_data_.physical_signal = self.generateTriangSignal_(frecuency, amplitude, sample_rate, duration)
        self.createDigitalSignal_()
        self.signal_data_.signal_name = signal_name
        self.signal_data_.frecuency = frecuency
        self.signal_data_.amplitude = amplitude
        self.signal_data_.sample_rate = sample_rate
        self.signal_data_.duration = duration
        selected_channels = []
        for channel in ProtocolDict.channel_enum_dict_.keys():
            selected_channels.append(channel)
        self.selected_channels_ = selected_channels # Select all channels

    def previewSignal(self):
        """
        Method to plot a preview of the specified signal

        Callback method for the GUI interface
        """
        if self.signal_data_.signal_name:
            self.plotSignal_(self.signal_data_.physical_signal)
        else:
            print("Testing signal not loaded, cannot preview signals")
            return False

    def getSimulationSignals(self):
        """
        Gets an array of header/signals pair that will be sent to the generator
        """
        signals_to_send = []
        start_point = self.selected_sim_time_[0] * int(self.getSampleRate())
        end_point = self.selected_sim_time_[1] * int(self.getSampleRate())
        for channel in self.selected_channels_:
            signals_to_send.append((channel, self.signal_data_.digital_signal[start_point:end_point]))
        return signals_to_send

    ###### Private ######

    def generateSquareSignal_(self, frecuency, amplitude, sample_rate, duration):
        """
        Method to generate a square signal
        """
        time = np.arange(0, duration, 1 / sample_rate)
        return amplitude * signal.square(2*np.pi * frecuency * time)

    def generateSinSignal_(self, frecuency, amplitude, sample_rate, duration):
        """
        Method to generate a sinusoidal signal
        """
        time = np.arange(0, duration, 1 / sample_rate)
        return amplitude * np.sin(2*np.pi * frecuency * time)

    def generateTriangSignal_(self, frecuency, amplitude, sample_rate, duration):
        """
        Method to generate a triangular signal
        """
        time = np.arange(0, duration, 1 / sample_rate)

        ## Triangular
        #output = amplitude * signal.sawtooth(2*np.pi * frecuency * time, 0.5)

        #Resp en frequencia:
        frequencies = [0.1, 0.2, 0.5, 0.8, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 50, 100]
        
        duration = 5
        t, output = generate_sinusoidal_waves_matching_time(amplitude = amplitude, duration = duration, frequencies = frequencies, sample_rate = sample_rate)
        
        return output
        

    def createDigitalSignal_(self):
        """
        Creates the digital signal from the physical one. Uses device parameters to make this convertion
        """
        m = (self.config_params_["max_physical"] - ( -self.config_params_["max_physical"] )) / (self.config_params_["max_digital"]-(0))
        b = self.config_params_["max_physical"] / m - self.config_params_["max_digital"]
        digital = self.signal_data_.physical_signal / m - b

        #self.signal_data_.digital_signal = digital
        #XXX: Gonza - Aplico la antitransformada de Divisor + Rail-to-Rail
        digital = ((self.signal_data_.physical_signal * 0.0125) +2.5) * (65536/5)
        self.signal_data_.digital_signal = digital


        

    def plotSignal_(self, signal):
        """
        Method to plot the physical signal to a graph. Shows only one channel as it will be the same for all
        """
        fig, axis = plt.subplots(1)
        start_point = self.selected_sim_time_[0] * int(self.getSampleRate())
        end_point = self.selected_sim_time_[1] * int(self.getSampleRate())
        time = np.arange(self.selected_sim_time_[0], self.selected_sim_time_[1], 1 / self.signal_data_.sample_rate)
        axis.plot(time, signal[start_point:end_point], color=(
            [168/255, 193/255, 5/255]), linewidth=0.4)
        axis.set_ylabel("Amplitude [uV]", rotation=0, labelpad=30)
        axis.set_xlabel("Time [sec]", rotation=0, labelpad=30)
        plot_figure_manager = plt.get_current_fig_manager()
        plot_figure_manager.window.showMaximized()
        plt.show()
