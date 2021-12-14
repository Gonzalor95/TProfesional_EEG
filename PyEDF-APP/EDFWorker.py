#!/usr/bin/python

from numpy.core.records import array
import pyedflib
import numpy as np
import matplotlib.pyplot as plt


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

    def _init_(self):
        print("EDF Worker initialized")

    def isFileLoaded(self):
        """
        Method to know if a file was loaded into the worker or not
        """
        return self.file_loaded_

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

    def getDuration(self):
        """
        Getter for the measurement duration in seconds
        """
        return self.physical_signals.shape[1] / self.getSampleRate()

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

    def generateDigitalSignals(self): #TODO: When stacking, channels get disorder
        """
        Method to generate the digital signals from the physical ones
        """
        if not self.digital_signals_generated_:
            self.digital_signals = np.empty([1, len(self.physical_signals[1])])
            for i in range(self.physical_signals.shape[0]):
                digital_signal = pyedflib.highlevel.phys2dig(self.physical_signals[i],
                                                             self.signal_headers[i]["digital_min"],
                                                             self.signal_headers[i]["digital_max"],
                                                             self.signal_headers[i]["physical_min"],
                                                             self.signal_headers[i]["physical_max"])
                self.digital_signals = np.vstack(
                    (self.digital_signals, digital_signal))
            self.digital_signals_generated_ = True

    def plotSignals(self, signal):
        _, axis = plt.subplots(len(self.selected_channels_), squeeze=False)
        for index in range(len(self.selected_channels_)):
            signal_to_print = signal[self.selected_channels_[
                index]][self.selected_sim_time_[0]:self.selected_sim_time_[1]]
            axis[index][0].plot(signal_to_print, color=(
                [168/255, 193/255, 5/255]), linewidth=0.4)
            # Hide axis values
            axis[index][0].get_xaxis().set_ticks([])
            axis[index][0].get_yaxis().set_ticks([])
            # Set plot title
            axis[index][0].set_ylabel(
                "Channel " + str(self.selected_channels_[index]), rotation=0, labelpad=30)
            # Adjust axis range to better fit the signal
            axis[index][0].set_xlim(
                [0, self.selected_sim_time_[1] - self.selected_sim_time_[0]])
        # Make it fullscreen # TODO: check that maxsize() does not work on windows
        plot_figure_manager = plt.get_current_fig_manager()
        plot_figure_manager.resize(
            *plot_figure_manager.window.maxsize())
        plt.show()
