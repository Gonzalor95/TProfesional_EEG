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
    selected_comm_port = ""  # Selected serial communication port
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
        self.parseSerialPorts()
        user_device_list = []
        if self.generator_devices:
            # Create list to be displayed to user
            for device in self.generator_devices:
                user_device_list.append(str(device.device))
            return user_device_list
        else:
            return []

    def parseSerialPorts(self):
        """
        Lists serial port names.
        Raises EnvironmentError on unsupported or unknown platforms.
        Returns A list of the serial ports available on the system.
        """
        # For linux platforms
        if sys.platform.startswith('linux'):
            self.generator_devices = self.searchLinuxCommPorts()
            return
        # For windows platforms
        if sys.platform.startswith('win'):
            self.generator_devices = self.searchWindowsCommPorts()
            return

    def searchLinuxCommPorts(self):
        """
        Method to look for connected EDF signal generator devices in Linux

        Returns a list of serial comm devices with key-value pairs containing information about it
        """
        # TODO: Change to save the devices the same way as the WIndows method does. Follow generator_devices format
        usb_devices = []
        device_re = re.compile(
            b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        df = subprocess.check_output("lsusb")
        for i in df.split(b'\n'):
            if i:
                info = device_re.match(i)
                if info:
                    dinfo = info.groupdict()
                    # Convert from bytes to str if value is not already a string
                    for key in dinfo.keys():
                        try:
                            dinfo[key] = dinfo[key].decode("utf-8")
                        except(UnicodeDecodeError, AttributeError):
                            continue
                    # Build the "device" key-value
                    dinfo['device'] = '/dev/bus/usb/%s/%s' % (
                        dinfo.pop('bus'), dinfo.pop('device'))
                    usb_devices.append(dinfo)
        generator_devices = []
        for device in usb_devices:
            if "STMicroelectronics" in str(device["tag"]):
                generator_devices.append(device)
        return generator_devices

    def searchWindowsCommPorts(self):
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
                    self.selected_comm_port = device.name
