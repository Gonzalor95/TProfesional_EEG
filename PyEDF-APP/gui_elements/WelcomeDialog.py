import os

from gui_elements.WelcomeScreenDesigner import Ui_WelcomeDialog
from PyQt5.QtWidgets import QDialog


class WelcomeDialog(QDialog):
    initial_selection_ = {}
    states_ = ["file", "device"]  # Two possible options: "file" and "device"
    state_ = ""  # State of the welcome dialog screen

    def __init__(self, serial_comm_worker, parent=None):
        super().__init__(parent)
        # Create an instance of the GUI
        self.ui = Ui_WelcomeDialog()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)

        # Save the serial comm worker. It will be used to list the edf devices
        self.serial_comm_worker = serial_comm_worker

        # Connect widget with callbacks
        self.ui.welcome_list.itemClicked.connect(self.saveListSelection)
        self.ui.back_button.clicked.connect(self.backButtonClicked)
        self.ui.skip_button.clicked.connect(self.skipButtonClicked)
        self.ui.next_button.clicked.connect(self.nextButtonClicked)

        # Set up for initial state
        self.setUpInitialState()

        # Execute and show widget
        self.exec_()

    def setUpInitialState(self):
        """
        Method to set up the initial state. Disables the corresponding buttons and looks for EDF files in
        the "edf_samples" folder at the same level the program is located
        """
        self.ui.welcome_list.clear()
        self.state_ = self.states_[0]
        self.ui.instructions_label.setText("Please, select an EDF file (you can choose a different one later on):")
        self.ui.next_button.setText("Next")
        self.ui.back_button.setEnabled(False)
        edf_files_path = os.getcwd() + "\edf_samples"
        for file in os.listdir(edf_files_path):
            if file.endswith(".edf"):
                self.ui.welcome_list.addItem(file)

    def setUpDeviceSelectionState(self):
        self.state_ = self.states_[1]
        self.ui.instructions_label.setText("Please, select an EDF generator device (you can choose a different one later on):")
        self.ui.next_button.setText("Finish")
        self.ui.skip_button.setEnabled(False)
        self.ui.back_button.setEnabled(True)
        self.ui.welcome_list.clear()
        comm_ports = self.serial_comm_worker.listSerialPorts()
        for device in comm_ports:
            self.ui.welcome_list.addItem(device)

    def backButtonClicked(self):
        if self.state_ ==self.states_[1]:
            self.setState(self.states_[0])

    def skipButtonClicked(self):
        if self.state_ == self.states_[0]:
            self.setState(self.states_[1])

    def nextButtonClicked(self):
        if self.state_ == self.states_[0]:
            self.setState(self.states_[1])
        elif self.state_ == self.states_[1]:
            self.done(1)

    def saveListSelection(self, selection):
        if self.state_ == self.states_[0]:
            full_path = os.getcwd() + "\edf_samples" + "\\" + selection.text()
            self.initial_selection_["initial_selected_file"] = full_path
        if self.state_ == self.states_[1]:
            self.initial_selection_[
                "initial_selected_device"] = selection.text()

    def setState(self, state):
        """
        Method to set the state of the welcome screen

        @param state -- State of the welcome screen. Supports "file" and "device"
        """
        if state == self.states_[0]:
            self.setUpInitialState()
        if state == self.states_[1]:
            self.setUpDeviceSelectionState()

    def getInitialSelection(self):
        """
        Method to return the initial selection of the user for EDF file and EDF device

        @return initial_selection -- Dictionary with the initial_file and initial_device selected by the user
        """
        return self.initial_selection_
