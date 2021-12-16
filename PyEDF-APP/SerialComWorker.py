#!/usr/bin/python

import serial
import sys
import glob
import re
import subprocess

"""
Class to handle the serial communication between the PC and the EDF signal generator

This class will be in charge of managing the ports and sending the data to the device
"""


class SerialComWorker():
    selected_comm_port = "" # Selected serial communication port
    generator_devices = [] # Available generator devices after checking serial ports

    def __init__(self):
        print("Serial communication worker initialized")

    def parseSerialPorts(self):
        """
        Lists serial port names.
        Raises EnvironmentError on unsupported or unknown platforms.
        Returns A list of the serial ports available on the system.
        """
        usb_devices = []
        # For linux platforms
        if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
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
        # For windows platforms
        # if sys.platform.startswith('win'):
            # TODO
        for device in usb_devices:
            if "STMicroelectronics" in str(device["tag"]):
                self.generator_devices.append(device)

    def listSerialPorts(self):
        self.parseSerialPorts()
        user_device_list = []
        # Create list to be displayed to user
        for device in self.generator_devices:
            user_device_list.append(
                "EDF signal generator: " + str(device["device"]))
        return user_device_list

    def selectCommPort(self, port):
        """
        Method to save the selected comm port
        """
        print("Selected port: " + port)
        self.selected_comm_port = port
