#!/usr/bin/python3

import sys
import os
import yaml
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from modules.EDFWorker import EDFWorker
from modules.SerialComWorker import SerialComWorker
from modules.TestingSignals import TestingSignalsWorker
from modules.utils import *

# GUI elements
from gui_elements.EDFGUIDesigner import Ui_MainWindow
from gui_elements.WelcomeScreenDesignLogic import WelcomeDialog
from gui_elements.PopUpWindow import PopUpWindow
from gui_elements.ListSelectionPopUp import ListSelectionPopUp
from gui_elements.Style import FontStyles
from gui_elements.ChannelSelectionDesignLogic import ChannelSelectionDialog
from gui_elements.TestingSignalsDesignLogic import TestingSignalsDialog


# TODO: (Delete) Command to convert .ui files to python files
# python -m PyQt5.uic.pyuic -x .\gui_elements\EDFGUIDesigner.ui -o .\gui_elements\EDFGUIDesigner.py
# Common mode signals: https://physionet.org/content/eegmat/1.0.0/


class EDFSimulator(QMainWindow, Ui_MainWindow):
    big_int_ = 9999999999
    # Max amount of channels of the signal generator. Set in the config file
    max_channels_ = 0
    # Flag to indicate whether the selected signal is a testing one or a real one
    is_testing_signal_ = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.info_h_boxes = []
        self.font_styles = FontStyles()

        # Read yaml config file and initialize values
        self.readConfigFile()
        # EDF worker instance
        self.edf_worker = EDFWorker()
        # Serial communication worker instance
        self.serial_comm_worker = SerialComWorker()
        # Testing signals worker instance
        self.testing_signals_worker = TestingSignalsWorker(self.max_channels_)

        # Add custom double range slider
        self.min_time_input = QLineEdit()
        self.max_time_input = QLineEdit()
        self.set_sim_time_button = QPushButton("Set time")
        self.range_slider_layout.addWidget(self.min_time_input)
        self.range_slider_layout.addWidget(self.max_time_input)
        self.range_slider_layout.addWidget(self.set_sim_time_button)

        # Set fonts
        self.setFonts()

        # Connect user inputs
        self.browse_edf_button.clicked.connect(self.browseEDFFiles)
        self.browse_devices_button.clicked.connect(self.browseDevices)
        self.testing_signals_button.clicked.connect(self.browseTestingSignals)
        self.channel_browse_button.clicked.connect(self.browseChannels)
        self.set_sim_time_button.clicked.connect(self.simTimeChanged)
        self.preview_button.clicked.connect(self.previewEDF)
        self.run_button.clicked.connect(self.runEDFSimulator)

        # Show welcome screen
        welcome_dialog = WelcomeDialog(self.serial_comm_worker)
        self.setInitialSelection(welcome_dialog.getInitialSelection())

    # ==================================== CLASS METHODS ====================================

    def browseEDFFiles(self):
        """
        Callback method for the "browse" button press.
        This method will try to load the EDF file clicked by the user
        into the system and display the corresponding information.
        """
        # Filter only for EDF files
        filter = "EDFFiles(*.edf)"
        file_name = QFileDialog.getOpenFileName(self, "Select EDF file", os.getcwd() + "\edf_samples", filter)[0]
        if file_name:
            self.loadEDFFile(file_name)

    def loadEDFFile(self, file_name):
        """
        Method to load an EDF file into the edf worker and its information on the GUI
        """
        # Load EDF file into worker and GUI
        if(self.edf_worker.readEDF(file_name)):
            # Check that the amount of channels doesn't exceed the configured one
            if self.edf_worker.getNumberOfChannels() >= self.max_channels_:
                print("Number of channels of the selected EDF file exceeds the max amount, please select a different EDF file")
                self.edf_worker.resetWorker()
                PopUpWindow("EDF file selection", "Number of channels of the selected EDF file exceeds the max amount, "
                            "please select a different EDF file",
                            QMessageBox.Abort, QMessageBox.Warning)
                return
            # Place the file name in the dialog box
            self.current_file_name_label.setText(file_name)
            # Set the maximun time selector slider value to the signal duration
            self.selected_sim_time_value.setText(
                str(0) + " - " + str(self.edf_worker.getDuration()))
            self.edf_worker.setSelectedSimTime(
                (int(0), int(self.edf_worker.getDuration())))
            # Set selected channels to ALL
            self.selected_channels_value.setText("-".join(self.edf_worker.getChannels()))
            # Delete info h layouts in the info v layout (not the title)
            for widget_index in range(self.information_labels_layout.count()):
                delete_box_from_layout(
                    self.information_labels_layout, self.info_h_boxes[widget_index])
            # Generate the information h boxes and add them to the info v layout
            signal_info_dict = self.edf_worker.getSignalInfo()
            self.info_h_boxes.clear()
            for key in signal_info_dict:
                info_key = QLabel(str(key) + ": ")
                info_key.setFont(self.font_styles.info_key_font)
                info_value = QLabel(str(signal_info_dict[key]))
                h_box = QHBoxLayout()
                h_box.addWidget(info_key)
                h_box.addWidget(info_value, stretch=1)
                self.info_h_boxes.append(h_box)
                self.information_labels_layout.addLayout(h_box)
            # Set the flag to indicate that the signal loaded is not a testing signal
            self.is_testing_signal_ = False
        else:
            print("Error when trying to load the EDF file")
            PopUpWindow("EDF file selection", "Error when trying to load the selected EDF file, please try again",
                        QMessageBox.Abort, QMessageBox.Critical)

    def browseDevices(self):
        """
        Callback method for the "browse devices" button press. This method will look for the
        connected serial communication devices and let the user choose the correct one
        """
        comm_ports = self.serial_comm_worker.listSerialPorts()

        if comm_ports:
            self.comm_ports_list = ListSelectionPopUp(
                self.saveSelectedDevice, comm_ports)
            self.comm_ports_list.show()
        else:
            PopUpWindow("Device selection", "No EDF signal generator found!",
                        QMessageBox.Abort, QMessageBox.Critical)

    def saveSelectedDevice(self, user_chosen_device):
        """
        Method to save the selected device and set it in the serial communication worker
        """
        self.serial_comm_worker.selectCommPort(user_chosen_device)
        self.current_device_name_label.setText(user_chosen_device)

    def browseTestingSignals(self):
        """
        Callback method for the "Testing signals" button press.
        """
        testing_signal_dialog = TestingSignalsDialog()
        self.loadTestingSignal(testing_signal_dialog.getSelection())

    def loadTestingSignal(self, selection_dict):
        """
        Method to load a testing signal into the testing signal worker and its information on the GUI
        """
        if selection_dict:
            # Load testing signal into worker and GUI
            self.testing_signals_worker.generateTestingSignal(
                selection_dict["signal_name"], selection_dict["frecuency"], selection_dict["amplitude"], selection_dict["sample_rate"], selection_dict["duration"])
            # Place the file name in the dialog box
            self.current_file_name_label.setText(selection_dict["signal_name"])
            # Set the maximun time selector slider value to the signal duration
            self.selected_sim_time_value.setText(str(0) + " - " + str(selection_dict["duration"]))
            self.testing_signals_worker.setSelectedSimTime((int(0), int(selection_dict["duration"])))
            # Set selected channels to ALL
            self.selected_channels_value.setText("ALL")
            # Delete info h layouts in the info v layout (not the title)
            for widget_index in range(self.information_labels_layout.count()):
                delete_box_from_layout(
                    self.information_labels_layout, self.info_h_boxes[widget_index])
            # Generate the information h boxes and add them to the info v layout
            self.info_h_boxes.clear()
            for key in selection_dict:
                info_key = QLabel(str(key) + ": ")
                info_key.setFont(self.font_styles.info_key_font)
                info_value = QLabel(str(selection_dict[key]))
                h_box = QHBoxLayout()
                h_box.addWidget(info_key)
                h_box.addWidget(info_value, stretch=1)
                self.info_h_boxes.append(h_box)
                self.information_labels_layout.addLayout(h_box)
            # Set the flag to indicate that the signal loaded is a testing signal
            self.is_testing_signal_ = True
        else:
            print("No testing signal selected")

    def previewEDF(self):
        """
        Callback method for the "preview" button press. Used to preview the physical signals
        This method will plot the selected signal channels and show it to the user
        """
        print("Preview EDF requested")
        if self.is_testing_signal_:
            if(self.testing_signals_worker.previewSignal() == False):
                print("Error when previewing testing signal. Check if a signal was loaded")
        else:
            if(self.edf_worker.previewSignals() == False):
                print("Error in preview EDF signal. Check if a file was loaded")

    def runEDFSimulator(self):
        """
        Callback method for the "run" button
        """
        if self.is_testing_signal_:
            headers_and_signals_to_send = self.testing_signals_worker.getSimulationSignals()
        else:
            headers_and_signals_to_send = self.edf_worker.getSimulationSignals()
        headers_and_signals_to_send = pre_process_signal(self.is_testing_signal_, headers_and_signals_to_send)
        print("Run EDF simulator requested")

    def browseChannels(self):
        """
        Callback for the browseChannels button click
        """
        if self.is_testing_signal_:
            ChannelSelectionDialog(self.setChannels, self.testing_signals_worker.getChannels())
        else:
            ChannelSelectionDialog(self.setChannels, self.edf_worker.getChannels())

    def setChannels(self, selected_channels):
        """
        Method to set the channels in the EDF Worker
        """
        if not selected_channels:
            print("No channels selected, keeping old selection")
        else:
            self.selected_channels_value.setText("-".join(selected_channels))
            if self.is_testing_signal_:
                self.testing_signals_worker.setSelectedChannels(selected_channels)
            else:
                self.edf_worker.setSelectedChannels(selected_channels)

    def simTimeChanged(self):
        """
        Callback method for the slider changed
        """
        raw_min_time_str = self.min_time_input.text()
        raw_max_time_str = self.max_time_input.text()
        if validate_sim_time(raw_min_time_str, raw_max_time_str, self.edf_worker.getDuration()) == False:
            PopUpWindow("Simulation time selection", "Bad user input for the simulation time, try again",
                        QMessageBox.Abort, QMessageBox.Critical)
            return
        # Set in both testing signal worker and edf worker
        self.testing_signals_worker.setSelectedSimTime(
            (int(raw_min_time_str), int(raw_max_time_str)))
        if self.edf_worker.isFileLoaded():
            self.edf_worker.setSelectedSimTime(
                (int(raw_min_time_str), int(raw_max_time_str)))
        self.selected_sim_time_value.setText(
            raw_min_time_str + " - " + raw_max_time_str)

    def centerMainWindow(self):
        """
        Class method to center the main window in the user screen
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def readConfigFile(self):
        """
        Method to read the yaml configuration file and load it
        """
        with open('config/device_params.yaml', 'r') as file:
            device_params = yaml.safe_load(file)
            try:
                self.max_channels_ = device_params["max_channels"]
                self.max_physical_ = device_params["max_physical"]
                self.bit_resolution_ = device_params["bit_resolution"]
            except(KeyError):
                PopUpWindow("Configuration file", "Error in configuration file",
                            QMessageBox.Abort, QMessageBox.Critical)
                sys.exit()

    def setFonts(self):
        """
        Method to set the font styles of the GUI
        """
        self.current_file_label.setFont(self.font_styles.info_key_font)
        self.current_device_label.setFont(self.font_styles.info_key_font)
        self.information_title_label.setFont(self.font_styles.title_font)
        self.configuration_title_label.setFont(self.font_styles.title_font)
        self.selected_channels_key.setFont(self.font_styles.info_key_font)
        self.selected_sim_time_key.setFont(self.font_styles.info_key_font)

    def setInitialSelection(self, initial_selection):
        """
        Method to set the initial selection of the user. Sets the EDF file and device if the user selected one
        """
        if "initial_selected_file" in initial_selection:
            self.loadEDFFile(initial_selection["initial_selected_file"])
        if "initial_selected_device" in initial_selection:
            self.saveSelectedDevice(
                initial_selection["initial_selected_device"])


def main():
    app = QApplication(sys.argv)
    # App icon
    # TODO logo not loading in Windows taskbar
    app_icon = QIcon()
    app_icon.addFile('logo_fiuba.png', QSize(16, 16))
    app_icon.addFile('logo_fiuba.png', QSize(24, 24))
    app_icon.addFile('logo_fiuba.png', QSize(32, 32))
    app_icon.addFile('logo_fiuba.png', QSize(48, 48))
    app_icon.addFile('logo_fiuba.png', QSize(256, 256))
    app.setWindowIcon(app_icon)
    # Start EDF worker
    ex = EDFSimulator()
    ex.show()
    # Start app
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
