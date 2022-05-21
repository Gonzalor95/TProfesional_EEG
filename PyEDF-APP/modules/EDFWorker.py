#!/usr/bin/python

import pyedflib
import numpy as np
import matplotlib.pyplot as plt

"""
Class used to work with the EDF files
"""


class EDFWorker():
    # Class variables
    # Flag to state if an EDF file is loaded in the system or not
    file_loaded_ = False
    # List with all the channels selected for the simulator
    selected_channels_ = []
    # Selected simulation time
    selected_sim_time_ = ()
    # Flag to indicate if digital signals were generated or not
    digital_signals_generated_ = False

    def __init__(self):
        print("EDF Worker initialized")

    def isFileLoaded(self):
        """
        Method to know if a file was loaded into the worker or not
        """
        return self.file_loaded_

    def resetWorker(self):
        """
        Method to reset the worker and return to it's default values
        """
        self.file_loaded_ = False
        self.selected_channels_ = []
        self.selected_sim_time_ = ()
        self.digital_signals_generated_ = False

    def getSelectedSimTime(self):
        """
        Getter for the selected simulation time
        """
        return self.selected_sim_time_

    def getSampleRate(self):
        """
        Getter for the signal sample rate
        """
        return self.signal_headers[0]["sample_rate"]

    def getSignalDimension(self):
        """
        Getter for the signal unit dimension
        """
        return self.signal_headers[0]["dimension"]

    def getNumberOfChannels(self):
        """
        Getter for the number of channels in the file
        """
        return self.physical_signals.shape[0]

    def getChannels(self):
        """
        Getter for the channels of the EDF file
        """
        if self.file_loaded_:
            channels_list = [header["label"] for header in self.signal_headers]
            print(channels_list)
            return channels_list
        else:
            print("File not loaded. Cannot get channels")
            return []

    def getDuration(self):
        """
        Getter for the measurement duration in seconds
        """
        return int(int(self.physical_signals.shape[1]) / int(self.getSampleRate()))

    def getSignalInfo(self):
        """
        Returns a dictionary with the signal information:
        Currently returns: Number of channels, dimension, sample_rate.
        """
        signal_info_dict = {}
        signal_info_dict["Sample rate"] = self.getSampleRate()
        signal_info_dict["Dimension"] = self.getSignalDimension()
        signal_info_dict["Number of channels"] = self.getNumberOfChannels()
        signal_info_dict["Duration [s]"] = self.getDuration()
        return signal_info_dict

    def setSelectedChannels(self, selected_channels):
        """
        Method to set the selected channels array
        param[in]: "selected_channels" Array of integers with the selected channels
        """
        if self.file_loaded_:
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
            print("File not loaded. Cannot select number of channels")
            return False

    def setSelectedSimTime(self, selected_sim_time):
        """
        Setter for the selected simulation time
        """
        self.selected_sim_time_ = selected_sim_time

    def readEDF(self, file_full_path):
        """
        Method to read an EDF file
        param[in]: "file_full_path" The full path to the EDF file
        returns: True if it was successful, false otherwise
        """
        try:
            self.physical_signals, self.signal_headers, self.headers = pyedflib.highlevel.read_edf(
                file_full_path, verbose=True)
            # Clear selected channels upon reading a new file
            self.selected_channels_.clear()
            # As a default when reading a file, select all channels
            for signal_index in range(len(self.signal_headers)):
                self.selected_channels_.append(signal_index)
            # Set the simulation time
            self.selected_sim_time_ = (int(0), int(self.getDuration()))
            self.file_loaded_ = True
            return True
        except:
            return False

    def previewSignals(self, signal_type):
        """
        Method to plot a preview of the specified signal
        """
        if (self.file_loaded_):
            if signal_type == "digital":
                self.generateDigitalSignals()
                self.plotSignals(self.digital_signals)
                return True
            elif signal_type == "physical":
                self.plotSignals(self.physical_signals)
                return True
            else:
                print("Incorrect type of signal specified to the preview method")
                return False
        else:
            print("EDF file not loaded, cannot preview signals")
            return False

    def generateDigitalSignals(self):
        """
        Method to generate the digital signals from the physical ones
        """
        if not self.digital_signals_generated_:
            self.digital_signals = np.empty([1, len(self.physical_signals[1])])
            for i in range(self.physical_signals.shape[0]):
                # Iterate backwards to get the correct order when stacking
                digital_signal = pyedflib.highlevel.phys2dig(self.physical_signals[-1-i],
                                                             self.signal_headers[-1 -
                                                                                 i]["digital_min"],
                                                             self.signal_headers[-1 -
                                                                                 i]["digital_max"],
                                                             self.signal_headers[-1 -
                                                                                 i]["physical_min"],
                                                             self.signal_headers[-1-i]["physical_max"])
                self.digital_signals = np.vstack(
                    (self.digital_signals, digital_signal))
            # Re-arrange the rows because they got disordered when stacking
            for i in range(int(self.physical_signals.shape[0] / 2)):
                self.digital_signals[[i, -1-i]
                                     ] = self.digital_signals[[-1-i, i]]
            self.digital_signals_generated_ = True

    def plotSignals(self, signal):
        """
        Method to plot the physical signal to a graph. Plots only the selected channels
        """
        _, axis = plt.subplots(len(self.selected_channels_), squeeze=False)
        for index in range(len(self.selected_channels_)):
            start_time = self.selected_sim_time_[0]*int(self.getSampleRate())
            end_time = self.selected_sim_time_[1]*int(self.getSampleRate())
            signal_to_print = signal[self.selected_channels_[
                index]][start_time:end_time]
            axis[index][0].plot(signal_to_print, color=(
                [168/255, 193/255, 5/255]), linewidth=0.4)
            # Hide axis values
            axis[index][0].get_xaxis().set_ticks([])
            axis[index][0].get_yaxis().set_ticks([])
            # Set plot title
            axis[index][0].set_ylabel(
                self.signal_headers[self.selected_channels_[index]]["label"], rotation=0, labelpad=30)
            # Adjust axis range to better fit the signal
            axis[index][0].set_xlim(
                [0, end_time - start_time])
        plot_figure_manager = plt.get_current_fig_manager()
        plot_figure_manager.window.showMaximized()
        plt.show()
