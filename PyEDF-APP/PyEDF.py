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
from gui_elements.PopUpWindow import PopUpWindow
from gui_elements.CommPortsPopUp import CommPortsPopUp
from gui_elements.WelcomeScreen import WelcomeScreen

# Utils
from utils import utils


class EDFSimulator(QWidget):
    big_int_ = 9999999999
    # Max amount of channels of the signal generator. Set in the config file
    max_channels = 0
    selected_device = ""    # Currently selected EDF simulator device
    selected_edf_file = ""  # Currently selected EDF file

    def __init__(self):
        super().__init__()
        self.info_h_boxes = []
        # Titles font
        self.title_font = QFont()
        self.title_font.setBold(True)
        self.title_font.setUnderline(True)
        self.title_font.setPointSize(15)
        # Info/config subtitles font
        self.info_key_font = QFont()
        self.info_key_font.setBold(True)
        self.info_key_font.setPointSize(14)
        # EDF worker instance
        self.edf_worker = EDFWorker()
        # Serial communication worker instance
        self.serial_comm_worker = SerialComWorker()
        # Read yaml config file and initialize values
        self.readConfigFile()
        initial_selection = self.showWelcomeScreen()
        self.initUI(initial_selection)

    def showWelcomeScreen(self):
        """
        Method to show a welcome screen for the user to initially select an EDF file and device
        """
        # Show the welcome screen and return a dict with the initial user selected EDF file and device
        return WelcomeScreen(self.edf_worker, self.serial_comm_worker)

    def initUI(self, initial_selection):
        """
        Method to show the main window

        @param initial_selection -- Initially selected EDF file and device from the welcome screen
        """
        # ==================================== LEFT COLUMN ====================================
        self.browse_edf_button = QPushButton("Browse EDFs")
        self.browse_edf_button.clicked.connect(self.browseEDFFiles)

        self.browse_devices_button = QPushButton("Browse devices")
        self.browse_devices_button.clicked.connect(self.browseDevices)

        self.testing_signals_button = QPushButton("Testing signals")
        self.testing_signals_button.clicked.connect(
            self.changeToTestingSignals)

        buttons_v_layout = QVBoxLayout()
        buttons_v_layout.addWidget(
            self.browse_edf_button, alignment=Qt.AlignTop)
        buttons_v_layout.addWidget(
            self.browse_devices_button, alignment=Qt.AlignTop)
        buttons_v_layout.addWidget(
            self.testing_signals_button, alignment=Qt.AlignTop)

        # ==================================== VERTICAL SEPARATOR LINE ====================================
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.VLine)
        separator_line.setStyleSheet("border:2px; border-style:solid")

        # ==================================== RIGHT COLUMN ====================================
        # Current file/signal and device selected
        current_file_label = QLabel("Current EDF file: ")
        current_file_label.setFont(self.info_key_font)
        self.current_file_name_label = QLabel("")
        current_file_h_layout = QHBoxLayout()
        current_file_h_layout.addWidget(current_file_label)
        current_file_h_layout.addWidget(
            self.current_file_name_label, stretch=1)
        current_device_label = QLabel("Current device: ")
        current_device_label.setFont(self.info_key_font)
        self.current_device_name_label = QLabel("")
        current_device_h_layout = QHBoxLayout()
        current_device_h_layout.addWidget(current_device_label)
        current_device_h_layout.addWidget(
            self.current_file_name_label, stretch=1)
        current_selection_v_layout = QVBoxLayout()
        current_selection_v_layout.addLayout(current_file_h_layout)
        current_selection_v_layout.addLayout(current_device_h_layout)

        separator_line_2a = QFrame()
        separator_line_2a.setFrameShape(QFrame.HLine)
        separator_line_2a.setStyleSheet("border:1px; border-style:dashed")

        # Information vertical layout
        information_title_label = QLabel("Signal information:")
        information_title_label.setFont(self.title_font)
        self.information_labels_layout = QVBoxLayout()
        dotted_separator_line = QFrame()
        dotted_separator_line.setFrameShape(QFrame.HLine)
        dotted_separator_line.setFrameShadow(QFrame.Sunken)
        dotted_separator_line.setStyleSheet("border:1px; border-style:dashed")
        info_v_layout = QVBoxLayout()
        info_v_layout.addWidget(
            information_title_label, alignment=Qt.AlignHCenter)
        info_v_layout.addLayout(
            self.information_labels_layout)
        info_v_layout.addWidget(dotted_separator_line)
        info_v_layout.addStretch()

        # Config vertical layout
        # Title
        config_v_layout = QVBoxLayout()
        configuration_title_label = QLabel("Configuration:")
        configuration_title_label.setFont(self.title_font)
        config_v_layout.addWidget(
            configuration_title_label, alignment=Qt.AlignHCenter)
        # Selected channels
        selected_channels_key = QLabel("Selected channels: ")
        selected_channels_key.setFont(self.info_key_font)
        self.selected_channels_value = QLabel("")
        selected_channels_h_box = QHBoxLayout()
        selected_channels_h_box.addWidget(selected_channels_key)
        selected_channels_h_box.addWidget(
            self.selected_channels_value, stretch=1)
        channel_selector_h_box = QHBoxLayout()
        self.select_channels_button = QPushButton("Select")
        self.select_channels_button.clicked.connect(self.selectChannels)
        self.channel_select_line_edit = QLineEdit()
        self.channel_select_line_edit.setPlaceholderText("0, 1, 5 - 6,...")
        channel_selector_h_box.addWidget(self.channel_select_line_edit)
        channel_selector_h_box.addWidget(self.select_channels_button)
        config_v_layout.addLayout(selected_channels_h_box)
        config_v_layout.addLayout(channel_selector_h_box)
        # Time slider
        selected_sim_time_key = QLabel("Simulation time [s]: ")
        selected_sim_time_key.setFont(self.info_key_font)
        self.selected_sim_time_value = QLabel("")
        selected_sim_time_h_box = QHBoxLayout()
        selected_sim_time_h_box.addWidget(selected_sim_time_key)
        selected_sim_time_h_box.addWidget(self.selected_sim_time_value)
        self.range_slider = QLabeledRangeSlider(Qt.Horizontal)
        self.range_slider.setHandleLabelPosition(
            QLabeledRangeSlider.LabelPosition.LabelsBelow)
        self.range_slider.setValue([0, 99])
        self.range_slider.valueChanged.connect(self.timeSliderChanged)
        config_v_layout.addLayout(selected_sim_time_h_box)
        config_v_layout.addWidget(self.range_slider)
        # Placeholders
        self.placeholder_label_3 = QLabel("asd3")
        self.placeholder_label_4 = QLabel("asd4")
        config_v_layout.addWidget(
            self.placeholder_label_3, alignment=Qt.AlignTop)
        config_v_layout.addWidget(
            self.placeholder_label_4, alignment=Qt.AlignTop)
        config_v_layout.addStretch()

        separator_line_2b = QFrame()
        separator_line_2b.setFrameShape(QFrame.HLine)
        separator_line_2b.setStyleSheet("border:1px; border-style:dashed")

        self.preview_button = QPushButton("PREVIEW PHYSICAL")
        self.preview_button.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.preview_button.clicked.connect(self.previewEDF)
        self.preview_dig_button = QPushButton("PREVIEW DIGITAL")
        self.preview_dig_button.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.preview_dig_button.clicked.connect(self.previewDigitalEDF)
        self.run_button = QPushButton("RUN")
        self.run_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.run_button.clicked.connect(self.runEDFSimulator)
        run_preview_buttons_h_layout = QHBoxLayout()
        run_preview_buttons_h_layout.addStretch(1)
        run_preview_buttons_h_layout.addWidget(self.preview_button)
        run_preview_buttons_h_layout.addWidget(self.preview_dig_button)
        run_preview_buttons_h_layout.addWidget(self.run_button)
        run_preview_buttons_h_layout.addStretch(1)

        # ==================================== GRID ====================================
        main_grid = QGridLayout()
        main_grid.setRowStretch(1, 1)
        main_grid.setRowStretch(2, 1)
        main_grid.setRowStretch(3, 1)
        main_grid.setRowStretch(4, 100)
        main_grid.setRowStretch(5, 1)
        main_grid.setRowStretch(6, 10)
        main_grid.addLayout(buttons_v_layout, 1, 1, alignment=Qt.AlignTop)
        main_grid.addWidget(separator_line, 1, 2, 6, 1)
        main_grid.addLayout(current_selection_v_layout, 1, 3)
        main_grid.addWidget(separator_line_2a, 2, 3, alignment=Qt.AlignTop)
        main_grid.addLayout(info_v_layout, 3, 3)
        main_grid.addLayout(config_v_layout, 4, 3)
        main_grid.addWidget(separator_line_2b, 5, 3)
        main_grid.addLayout(run_preview_buttons_h_layout, 6, 3)

        self.setLayout(main_grid)

        self.setGeometry(300, 300, 1000, 800)
        self.setWindowTitle('EDF Simulator')

        self.centerMainWindow()
        self.show()
        # Load the user selected file and device that was chosen in the welcome screen
        if "selected_edf_file" in initial_selection:
            self.loadEDFFile(initial_selection["selected_edf_file"])
        if "selected_edf_device" in initial_selection:
            self.saveSelectedDevice(initial_selection["selected_edf_device"])

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
        self.loadEDFFile(file_name)

    def loadEDFFile(self, file_name):
        """
        Method to load an EDF file into the edf worker and its information on the GUI
        """
        # Load EDF file into worker and GUI
        if(self.edf_worker.readEDF(file_name)):
            # Check that the amount of channels doesn't exceed the configured one
            if self.edf_worker.getNumberOfChannels() >= self.max_channels:
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
                info_key.setFont(self.info_key_font)
                info_value = QLabel(str(signal_info_dict[key]))
                h_box = QHBoxLayout()
                h_box.addWidget(info_key)
                h_box.addWidget(info_value, stretch=1)
                self.info_h_boxes.append(h_box)
                self.information_labels_layout.addLayout(h_box)
            self.selected_edf_file = file_name
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
        self.selected_device = user_chosen_device
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
                self.max_channels = device_params["max_channels"]
            except(KeyError):
                PopUpWindow("Configuration file", "Error in configuration file",
                            QMessageBox.Abort, QMessageBox.Critical)
                sys.exit()


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
    # Start app
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
