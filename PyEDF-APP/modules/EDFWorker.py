#!/usr/bin/python

import pyedflib
import numpy as np
import matplotlib.pyplot as plt
from modules.ChannelToIntProtocol import ProtocolDict

"""
Class used to work with the EDF files
"""


# Structure tipe of class to hold the signal data
# Array lenghts should all be the same
class SignalData:
    physical_signals = []  # Used only for previews
    signal_headers = []  # Signal headers as read from the .edf file
    digital_signals = []
    # Parsed channel names, may not be the same as the ones present in the signal headers
    channel_names = []


class EDFWorker():
    # Class variables
    # Flag to state if an EDF file is loaded in the system or not
    file_loaded_ = False
    # Selected simulation channels in EEG standard
    selected_channels_ = []
    # Selected simulation time
    selected_sim_time_ = ()
    # Data structure to hold the .edf data
    signal_data_ = SignalData()

    def __init__(self):
        print("EDF Worker initialized")

    def resetWorker(self):
        """
        Method to reset the worker and return to it's default values
        """
        self.file_loaded_ = False
        self.selected_channels_ = []
        self.selected_sim_time_ = ()
        self.digital_signals_generated_ = False
        self.signal_data_ = SignalData()

    def readEDF(self, file_full_path):
        """
        Method to read an EDF file
        param[in]: "file_full_path" The full path to the EDF file
        returns: True if it was successful, false otherwise
        """
        try:
            physical_signals, signal_headers, header = pyedflib.highlevel.read_edf(file_full_path, verbose=True)
            self.fillSignalData(physical_signals, signal_headers, header)
            # Set the simulation time
            self.selected_sim_time_ = (int(0), int(self.getDuration()))
            # Set the selected channels to all
            self.selected_channels_ = self.getChannels()
            self.file_loaded_ = True
            return True
        except:
            return False

    def fillSignalData(self, physical_signals, signal_headers, header):
        self.resetWorker()
        self.signal_data_.physical_signals = physical_signals
        self.signal_data_.signal_headers = signal_headers
        self.signal_data_.channel_names = self.parseChannelsNames(
            signal_headers)
        self.signal_data_.digital_signals = self.generateDigitalSignals(
            physical_signals, signal_headers)

    def parseChannelsNames(self, signal_headers):
        channels = [header["label"] for header in signal_headers]
        parsed_channels = []
        for key in ProtocolDict.channel_enum_dict_.keys():
            for channel in channels:
                all_chars_in_channel = True
                for char in key:
                    if channel.lower().find(char.lower()) == -1:
                        all_chars_in_channel = False
                if (all_chars_in_channel == True) and (key not in parsed_channels):
                    parsed_channels.append(key)
        return parsed_channels

    def generateDigitalSignals(self, physical_signals, signal_headers):
        """
        Method to generate the digital signals from the physical ones
        """
        digital_signals = np.empty([1, len(physical_signals[1])])
        for i in range(physical_signals.shape[0]):
            # Iterate backwards to get the correct order when stacking
            digital_signal = pyedflib.highlevel.phys2dig(physical_signals[-1-i], signal_headers[-1 - i]["digital_min"],
                                                         signal_headers[-1 - i]["digital_max"], signal_headers[-1 - i]["physical_min"], signal_headers[-1 - i]["physical_max"])
            digital_signals = np.vstack((digital_signals, digital_signal))
        # Re-arrange the rows because they got disordered when stacking
        for i in range(int(physical_signals.shape[0] / 2)):
            digital_signals[[i, -1-i]] = digital_signals[[-1-i, i]]
        return digital_signals

    def isFileLoaded(self):
        """
        Method to know if a file was loaded into the worker or not
        """
        return self.file_loaded_

    def getNumberOfChannels(self):
        """
        Getter for the number of channels in the file
        """
        return self.signal_data_.physical_signals.shape[0]

    def getSampleRate(self):
        """
        Getter for the signal sample rate
        """
        return self.signal_data_.signal_headers[0]["sample_rate"]

    def getSignalDimension(self):
        """
        Getter for the signal unit dimension
        """
        return self.signal_data_.signal_headers[0]["dimension"]

    def getChannels(self):
        """
        Getter for the channels of the EDF file
        """
        return self.signal_data_.channel_names

    def setSelectedChannels(self, selected_channels):
        """
        Setter for the selected channels to simulate
        """
        self.selected_channels_ = selected_channels

    def getDuration(self):
        """
        Getter for the measurement duration in seconds
        """
        return int(int(self.signal_data_.physical_signals.shape[1]) / int(self.getSampleRate()))

    def getSelectedSimTime(self):
        """
        Getter for the selected simulation time
        """
        return self.selected_sim_time_

    def setSelectedSimTime(self, selected_sim_time):
        """
        Setter for the selected simulation time
        """
        self.selected_sim_time_ = selected_sim_time

    def getSignalInfo(self):
        """
        Returns a dictionary with the signal information:
        Currently returns: Number of channels, dimension, sample_rate and duration.
        """
        signal_info_dict = {}
        signal_info_dict["Sample rate"] = self.getSampleRate()
        signal_info_dict["Dimension"] = self.getSignalDimension()
        signal_info_dict["Number of channels"] = self.getNumberOfChannels()
        signal_info_dict["Duration [s]"] = self.getDuration()
        return signal_info_dict

    def previewSignals(self):
        """
        Method to plot a preview of the physical signal
        """
        if (self.file_loaded_):
            self.plotSignals(self.signal_data_.physical_signals)
            return True
        else:
            print("EDF file not loaded, cannot preview signals")
            return False

    def plotSignals(self, signal):
        """
        Method to plot the physical signal to a graph. Plots only the selected channels
        """
        _, axis = plt.subplots(len(self.selected_channels_), squeeze=False)
        for index in range(len(self.selected_channels_)):
            start_time = self.selected_sim_time_[0]*int(self.getSampleRate())
            end_time = self.selected_sim_time_[1]*int(self.getSampleRate())

            # Get where that channel is in the array
            signal_index = self.signal_data_.channel_names.index(self.selected_channels_[index])
            # Get the piece of signal to plot
            signal_to_print = signal[signal_index][start_time:end_time]
            # Plot
            axis[index][0].plot(signal_to_print, color=([168/255, 193/255, 5/255]), linewidth=0.4)
            # Hide axis values
            axis[index][0].get_xaxis().set_ticks([])
            # axis[index][0].get_yaxis().set_ticks([])
            # Set plot title
            axis[index][0].set_ylabel(self.signal_data_.channel_names[signal_index], rotation=0, labelpad=30)
            # Adjust axis range to better fit the signal
            axis[index][0].set_xlim([0, end_time - start_time])
        plot_figure_manager = plt.get_current_fig_manager()
        plot_figure_manager.window.showMaximized()
        plt.show()
