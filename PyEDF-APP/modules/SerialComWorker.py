#!/usr/bin/python

import serial
import numpy as np
import serial.tools.list_ports
from modules.ChannelToIntProtocol import ProtocolDict
import sys
import glob
import re
import subprocess
import time
from modules.utils import timeit


"""
Class to handle the serial communication between the PC and the EDF signal generator

This class will be in charge of managing the ports and sending the data to the device
"""

CHANNEL_AMOUNT_CONFIG = 39
SAMPLE_RATE_CONFIG = 40

class SerialComWorker():
    chosen_device = ""  # Selected serial communication port
    """
    List of key-value pairs of EDF signal generators found. Should contain:
    Name: Identifier for the device
    Device: String used to open and close the port (COMx for Windows)
    """
    generator_devices = []  # Available generator devices after checking serial ports

    def __init__(self):
        print("Serial communication worker initialized")

    def listSerialPorts(self):
        """
        Method to create a list of all corresponding EDF signal generator devices
        """
        self.generator_devices = self.searchCommPorts()
        user_device_list = []
        if self.generator_devices:
            # Create list to be displayed to user
            for device in self.generator_devices:
                user_device_list.append(str(device.device))
            return user_device_list
        else:
            return []

    def searchCommPorts(self):
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

    def selectCommPort(self, user_chosen_device):
        """
        Method to save the selected comm port
        """
        # Check that devices are loaded
        if self.generator_devices:
            # Go through loaded devices and check if name is in user_chosen_device
            for device in self.generator_devices:
                if device.name in user_chosen_device:
                    print("Selected port: " + device.name)
                    self.chosen_device = device

    def create_config_package(self, config_num: int, config_data: int):
        """
        This method creates a custom configuration package to send config_data to the microcontroller.
        """
        enum_pkg = int(config_num).to_bytes(2, byteorder="big", signed=False)
        data_pkg = int(config_data).to_bytes(2, byteorder="big", signed=False)
        return b"".join([enum_pkg, data_pkg])

    @timeit
    def beginTransmision(self, bytes_packages: list, channels_amount, sample_rate):
        """
        Method to start the transmition to the generator
        """
        ## With this implementation we could make a single call to serial.write(configurations) for all configurations
        ## sending them packeted as the bytes_package
        # configurations = []
        # configurations.append(self.create_config_package(SAMPLE_RATE_CONFIG, sample_rate))
        # configurations.append(self.create_config_package(CHANNEL_AMOUNT_CONFIG, channels_amount))


        config_sample_rate_package = self.create_config_package(SAMPLE_RATE_CONFIG, sample_rate)
        config_channel_amount_pkg = self.create_config_package(CHANNEL_AMOUNT_CONFIG, channels_amount)

        bytes_packages_packeted = [bytes_packages[i:i+64] for i in range(0,len(bytes_packages),64)]

        print(f"len of bytes_packages = {len(bytes_packages)}")
        print(f"sample rate = {sample_rate}")
        print(f"config_sample_rate_package = {config_sample_rate_package}")
        print(f"config_data_channels = TODO")
       # print(f"packeted bytes_packages is: {bytes_packages_packeted}")


        serial_connection = serial.Serial(self.chosen_device.name, baudrate=115200, bytesize=serial.EIGHTBITS)

        serial_connection.write(serial.to_bytes(config_sample_rate_package))
        time.sleep(0.1)
        # Send the amount of channels as a configuration
        serial_connection.write(serial.to_bytes(config_channel_amount_pkg))
        
        for byte_pkg in bytes_packages_packeted:
            #for j in range(channels_amount):
            serial_connection.write(b"".join(byte_pkg))

        serial_connection.close()

        # print(f'package ={serial.to_bytes(package)}')
        # Looping test function. Needs to change since DAC_A not working
        #MSBy = 0x00
        #LSBy = 0x00
        # while True:
        #
        #    if LSBy > 0xff:
        #        MSBy += 1
        #        LSBy = 0x00
        #    if MSBy == 0xff:
        #        MSBy = 0x00
        #
        #    cw = [MSBy,LSBy]
        #    print (serial.to_bytes(cw))
        #    ser.write(serial.to_bytes(cw))
        #    LSBy += 1
