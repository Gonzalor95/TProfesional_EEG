
import serial

ser = serial.Serial('COM6')  # open serial port


print (ser.name)


MSBy = 0x00
LSBy = 0x00
while True:

    if LSBy > 0xff:
        MSBy += 1
        LSBy = 0x00
    if MSBy == 0xff:
        MSBy = 0x00

    cw = [MSBy,LSBy]
    print (serial.to_bytes(cw))
    ser.write(serial.to_bytes(cw))
    LSBy += 1
cw = [0xff,0xff]
print (serial.to_bytes(cw))
ser.write(serial.to_bytes(cw))
ser.close()




