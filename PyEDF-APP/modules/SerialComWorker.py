#!/usr/bin/python

import serial
import numpy as np
import serial.tools.list_ports
from modules.ChannelToIntProtocol import ProtocolDict
import sys
import glob
import re
import subprocess

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

    def beginTransmision(self, signals, sample_rate, channels):
        """
        Method to start the transmition to the generator
        """
        serial_connection = serial.Serial(self.chosen_device)
        trigger = np.uint16(33)  # Using numpy ints to make sure size is 16 bits
        LDAC_trigger_package = bytearray([0, trigger, 0, 0])

        # For each data type we will need to do this:
        channel = 8
        data = 453
        config_bytes = channel.to_bytes(1, byteorder="big", signed=False)
        data_bytes = data.to_bytes(2, byteorder="big", signed=True)

        print(config_bytes)
        print(data_bytes)

        config_MSB = 0
        config_LSB = 8
        data_MSB = 0xFf
        data_LSB = 0xff
        package = [config_MSB, config_LSB, data_MSB, data_LSB]

        print(serial.to_bytes(package))
        serial_connection.write(serial.to_bytes(package))

        # Trigger LDAC after filling all channels:
        serial_connection.write(serial.to_bytes(LDAC_trigger_package))

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
