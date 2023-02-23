import serial
import numpy as np
#import mne
import pyedflib
import matplotlib.pyplot as plt

######################## diff signal separation test
#
#time = np.arange(0, 1, 1 / 500)
#s1 = np.sin(2*np.pi * 10 * time)
#s2 = 2 * np.sin(2*np.pi * 50 * time)
#s3 = 3 * np.sin(2*np.pi * 20 * time)
#
#s_diff = s1 - s2
#s_diff2 = s2 - s3
#
## Calculate the common mode signal
#mean = np.mean(s_diff)
#mean2 = np.mean(s_diff2)
## Subtract the common mode signal from the differential signal
#signal_diff_zero_mean = s_diff - mean
#signal_diff_zero_mean2 = s_diff2 - mean2
#
## Add the common mode signal to the differential signal with a zero mean
#signal_common1 = mean + signal_diff_zero_mean
#signal_common2 = mean - signal_diff_zero_mean
#signal_common3 = mean2 + signal_diff_zero_mean2
#signal_common4 = mean2 - signal_diff_zero_mean2
#
#fig, axis = plt.subplots(5, squeeze=False)
#axis[0][0].plot(time, signal_common1, color=([168/255, 193/255, 5/255]), linewidth=0.4)
#axis[0][0].set_ylabel("s1", rotation=0, labelpad=30)
#axis[1][0].plot(time, signal_common2, color=([168/255, 193/255, 5/255]), linewidth=0.4)
#axis[1][0].set_ylabel("s2", rotation=0, labelpad=30)
#axis[2][0].plot(time, signal_common3, color=([168/255, 193/255, 5/255]), linewidth=0.4)
#axis[2][0].set_ylabel("s2", rotation=0, labelpad=30)
#axis[3][0].plot(time, signal_common4, color=([168/255, 193/255, 5/255]), linewidth=0.4)
#axis[3][0].set_ylabel("s3", rotation=0, labelpad=30)
## axis[4][0].plot(time, signal_common1- signal_common2, color=([168/255, 193/255, 5/255]), linewidth=0.4)
## axis[4][0].set_ylabel("s-s", rotation=0, labelpad=30)
#plt.show()
#

# # Open the EDF file
# f = pyedflib.EdfReader('my_file.edf')

# # Select the two channels that were used to generate the differential signal
# channel1 = 0
# channel2 = 1

# # Read the data from the EDF file
# data1 = f.readSignal(channel1)
# data2 = f.readSignal(channel2)

# # Calculate the differential signal
# signal_diff = data1 - data2

# # Calculate the common mode signal
# signal_common = (data1 + data2) / 2

# # Subtract the common mode signal from the differential signal to obtain the signal with zero mean
# signal_diff_zero_mean = signal_diff - signal_common

# # Add back the two electrode signals with a zero mean to obtain the two original signals
# signal1 = signal_common + signal_diff_zero_mean
# signal2 = signal_common - signal_diff_zero_mean


######################## bytes test

channel = 8
data = 4000
config_bytes = channel.to_bytes(1, byteorder="big", signed=False)
data_bytes = data.to_bytes(2, byteorder="big", signed=False)
print(config_bytes)
print(data_bytes)
package = [config_bytes, data_bytes]
package2 = b"".join(package)
print (package)
print (package2)
print (type(package2))


######################## Serial test

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
