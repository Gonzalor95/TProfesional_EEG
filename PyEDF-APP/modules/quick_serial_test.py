
import serial

ser = serial.Serial('/dev/ttyACM0')  # open serial port

print (ser.name)

ser.write(b"1")
ser.close()
