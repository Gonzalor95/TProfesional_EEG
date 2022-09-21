
import serial

ser = serial.Serial('COM6')  # open serial port


print (ser.name)


i = 0
#while True:
#    i_tobytes = i.to_bytes(2, 'big')
#    ser.write(i_tobytes)
#    i += 1
#    if i > 256:
#        i = 0
ser.write(b'h')
ser.close()




