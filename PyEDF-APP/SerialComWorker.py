#!/usr/bin/python

import serial
import serial.tools.list_ports
import sys
import glob
import re
import subprocess

"""
Class to handle the serial communication between the PC and the EDF signal generator

This class will be in charge of managing the ports and sending the data to the device
"""


class SerialComWorker():
    chosen_device = {}  # Selected serial communication port
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
