
import serial

ser = serial.Serial('COM3')  # open serial port

print (ser.name)

ser.write(b"1")
ser.close()
