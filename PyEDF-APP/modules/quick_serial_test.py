import serial

## This function will communicate via USB with Project

ser = serial.Serial('COM6')  # open serial port. Verify for your computer

print (ser.name)

config_MSB = 0
config_LSB = 8

data_MSB = 0xFf
data_LSB = 0xff

cw = [config_MSB, config_LSB, data_MSB, data_LSB]

print (serial.to_bytes(cw))
ser.write(serial.to_bytes(cw))

## TRIGGER LDAC:
config_MSB = 0
config_LSB = 33
cw = [config_MSB, config_LSB, data_MSB, data_LSB]
print (f'This word should be config = 33 and data = xx (does not matter). cw ={serial.to_bytes(cw)}')
ser.write(serial.to_bytes(cw))

ser.close()


## Looping test function. Needs to change since DAC_A not working
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

