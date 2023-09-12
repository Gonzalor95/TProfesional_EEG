#!/usr/bin/python

import pyedflib
import numpy as np
import matplotlib.pyplot as plt
from modules.ChannelToIntProtocol import ProtocolDict





#################### INVERSE FILTER

from scipy.signal import butter, iirnotch, filtfilt, sosfiltfilt

#CALL:
#signal_inverse_filter = inverse_filter(data = signal, stopband = [0.8, 30], fs = sampling_rate)
def inverse_filter(data = [], stopband = [0.8, 30], fs = 1):

    sos = butter(N = 1, Wn = stopband, fs = fs, btype = 'bandstop', analog = False, output='sos')
    bw = stopband[1] - stopband[0] # =  29.2
    w0 = stopband[0] + (stopband[1] - stopband[0])/2 # 0.8 + ( 14.6 ) = 15.4

    Q = w0/bw 
    b, a = iirnotch(w0 = w0, Q = Q, fs=fs)

    gain = 1.41 # 3db

    data = data * gain
    #y = filtfilt(b, a, data) # Notch
    y = sosfiltfilt(sos, data) # Butter bandstop

    return y
##########################

class SignalData:
    """
    Structure type of class to hold the signal data
    """
    physical_signals = []  # Used only for previews, as read from the .edf file
    signal_headers = []  # Signal headers, as read from the .edf file
    digital_signals_and_channels = []  # channel-signal pairs to represent the parsed channel and digital signal
    physical_signals_and_channels = []  # channel-signal pairs to represent the parsed channel and physical signal


class EDFWorker():
    """
    Class used to work with the EDF files
    """
    # Class variables
    # Flag to state if an EDF file is loaded in the system or not
    file_loaded_ = False
    # Selected simulation channels in EEG standard
    selected_channels_ = []
    # Selected simulation time
    selected_sim_time_ = ()
    # Data structure to hold the .edf data
    signal_data_ = SignalData()

    def __init__(self, config):
        self.config_params_ = config
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
            self.fillSignalData_(physical_signals, signal_headers)
            # Set the simulation time
            self.selected_sim_time_ = (int(0), int(self.getDuration()))
            # Set the selected channels to all
            self.selected_channels_ = self.getChannels()
            self.file_loaded_ = True
            return True
        except:
            self.signal_data_ = signal_data_copy
            return False

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
        for header, _ in self.signal_data_.physical_signals_and_channels:
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
            self.plotSignals_(self.signal_data_.physical_signals)
            return True
        else:
            print("EDF file not loaded, cannot preview signals")
            return False

    def getSimulationSignals(self):
        """
        Gets an array of header/signals pair that will be sent to the generator
        """
        signals_to_send = []
        for channel in self.selected_channels_:
            for pair in self.signal_data_.physical_signals_and_channels:
                if channel == pair[0]:
                    signals_to_send.append(pair)

        # Pre-processing of the edf signal
        # 1. Make it go from (-edf_physical_min, edf_physical_max) to (0, our_digital_max)
        processed_signal_to_send = []

        start_point = self.selected_sim_time_[0] * int(self.getSampleRate())
        end_point = self.selected_sim_time_[1] * int(self.getSampleRate())
        for header,signal in signals_to_send:
            m = (self.config_params_["max_physical"] - self.config_params_["min_physical"]) / self.config_params_["max_digital"]
            b = self.config_params_["max_physical"] / m - self.config_params_["max_digital"]
            processed_signal = signal / m - b

            #self.signal_data_.digital_signal = digital
            #XXX: Gonza - Aplico la antitransformada de Divisor + Rail-to-Rail.
            # creo que le falta un * 2
            processed_signal = ((signal * 0.0125) +2.5) * (65536/5)
            #processed_signal = inverse_filter(data = processed_signal, stopband = [0.8, 30], fs = self.getSampleRate())

            processed_signal_to_send.append((header, processed_signal[start_point:end_point]))

        return processed_signal_to_send

    ###### Private ######

    def fillSignalData_(self, physical_signals, signal_headers):
        self.resetWorker()
        self.signal_data_.physical_signals = physical_signals
        self.signal_data_.signal_headers = signal_headers
        self.generateSignalsAndHeaders_(physical_signals, signal_headers)

    def generateSignalsAndHeaders_(self, physical_signals, signal_headers):
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

        self.signal_data_.physical_signals_and_channels = self.parseHeadersAndSignals_(raw_headers_and_physical_signals)
        self.signal_data_.digital_signals_and_channels = self.parseHeadersAndSignals_(raw_headers_and_digital_signals)


    def parseHeadersAndSignals_(self, raw_headers_and_signals):
        """
        Method to build the channel-signal pair to fill in the SignalData structure
        """
        clean_headers_and_signals = []
        if self.areSignalsBipolar_(raw_headers_and_signals):
            # TODO
            print("Implement this? -> Probably not possible")
            raise Exception("EDF file is in bipolar mode")
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
                    clean_headers_and_signals.extend(self.handleReferenceSignal_(header, signal))
                    reference_signal_set = True
            # If A1 or A2 are not present in the dataset, create a vector of 0s to represent these channels
            if not reference_signal_set:
                clean_headers_and_signals.extend([("A1", np.zeros(len(signal), dtype=np.uint16)), ("A2", np.zeros(len(signal), dtype=np.uint16))])
                reference_signal_set = True
        return clean_headers_and_signals

    def areSignalsBipolar_(self, raw_headers_and_signals):
        """
        Method to check if the loaded signals from the edf file are in bipolar mode
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
        return bipolar_mode

    def plotSignals_(self, signal):
        """
        Method to plot the physical signal to a graph. Plots only the selected channels
        """
        _, axis = plt.subplots(len(self.selected_channels_), squeeze=False)
        start_point = self.selected_sim_time_[0]*int(self.getSampleRate())
        end_point = self.selected_sim_time_[1]*int(self.getSampleRate())

        signals_to_print = []
        # Get the header-signal pairs to print
        for channel in self.selected_channels_:
            for header, signal in self.signal_data_.physical_signals_and_channels:
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
            axis[index][0].set_xlim([0, end_point - start_point])
        plot_figure_manager = plt.get_current_fig_manager()
        plot_figure_manager.window.showMaximized()
        plt.show()

    def handleReferenceSignal_(self, header, signal):
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
