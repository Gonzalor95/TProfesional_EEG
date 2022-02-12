#!/usr/bin/python3

import sys
import os
import yaml
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qtrangeslider import QLabeledRangeSlider
from EDFWorker import EDFWorker
from SerialComWorker import SerialComWorker

# GUI elements
from EDFGUI import Ui_MainWindow
from gui_elements.PopUpWindow import PopUpWindow
from gui_elements.CommPortsPopUp import CommPortsPopUp
from gui_elements.WelcomeScreen import WelcomeScreen
from gui_elements.Style import FontStyles

# Utils
from utils import utils


class EDFSimulator(QMainWindow, Ui_MainWindow):
    big_int_ = 9999999999
    # Max amount of channels of the signal generator. Set in the config file
    max_channels_ = 0
    selected_device_ = ""    # Currently selected EDF simulator device
    selected_edf_file_ = ""  # Currently selected EDF file

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.info_h_boxes = []
        self.font_styles = FontStyles()

        # EDF worker instance
        self.edf_worker = EDFWorker()
        # Serial communication worker instance
        self.serial_comm_worker = SerialComWorker()
        # Read yaml config file and initialize values
        self.readConfigFile()

        self.range_slider = QLabeledRangeSlider(Qt.Horizontal)
        self.range_slider.setHandleLabelPosition(
            QLabeledRangeSlider.LabelPosition.LabelsBelow)
        self.range_slider.setValue([0, 99])
        self.range_slider_layout.addWidget(self.range_slider)

        # Set fonts
        self.setFonts()

        # Connect user inputs
        self.browse_edf_button.clicked.connect(self.browseEDFFiles)
        self.browse_devices_button.clicked.connect(self.browseDevices)
        self.testing_signals_button.clicked.connect(
            self.changeToTestingSignals)
        self.select_channels_button.clicked.connect(self.selectChannels)
        self.range_slider.valueChanged.connect(self.timeSliderChanged)
        self.preview_button.clicked.connect(self.previewEDF)
        # self.preview_dig_button.clicked.connect(self.previewDigitalEDF)
        self.run_button.clicked.connect(self.runEDFSimulator)

    # ==================================== CLASS METHODS ====================================

    def browseEDFFiles(self):
        """
        Callback method for the "browse" button press.
        This method will try to load the EDF file clicked by the user
        into the system and display the corresponding information.
        """
        # Filter only for EDF files
        filter = "EDFFiles(*.edf)"
        file_name = QFileDialog.getOpenFileName(
            self, "Select EDF file", os.getcwd(), filter)[0]
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
                print(
                    "Number of channels of the selected EDF file exceeds the max amount, "
                    "please select a different EDF file")
                self.edf_worker.resetWorker()
                return
            # Place the file name in the dialog box
            self.current_file_name_label.setText(file_name)
            # Set the maximun time selector slider value to the signal duration
            self.range_slider.setMaximum(self.edf_worker.getDuration())
            self.range_slider.setValue([0, self.big_int_])
            # Set selected channels to ALL
            self.selected_channels_value.setText("ALL")
            # Delete info h layouts in the info v layout (not the title)
            for widget_index in range(self.information_labels_layout.count()):
                utils.delete_box_from_layout(
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
            self.selected_edf_file_ = file_name
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
            self.comm_ports_list = CommPortsPopUp(
                comm_ports, self.saveSelectedDevice, prefix="EDF signal generator: ")
            self.comm_ports_list.show()
        else:
            PopUpWindow("Device selection", "No EDF signal generator found!",
                        QMessageBox.Abort, QMessageBox.Critical)

    def saveSelectedDevice(self, user_chosen_device):
        """
        Method to save the selected device and set it in the serial communication worker
        """
        self.selected_device_ = user_chosen_device
        self.serial_comm_worker.selectCommPort(user_chosen_device)

    def changeToTestingSignals(self):
        """
        Callback metho for the "Testing signals" button press.
        """

    def previewEDF(self):
        """
        Callback method for the "preview" button press. Used to preview the physical signals
        This method will plot the selected signal channels and show it to the user
        """
        print("Preview EDF requested")
        if(self.edf_worker.previewSignals("physical") == False):
            print("Error in preview EDF signal. Check if a file was loaded")

    def previewDigitalEDF(self):
        """
        Callback method for the "preview" button press. Used to preview digital signals.
        This method will plot the selected signal channels and show it to the user
        """
        print("Preview digital EDF requested")
        if(self.edf_worker.previewSignals("digital") == False):
            print("Error in preview EDF signal. Check if a file was loaded")

    def runEDFSimulator(self):
        """
        Callback method for the "run" button
        """
        print("Run EDF simulator requested")

    def selectChannels(self):
        """
        Callback method for the "select channels" button
        This method reads the selected channels line edit, parses it into an array of
        integers and set the EDF worker with it
        """
        raw_string = self.channel_select_line_edit.text()
        if raw_string:
            if raw_string == "ALL":
                selected_channels = [i for i in range(
                    0, self.edf_worker.getNumberOfChannels())]
            else:
                # Remove all whitespaces
                raw_string = raw_string.replace(" ", "")
                selected_channels = utils.parse_selected_channels_string(
                    raw_string)
            if not selected_channels:
                print("Error when parsing input into channels")
            if self.edf_worker.setSelectedChannels(selected_channels) == False:
                PopUpWindow("Channel selection", "Error when trying to set the selected channels in the EDF worker, please try again",
                            QMessageBox.Abort, QMessageBox.Critical)
                print("Error when trying to set the selected channels in the EDF worker")
            else:
                self.selected_channels_value.setText(
                    ",".join([str(int) for int in selected_channels]))
        else:
            print("Empty input in channel selector")
        # Clear line edit
        self.channel_select_line_edit.clear()

    def timeSliderChanged(self):
        if self.edf_worker.isFileLoaded():
            self.edf_worker.setSelectedSimTime(self.range_slider.value())

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
        with open('device_params.yaml', 'r') as file:
            device_params = yaml.safe_load(file)
            try:
                self.max_channels_ = device_params["max_channels"]
            except(KeyError):
                PopUpWindow("Configuration file", "Error in configuration file",
                            QMessageBox.Abort, QMessageBox.Critical)
                sys.exit()

    def setFonts(self):
        """
        TODO
        """
        self.current_file_label.setFont(self.font_styles.info_key_font)
        self.current_device_label.setFont(self.font_styles.info_key_font)
        self.information_title_label.setFont(self.font_styles.title_font)
        self.configuration_title_label.setFont(self.font_styles.title_font)
        self.selected_channels_key.setFont(self.font_styles.info_key_font)
        self.selected_sim_time_key.setFont(self.font_styles.info_key_font)


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
