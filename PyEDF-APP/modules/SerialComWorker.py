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

    @timeit
    def beginTransmision(self, bytes_packages: list, channels_amount, sample_rate):
        """
        Method to start the transmition to the generator
        """

        enum_sample_rate_package = int(40).to_bytes(2, byteorder="big", signed=False)
        data_sample_rate_package = int(sample_rate).to_bytes(2, byteorder="big", signed=False)
        config_sample_rate_package  = b"".join([enum_sample_rate_package, data_sample_rate_package])
 
        print(f"len of bytes_packages = {len(bytes_packages)}")
        print(f"sample rate = {sample_rate}")
        print(f"config_sample_rate_package = {config_sample_rate_package}")
        print(f"bytes_packages is: {bytes_packages}")

        serial_connection = serial.Serial(self.chosen_device.name, baudrate=115200, bytesize=serial.EIGHTBITS)

        serial_connection.write(serial.to_bytes(config_sample_rate_package))
        
        for i in range(len(bytes_packages)):
            #for j in range(channels_amount):
            serial_connection.write(bytes_packages[i])

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
