
import serial

ser = serial.Serial('COM6')  # open serial port


print (ser.name)


#MSBy = 0x00
#LSBy = 0x00
#while True:
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

config_MSB = 5
config_LSB = 0

data_MSB = 0xff
data_LSB = 0xff

cw = [config_MSB, config_LSB, data_MSB, data_LSB]

print (serial.to_bytes(cw))
while True:
    ser.write(serial.to_bytes(cw))

ser.close()




