#!/usr/bin/python

from numpy.core.records import array
import pyedflib
import numpy as np
import matplotlib.pyplot as plt


class EDFWorker():
    # Class variables
    # Flag to state if an EDF file is loaded in the system or not
    file_loaded = False
    # List with all the channels selected for the simulator
    selected_channels = []

    def _init_(self):
        print("EDF Worker initialized")

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

    def getSignalInfo(self):
        """
        Returns a dictionary with the signal information:
        Currently returns: Number of channels, dimension, sample_rate.
        """
        signal_info_dict = {}
        signal_info_dict["sample_rate"] = self.getSampleRate()
        signal_info_dict["dimension"] = self.getSignalDimension()
        signal_info_dict["number_of_channels"] = self.getNumberOfChannels()
        return signal_info_dict

    def setSelectedChannels(self, selected_channels):
        """
        Method to set the selected channels array

        param[in]: "selected_channels" Array of integers with the selected channels
        """
        number_of_channels = self.getNumberOfChannels()
        # Check the size of the input array
        if len(selected_channels) < 0 or len(selected_channels) > number_of_channels:
            print ("Invalid amount of selected channels")
            return False
        # Check that all channels are valid
        for channel_number in selected_channels:
            if (channel_number < 0) or (channel_number > number_of_channels - 1):
                print ("Selected channel out of bounds")
                return False
        else:
            self.selected_channels = selected_channels
            return True

    def generateDigitalSignals(self):
        """
        Method to generate the digital signals from the physical ones
        """
        self.digital_signals = np.empty([1, self.physical_signals[1]])
        for i in range(self.physical_signals.shape[0]):
            digital_signal = self.physicalToDigital(self.physical_signals[i],
                                                    self.signal_headers[i]["digital_min"],
                                                    self.signal_headers[i]["digital_max"],
                                                    self.signal_headers[i]["physical_min"],
                                                    self.signal_headers[i]["physical_max"])
            self.digital_signals = np.vstack(
                (self.digital_signals, digital_signal))

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
            self.selected_channels.clear()
            # As a default when reading a file, select all channels
            for signal_index in range(len(self.signal_headers)):
                self.selected_channels.append(signal_index)
            self.file_loaded = True
            return True
        except:
            return False

    def previewSignals(self):
        """
        Method to plot a preview of the selected signal channels for the user to view
        """
        if (self.file_loaded):
            _, axis = plt.subplots(len(self.selected_channels))
            for index in range(len(self.selected_channels)):
                axis[index].plot(self.physical_signals[self.selected_channels[index]], color=(
                    [168/255, 193/255, 5/255]), linewidth=0.2)
                # Hide axis values
                axis[index].get_xaxis().set_ticks([])
                axis[index].get_yaxis().set_ticks([])
                axis[index].set_title(
                    "Channel " + str(self.selected_channels[index]))
            # Make it fullscreen # TODO: check that maxsize() does not work on windows
            #plot_figure_manager = plt.get_current_fig_manager()
            #plot_figure_manager.resize(*plot_figure_manager.window.maxsize())
            plt.show()
        else:
            print("EDF file not loaded, cannot preview signals")
            return False

    def physicalToDigital(self, signal, dmin, dmax, pmin, pmax):
        m = (pmax-pmin) / (dmax/dmin)
        b = pmax / m - dmax
        digital = signal/m - b
        return digital
