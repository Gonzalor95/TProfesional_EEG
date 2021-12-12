#!/usr/bin/python

import serial

ser = serial.Serial('COM3', 115200)

print(ser.name)         # check which port was really used
ser.write(b'Esto esta escrito desde python')     # write a string
ser.close()             # close port
