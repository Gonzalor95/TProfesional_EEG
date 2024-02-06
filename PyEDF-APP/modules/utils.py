from gui_elements.PopUpWindow import PopUpWindow
from PyQt5.QtWidgets import *
from modules.ChannelToIntProtocol import ProtocolDict
from functools import wraps
import numpy as np
import time

def timeit(func):
    """
    Function to time functions with a decorator
    """
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper

def delete_box_from_layout(layout, box):
    """
    Method to delete a GUI box layout from another layout
    """
    for i in range(layout.count()):
        layout_item = layout.itemAt(i)
        if layout_item.layout() == box:
            delete_items_of_layout(layout_item.layout())
            layout.removeItem(layout_item)
            break

def delete_items_of_layout(layout):
    """
    Method to delete the items of a GUI layout
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

def to_bytes_packages(headers_and_signals_to_send):
    """
    Pre-processes the signals before beginning the transmision
    """
    # We will need to adequate the signal before beginning the transmition. Every pre-processing that can be done before the transmission is time we save
    # - Convert the channel names from strings to a byte by mapping then with the dict, then applying "to_bytes"
    # - Convert the signal data to 2 bytes using the "to_bytes" method
    # Output format: [ (b"0x01", [b"0xff", b"0x1e", ...]),  (b"0x04", [b"0xff", b"0x1e", ...]), ...]
    processed_headers_and_signals = []

    for header,signal in headers_and_signals_to_send:
        if header not in ['A1', 'A2']:
            try:
                bytes_header = int(ProtocolDict.channel_enum_dict_[header]).to_bytes(2, byteorder="big", signed=False)
                bytes_signal = []
                for datum in signal:
                    bytes_datum = int(datum).to_bytes(2, byteorder="big", signed=False)
                    bytes_signal.append(bytes_datum)
                processed_headers_and_signals.append((bytes_header, bytes_signal))
            except Exception as e:
                print(f"There was a problem pre-processing the signal, cancelling transmission. {e}.")
                return []

    # Group header and signal datum in a single 4 bytes package
    # This will create a list of 4 bytes packages that can be sent directly to the generator
    # Example ouput to channels 1 and 3: [ b"\0x01\0xff", b"\0x03\0xff", b"\0x01\0x14", b"\0x03\0x16", ... ]
    ## TODO: Properly ignore signals when header is A1 or A2.
    amount_of_channels = len([signal for header, signal in headers_and_signals_to_send if header not in ["A1","A2"]])
    signal_len = len(headers_and_signals_to_send[0][1])

    print(f"Amount of channels: {amount_of_channels}\nSignal_len: {signal_len}")
    bytes_packages = []
    for i in range(signal_len):
        for j in range(amount_of_channels):
            bytes_packages.append(b"".join([processed_headers_and_signals[j][0], processed_headers_and_signals[j][1][i]]))
    return bytes_packages, amount_of_channels


def generate_sinusoidal_waves_matching_time(amplitude, duration, frequencies, sample_rate):
        """
        Generates a single signal that contains all frequencies. Each repeated for a duration specified by parameter.
        """
        t = np.arange(0, duration*len(frequencies), 1 / sample_rate)
        signal = np.array([])

        for frequency in frequencies:
            cycle = amplitude * np.sin(2 * np.pi * frequency * np.arange(0, duration, 1/sample_rate))
            signal = np.append(signal, cycle)
        return t, signal
