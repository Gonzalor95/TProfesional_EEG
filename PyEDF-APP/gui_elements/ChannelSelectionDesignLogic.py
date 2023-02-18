import os

from gui_elements.ChannelSelectionDesign import Ui_channel_selection_dialog
from PyQt5.QtWidgets import QDialog


class ChannelSelectionDialog(QDialog):
    def __init__(self, cb_method, channels, parent=None):
        super().__init__(parent)
        # Create an instance of the GUI
        self.ui = Ui_channel_selection_dialog()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)

        self.cb_method = cb_method
        self.selected_channels = []

        # Connect buttons with callbacks
        self.ui.channel_selection_accept_button.clicked.connect(self.acceptButtonClicked)
        self.ui.channel_selection_cancel_button.clicked.connect(self.cancelButtonClicked)
        self.ui.channel_list_view.itemClicked.connect(self.trackSelectedChannels)

        # Set up for initial state
        self.setUpInitialState(channels)

        # Execute and show widget
        self.exec_()

    def setUpInitialState(self, channels):
        """
        Method to set up the initial state
        """
        self.ui.channel_list_view.clear()
        for channel in channels:
            self.ui.channel_list_view.addItem(channel)

    def acceptButtonClicked(self):
        """
        Callback method for the Back button
        """
        # Get list of selected channels and return it
        self.cb_method(self.selected_channels)
        self.close()

    def cancelButtonClicked(self):
        """
        Callback method for the Skip button
        """
        # Return an empty array of selected channels
        self.cb_method([])
        self.close()

    def trackSelectedChannels(self, item):
        clicked_channel = item.text()
        if clicked_channel not in self.selected_channels:
            self.selected_channels.append(clicked_channel)
