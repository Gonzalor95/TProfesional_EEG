import modules.utils
import modules.TestingSignals
import matplotlib.pyplot as plt
from gui_elements.PopUpWindow import PopUpWindow
from PyQt5.QtWidgets import *
from modules.ChannelToIntProtocol import ProtocolDict
import os

def to_bytes_packages(is_testing_signal, headers_and_signals_to_send):
    """
    Pre-processes the signals before beginning the transmision
    """
    # We will need to adequate the signal before beginning the transmition. Every pre-processing that can be done before the transmission is time we save
    # - Convert the channel names from strings to a byte by mapping then with the dict, then applying "to_bytes"
    # - Convert the signal data to 2 bytes using the "to_bytes" method
    # Output format: [ (b"0x01", [b"0xff", b"0x1e", ...),  (b"0x04", [b"0xff", b"0x1e", ...), ...]
    processed_headers_and_signals = []

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

    # Group header and signal datum in a single 4 bytes package
    # This will create a list of 4 bytes packages that can be sent directly to the generator
    # Example ouput to channels 1 and 3: [ b"\0x01\0xff", b"\0x03\0xff", b"\0x01\0x14", b"\0x03\0x16", ... ]

    amount_of_channels = len(headers_and_signals_to_send)
    signal_len = len(headers_and_signals_to_send[0][1])

    bytes_packages = []
    for i in range(signal_len):
        for j in range(amount_of_channels):
            bytes_packages.append(b"".join([processed_headers_and_signals[j][0], processed_headers_and_signals[j][1][i]]))

    return bytes_packages



testingSignalWorker = modules.TestingSignals.TestingSignalsWorker(1)

testingSignalWorker.generateTestingSignal("Sinusoidal",22,50,2048,1) ## --> Aca fuerza a usar todos los canales

testingSignalWorker.setSelectedSimTime([0,1])

simulation_signals = testingSignalWorker.getSimulationSignals()


print([simulation_signals[0]]) ## -> tira solo Fp1. Hasta aca todo bien
print("")
print("hasta aca, todo bien")
print("")

plt.plot(simulation_signals[0][1])
plt.show()


bytes_packages = to_bytes_packages(True, [simulation_signals[0]])

falopath = os.path.join(os.curdir,"FALOPA")
os.makedirs(falopath, exist_ok=True)

with open(os.path.join(falopath, "Falopa.txt"), "w+") as falofile:
    for byte in bytes_packages:
        falofile.write(str(byte))

back_signal = []
for byte in bytes_packages:
    back_signal.append(int.from_bytes(byte, byteorder='big'))


print(back_signal)

plt.plot(back_signal)
plt.show()





