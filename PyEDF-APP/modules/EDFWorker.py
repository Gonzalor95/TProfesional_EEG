#!/usr/bin/python

import pyedflib
import numpy as np
import matplotlib.pyplot as plt
from modules.ChannelToIntProtocol import ProtocolDict

"""
Class used to work with the EDF files
"""

DEVICE_MAX_VALUE = 134 # 134uV seems to be the max value we can represent.

# Structure type of class to hold the signal data
class SignalData:
    physical_signals = []  # Used only for previews, as read from the .edf file
    signal_headers = []  # Signal headers, as read from the .edf file
    digital_signals_and_headers = []  # header-signal pair to represent the parsed header and digital signal
    physical_signals_and_headers = []  # header-signal pair to represent the parsed header and physical signal


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
        # Make a copy of the data in case reading fails
        signal_data_copy = self.signal_data_
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
            self.signal_data_ = signal_data_copy
            return False

    def fillSignalData(self, physical_signals, signal_headers, header):
        self.resetWorker()
        self.signal_data_.physical_signals = physical_signals
        self.signal_data_.signal_headers = signal_headers
        self.generateSignalsAndHeaders(physical_signals, signal_headers)

    def generateSignalsAndHeaders(self, physical_signals, signal_headers):
        """
        Method to create the digital signal and header pair
        """
        digital_signals = self.generateDigitalSignals(physical_signals, signal_headers)
        channels = [header["label"] for header in signal_headers]
        clean_channels = self.cleanChannelNames(channels)

        # Create header-signal pair. These will be evaluated to see if they are differential or common mode
        # If they are differential, they will ve converted to common mode
        raw_headers_and_digital_signals = []
        raw_headers_and_physical_signals = []
        for clean_channel, digital_signal in zip(clean_channels, digital_signals):
            raw_headers_and_digital_signals.append((clean_channel, digital_signal))
        for clean_channel, physical_signal in zip(clean_channels, physical_signals):
            raw_headers_and_physical_signals.append((clean_channel, physical_signal))

        self.signal_data_.physical_signals_and_headers = self.parseHeadersAndSignals(raw_headers_and_physical_signals)
        self.signal_data_.digital_signals_and_headers = self.parseHeadersAndSignals(raw_headers_and_digital_signals)

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

    def cleanChannelNames(self, channels):
        """
        Algorithm to remove any unwanted characters from the edf header files
        Add any criteria that we notice to clean headers
        """
        clean_channels = []
        # Remove "EEG" str
        for channel in channels:
            clean_channels.append(channel.replace("EEG", ""))
        return clean_channels

    def parseHeadersAndSignals(self, raw_headers_and_signals):
        """
        Checks the raw headers of the edf file to see if they are in common or bipolar mode
        If they are in bipolar, separates signals
        """
        # Decide if signals are bipolar or common mode
        # If more than half the headers contain a "-", it's a bipolar dataset
        bipolar_mode = False
        count = 0
        for header, _ in raw_headers_and_signals:
            if "-" in header:
                count += 1
        if count > len(raw_headers_and_signals)/2:
            bipolar_mode = True

        clean_headers_and_signals = []
        if bipolar_mode:
            # TODO
            print("Implement this with what Nachi sent")
        else:
            reference_signal_set = False
            for header, signal in raw_headers_and_signals:
                for key in ProtocolDict.possible_channels_array_:
                    all_chars_in_channel = True
                    for char in key:
                        if header.lower().find(char.lower()) == -1:
                            all_chars_in_channel = False
                    if (all_chars_in_channel == True):
                        # Try looking for the alias, else fill with the current name
                        # This avoids using the alias and using our protocol channel name instead
                        try:
                            protocol_channel = ProtocolDict.alias_dict_[key]
                            clean_headers_and_signals.append((protocol_channel, signal))
                        except:
                            clean_headers_and_signals.append((key, signal))
                # Special case for ref channels in common mode datasets if these are present
                if ("a1" in header.lower() or "a2" in header.lower()) and (not reference_signal_set):
                    clean_headers_and_signals.extend(self.handleReferenceSignal(header, signal))
                    reference_signal_set = True
            # If A1 or A2 are not present in the dataset, create a vector of 0s to represent these channels
            if not reference_signal_set:
                clean_headers_and_signals.extend([("A1", np.zeros(len(signal), dtype=np.uint16)), ("A2", np.zeros(len(signal), dtype=np.uint16))])
                reference_signal_set = True
        return clean_headers_and_signals

    def handleReferenceSignal(self, header, signal):
        """
        Method used to parse the A1-A2 signal present in some datasets that use common mode
        """
        header.replace(" ", "")  # Remove spaces if any
        # Parse both channels, should be A1 and A2
        channels = header.split("-")
        channel1 = channels[0]
        channel2 = channels[1]

        # TODO: Temporarily fill A1 and A2 channels with a 0s to match the other signals and use as reference
        channel1 = np.zeros(len(signal))
        channel2 = np.zeros(len(signal))
        return [("A1", channel1), ("A2", channel2)]

        # TODO: Get the actual values of A1 and A2 if present. This would replace the above TODO
        # # Now we should get the signal
        # import mne
        # # Load the bipolar signals from file
        # bipolar_data = mne.io.read_raw_edf('bipolar_signals.edf', preload=True)
        # # Re-reference to a common average reference
        # common_avg = bipolar_data.get_data().mean(axis=0)
        # data_reavg = bipolar_data.copy().apply_function(lambda x: x - common_avg)
        # # Convert to monopolar signals
        # data_mono = data_reavg.copy().apply_function(lambda x: x[0] - x[1])
        # # Save the monopolar signals to file
        # mne.io.write_raw_edf(data_mono, 'unipolar_signals.edf')

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
        channels = []
        for header, _ in self.signal_data_.physical_signals_and_headers:
            channels.append(header)
        return channels

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
        start_time = self.selected_sim_time_[0]*int(self.getSampleRate())
        end_time = self.selected_sim_time_[1]*int(self.getSampleRate())

        signals_to_print = []
        # Get the header-signal pairs to print
        for channel in self.selected_channels_:
            for header, signal in self.signal_data_.physical_signals_and_headers:
                if (header == channel):
                    signals_to_print.append((header, signal))

        for index in range(len(self.selected_channels_)):
            header, signal = signals_to_print[index]
            # Plot
            axis[index][0].plot(signal, color=([168/255, 193/255, 5/255]), linewidth=0.4)
            # Hide axis values
            axis[index][0].get_xaxis().set_ticks([])
            # axis[index][0].get_yaxis().set_ticks([])
            # Set plot title
            axis[index][0].set_ylabel(header, rotation=0, labelpad=30)
            # Adjust axis range to better fit the signal
            axis[index][0].set_xlim([0, end_time - start_time])
        plot_figure_manager = plt.get_current_fig_manager()
        plot_figure_manager.window.showMaximized()
        plt.show()

    def getSimulationSignals(self):
        """
        Gets an array of header/signals pair that will be sent to the generator
        """
        signals_to_send = []
        for channel in self.selected_channels_:
            for pair in self.signal_data_.digital_signals_and_headers:
                if channel == pair[0]:
                    signals_to_send.append(pair)

        # Pre-processing of the edf signal
        # 1. Make it go from (-edf_digital_min, edf_digital_max) to (0, our_digital_max)
        # 2. Normalize it to our (digital_max, physical_max) ratio instead of the one present in the edf
        processed_signal_to_send = []
        digital_min = self.signal_data_.signal_headers[0]["digital_min"]
        digital_max = self.signal_data_.signal_headers[0]["digital_max"]
        for header,signal in signals_to_send:
            processed_signal = (signal - digital_min)
            processed_signal = processed_signal * DEVICE_MAX_VALUE / (digital_max - digital_min)

            processed_signal_to_send.append((header, processed_signal))

        return processed_signal_to_send
