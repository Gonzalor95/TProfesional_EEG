#!/usr/bin/python3

import sys
import os
import time
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from EDFWorker import EDFWorker


class EDFSimulator(QWidget):

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
        self.initUI()

    def initUI(self):
        # ==================================== LEFT COLUMN ====================================
        self.browse_button = QPushButton("BROWSE")
        self.browse_button.clicked.connect(self.browseEDFFiles)

        # ==================================== VERTICAL SEPARATOR LINE ====================================
        self.separator_line = QFrame()
        self.separator_line.setFrameShape(QFrame.VLine)

        # ==================================== RIGHT COLUMN ====================================
        self.current_file_label = QLabel("Current EDF file: ")
        self.current_file_name_label = QLabel("")
        self.current_file_h_layout = QHBoxLayout()
        self.current_file_h_layout.addWidget(self.current_file_label)
        self.current_file_h_layout.addWidget(
            self.current_file_name_label, stretch=1)

        self.separator_line_2a = QFrame()
        self.separator_line_2a.setFrameShape(QFrame.HLine)

        # Information vertical layout
        self.information_title_label = QLabel("Signal information:")
        self.information_title_label.setFont(self.title_font)
        self.information_labels_layout = QVBoxLayout()
        self.info_v_layout = QVBoxLayout()
        self.info_v_layout.addWidget(
            self.information_title_label, alignment=Qt.AlignHCenter)
        self.info_v_layout.addLayout(
            self.information_labels_layout)
        self.info_v_layout.addStretch()

        # Config vertical layout
        # Title
        self.config_v_layout = QVBoxLayout()
        self.configuration_title_label = QLabel("Configuration:")
        self.configuration_title_label.setFont(self.title_font)
        self.config_v_layout.addWidget(
            self.configuration_title_label, alignment=Qt.AlignHCenter)
        # Selected channels
        self.selected_channels_key = QLabel("Selected channels: ")
        self.selected_channels_key.setFont(self.info_key_font)
        self.selected_channels_value = QLabel("")
        selected_channels_h_box = QHBoxLayout()
        selected_channels_h_box.addWidget(self.selected_channels_key)
        selected_channels_h_box.addWidget(
            self.selected_channels_value, stretch=1)
        self.config_v_layout.addLayout(selected_channels_h_box)
        channel_selector_h_box = QHBoxLayout()
        self.select_channels_button = QPushButton("Select")
        self.select_channels_button.clicked.connect(self.selectChannels)
        self.channel_select_line_edit = QLineEdit()
        channel_selector_h_box.addWidget(self.channel_select_line_edit)
        channel_selector_h_box.addWidget(self.select_channels_button)
        self.config_v_layout.addLayout(channel_selector_h_box)
        # Placeholders
        self.placeholder_label_2 = QLabel("asd2")
        self.placeholder_label_3 = QLabel("asd3")
        self.config_v_layout.addWidget(
            self.placeholder_label_2, alignment=Qt.AlignTop)
        self.config_v_layout.addWidget(
            self.placeholder_label_3, alignment=Qt.AlignTop)
        self.config_v_layout.addStretch()

        self.separator_line_2b = QFrame()
        self.separator_line_2b.setFrameShape(QFrame.HLine)

        self.preview_button = QPushButton("PREVIEW")
        self.preview_button.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.preview_button.clicked.connect(self.previewEDF)
        self.run_button = QPushButton("RUN")
        self.run_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.run_button.clicked.connect(self.runEDFSimulator)
        self.run_preview_buttons_h_layout = QHBoxLayout()
        self.run_preview_buttons_h_layout.addStretch(1)
        self.run_preview_buttons_h_layout.addWidget(self.preview_button)
        self.run_preview_buttons_h_layout.addWidget(self.run_button)
        self.run_preview_buttons_h_layout.addStretch(1)

        # ==================================== GRID ====================================
        main_grid = QGridLayout()
        main_grid.setRowStretch(1, 1)
        main_grid.setRowStretch(2, 1)
        main_grid.setRowStretch(3, 1)
        main_grid.setRowStretch(4, 100)
        main_grid.setRowStretch(5, 1)
        main_grid.setRowStretch(6, 10)
        main_grid.addWidget(self.browse_button, 1, 1, alignment=Qt.AlignTop)
        main_grid.addWidget(self.separator_line, 1, 2, 6, 1)
        main_grid.addLayout(self.current_file_h_layout,
                            1, 3, alignment=Qt.AlignTop)
        main_grid.addWidget(self.separator_line_2a, 2, 3)
        main_grid.addLayout(self.info_v_layout, 3, 3)
        main_grid.addLayout(self.config_v_layout, 4, 3)
        main_grid.addWidget(self.separator_line_2b, 5, 3)
        main_grid.addLayout(self.run_preview_buttons_h_layout, 6, 3)

        self.setLayout(main_grid)

        self.setGeometry(300, 300, 1000, 800)
        self.setWindowTitle('EDF Simulator')

        self.centerMainWindow()
        self.show()

    # ==================================== CLASS METHODS ====================================
    def centerMainWindow(self):
        """
        Class method to center the main window in the user screen
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

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
        # Load EDF file into worker
        if(self.edf_worker.readEDF(file_name)):
            # Place the file name in the dialog box
            self.current_file_name_label.setText(file_name)
            # Delete info h layouts in the info v layout (not the title)
            for widget_index in range(self.information_labels_layout.count()):
                self.deleteBoxFromLayout(
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
        else:
            print("Error when trying to load the EDF file")

    def previewEDF(self):
        """
        Callback method for the "preview" button press.

        This method will plot the selected signal channels and show it to the user
        """
        print("Preview EDF requested")
        if(self.edf_worker.previewSignals() == False):
            print("Error in preview EDF signal. Check if a file was loaded")

    def runEDFSimulator(self):
        print("Run EDF simulator requested")

    def selectChannels(self):
        """
        Callback method for the select channels button

        This method reads the selected channels line edit, parses it into an array of
        integers and set the EDF worker with it
        """
        raw_selected_channels_string = self.channel_select_line_edit.text()
        selected_channels = self.parseSelectedChannelsString(
            raw_selected_channels_string)
        if not selected_channels:
            print("Error when parsing input into channels")
        if(self.edf_worker.setSelectedChannels(selected_channels) == False):
            print("Error when trying to set the selected channels in the EDF worker")
        self.selected_channels_value.setText(",".join([str(int) for int in selected_channels]))

    def deleteBoxFromLayout(self, layout, box):
        """
        Method to delete a box layout from another layout
        """
        for i in range(layout.count()):
            layout_item = layout.itemAt(i)
            if layout_item.layout() == box:
                self.deleteItemsOfLayout(layout_item.layout())
                layout.removeItem(layout_item)
                break

    def deleteItemsOfLayout(self, layout):
        """
        Method to delete the items of a layout
        """
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())

    def parseSelectedChannelsString(self, raw_selected_channels_string):
        """
        Method to parse the user input selected channel string into an array of ints
        """
        return_list = []
        aux_list = raw_selected_channels_string.split(",")
        for value in aux_list:
            if value.isdigit() and int(value) not in return_list:
                return_list.append(int(value))
            elif "-" in value:
                dash_subarray = parse_dash_separated_values(value)
                for value in dash_subarray:
                    if value not in return_list:
                        return_list.append(value)
            elif not value.isdigit():
                print("Wrong input format for channel selection")
                return []
        return return_list


def main():
    app = QApplication(sys.argv)
    ex = EDFSimulator()
    sys.exit(app.exec_())


def parse_dash_separated_values(dash_string):
    """
    Aux method to parse the dash separated values into an array of ints
    """
    aux_list = dash_string.split("-")
    return_list = []
    if len(aux_list) != 2:
        print(
            "Error when parsing '-' separated values, more than two values found")
        return []
    if (not aux_list[0].isdigit()) or (not aux_list[1].isdigit()):
        print(
            "Error when parsing '-' separated values, values are not digits")
        return []
    if int(aux_list[0]) > int(aux_list[1]):
        print(
            "Error when parsing '-' separated values, first value bigger than the second one")
        return []
    for i in range(int(aux_list[1]) - int(aux_list[0])):
        return_list.append(int(aux_list[0]) + i)
    return_list.append(int(aux_list[1]))
    return return_list


if __name__ == '__main__':
    main()
