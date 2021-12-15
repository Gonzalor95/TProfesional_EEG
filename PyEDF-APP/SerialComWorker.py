#!/usr/bin/python

import serial
import sys
import glob

"""
Class to handle the serial communication between the PC and the EDF signal generator

This class will be in charge of managing the ports and sending the data to the device
"""


class SerialComWorker():
    selected_comm_port = ""

    def __init__(self):
        print("Serial communication worker initialized")

    def listSerialPorts(self):
        """
        Lists serial port names.
        Raises EnvironmentError on unsupported or unknown platforms.
        Returns A list of the serial ports available on the system.
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def selectCommPort(self, port):
        """
        Method to save the selected comm port
        """
        print("Selected port: " + port)
        self.selected_comm_port = port
