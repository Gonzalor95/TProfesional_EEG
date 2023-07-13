#!/usr/bin/python

import serial
import serial.tools.list_ports
import time
from modules.utils import timeit


class SerialComWorker():
    """
    Class to handle the serial communication between the PC and the EDF signal generator

    This class will be in charge of managing the ports and sending the data to the device
    """
    def __init__(self, config):
        self.config_params_ = config
        print("Serial communication worker initialized")

    def listSerialPorts(self):
        """
        Method to create a list of all corresponding EDF signal generator devices.

        Callback for the GUI interaction
        """
        self.generator_devices_ = self.searchCommPortsWindows_()
        user_device_list = []
        if self.generator_devices_:
            # Create list to be displayed to user
            for device in self.generator_devices_:
                user_device_list.append(str(device.device))
            return user_device_list
        else:
            return []

    def selectCommPort(self, user_chosen_device):
        """
        Method to save the selected comm port.

        Callback for the GUI interaction
        """
        # Check that devices are loaded
        if self.generator_devices_:
            # Go through loaded devices and check if name is in user_chosen_device
            for device in self.generator_devices_:
                if device.name in user_chosen_device:
                    print("Selected port: " + device.name)
                    self.chosen_device_ = device

    @timeit
    def beginTransmision(self, bytes_packages: list, channels_amount, sample_rate):
        """
        Method to start the transmition to the generator.

        Callback for the GUI interaction
        """
        config_sample_rate_pkg = self.createConfigPackage_(self.config_params_["config_sample_rate"], sample_rate)
        config_channel_amount_pkg = self.createConfigPackage_(self.config_params_["config_channels_amount"], channels_amount)
        config_reset_all_dacs_pkg = self.createConfigPackage_(self.config_params_["config_reset_all_dacs"], channels_amount)
        data_pkgs = [bytes_packages[i:i+64] for i in range(0,len(bytes_packages),64)]

        try:
            # Start serial connection
            serial_connection = serial.Serial(self.chosen_device_.name, baudrate=115200, bytesize=serial.EIGHTBITS, write_timeout=5)

            # Write sample rate config
            serial_connection.write(serial.to_bytes(config_sample_rate_pkg))
            time.sleep(0.1)

            # Write amount of channels config
            serial_connection.write(serial.to_bytes(config_channel_amount_pkg))

            for byte_pkg in data_pkgs:
                #for j in range(channels_amount):
                serial_connection.write(b"".join(byte_pkg))


            # When simulation ended, we reset outputs and configs of DACs:
            serial_connection.write(serial.to_bytes(config_reset_all_dacs_pkg))
            

            # End serial connection
            serial_connection.close()
            return True
        except serial.SerialTimeoutException:
            print("Serial write operation timed out, try resetting the device")
            return False


    ###### Private ######

    """
    List of key-value pairs of EDF signal generators found. Should contain:
    Name: Identifier for the device
    Device: String used to open and close the port (COMx for Windows)
    """
    generator_devices_ = []
    chosen_device_ = ""  # Selected serial communication port

    def searchCommPortsWindows_(self):
        """
        Method to look for connected EDF signal generator devices in Windows

        Returns a list of serial comm devices with key-value pairs containing information about it

        It uses the PID 0483 to identify the STMicroelectronics device and 5740 for the Virtual COMM port
        """
        generator_devices = []
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if ("0483" and "5740") in port.hwid:
                device = {}
                device["Name"] = port.name
                device["Device"] = port.device
                generator_devices.append(port)
        return generator_devices

    def createConfigPackage_(self, config_num: int, config_data: int):
        """
        This method creates a custom configuration package to send config_data to the microcontroller.
        """
        enum_pkg = int(config_num).to_bytes(2, byteorder="big", signed=False)
        data_pkg = int(config_data).to_bytes(2, byteorder="big", signed=False)
        return b"".join([enum_pkg, data_pkg])
