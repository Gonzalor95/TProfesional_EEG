import serial
import numpy as np

channel = 8
data = 4000
config_bytes = channel.to_bytes(2, byteorder="big", signed=False)
data_bytes = data.to_bytes(2, byteorder="big", signed=False)

print(config_bytes)
print(data_bytes)

package = [config_bytes, data_bytes]
package2 = b"".join(package)
print (package)
print (package2)
print (type(package2))


# ser = serial.Serial('COM6')  # open serial port. Verify for your computer

# print (ser.name)

# config_MSB = 0
# config_LSB = 8

# data_MSB = 0xFf
# data_LSB = 0xff

# cw = [config_MSB, config_LSB, data_MSB, data_LSB]

# print (serial.to_bytes(cw))
# ser.write(serial.to_bytes(cw))

# ## TRIGGER LDAC:
# config_MSB = 0
# config_LSB = 33
# cw = [config_MSB, config_LSB, data_MSB, data_LSB]
# print (f'This word should be config = 33 and data = xx (does not matter). cw ={serial.to_bytes(cw)}')
# ser.write(serial.to_bytes(cw))

# ser.close()


# Looping test function. Needs to change since DAC_A not working
#MSBy = 0x00
#LSBy = 0x00
# while True:
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
