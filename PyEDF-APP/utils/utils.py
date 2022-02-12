from gui_elements.PopUpWindow import PopUpWindow
from PyQt5.QtWidgets import *


def parse_selected_channels_string(raw_selected_channels_string):
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
            PopUpWindow("Channel selection", "Wrong input format when selecting channels",
                        QMessageBox.Abort, QMessageBox.Warning)
            return []
    return return_list


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
