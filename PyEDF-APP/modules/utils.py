from gui_elements.PopUpWindow import PopUpWindow
from PyQt5.QtWidgets import *
from modules.ChannelToIntProtocol import ProtocolDict


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

def delete_box_from_layout(layout, box):
    """
    Method to delete a box layout from another layout
    """
    for i in range(layout.count()):
        layout_item = layout.itemAt(i)
        if layout_item.layout() == box:
            delete_items_of_layout(layout_item.layout())
            layout.removeItem(layout_item)
            break

def delete_items_of_layout(layout):
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
                delete_items_of_layout(item.layout())

def validate_sim_time(selected_min_time, selected_max_time, max_allowable_time):
    """
    Method to validate the user input for the simulation time
    """
    try:
        x = int(selected_min_time)
        y = int(selected_max_time)
    except:
        return False
    if (x >= y) or (y > max_allowable_time):
        return False
    return True

def pre_process_signal(is_testing_signal, headers_and_signals_to_send):
    """
    Pre-processes the signals before beginning the transmision
    """
    # We will need to adequate the signal before beginning the transmition. Every pre-processing that can be done before the transmission is time we save
    # 1. Make it go from (-edf_digital_min, edf_digital_max) to (0, our_digital_max)
    # 2. Normalize it to our digital_max / physical_max range instead of the one present in the edf
    # 3. Convert the channels from strings to a byte by mapping then with the dict, then applying "to_bytes"
    # 4. Convert the signal data to 2 bytes using the "to_bytes" method
    processed_headers_and_signals = []

    # Step 1 and 2
    if not is_testing_signal:
        print ("for .edf signals we must perform step 1 and 2")

    # Step 3 and 4
    for header,signal in headers_and_signals_to_send:
        try:
            bytes_header = int(ProtocolDict.channel_enum_dict_[header]).to_bytes(2, byteorder="big", signed=False)
            bytes_signal = []
            for datum in signal:
                bytes_datum = int(datum).to_bytes(2, byteorder="big", signed=False)
                bytes_signal.append(bytes_datum)
            processed_headers_and_signals.append((bytes_header, bytes_signal))
        except Exception as e:
            print("There was a problem pre-processing the signal, cancelling transmission")
            return []
    return processed_headers_and_signals
