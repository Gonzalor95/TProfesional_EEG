#!/usr/bin/python

# Informe de Avance: https://docs.google.com/document/d/1EIHrQZklle4uGBhgkOXfJJSVN3VgxFF6GjC-wz1y94w 
import serial
import logging

# TODO:
    ## Señales de prueba:
        # Pulsos (duracion de test, frec, duty cycle, etc.)
        # Triangular (duracion, triangular o diente, frec, etc.)
        # Senoidal (duracion, frec, etc.)
    ## Send batch of data


## Protocol Dictionary (Leer del informe de avance. Y tiene que ser igual al codigo del MC)
channel_config_enum_dict = {
    # DAC A
    "CH_Fp1": 0, "CH_Fz": 1,	"CH_Fp2": 2,	"CH_F3": 3,	"CH_F4": 4,	"CH_C3": 5,	"CH_C4": 6,	"CH_P3": 7,
    # DAC B
    "CH_P4": 8,	"CH_O1": 9,	"CH_O2": 10, "CH_F7" : 11,	"CH_F8" : 12,	"CH_T7" : 13,	"CH_T8" : 14,	"CH_P7" : 15,
    # DAC C
    "CH_P8": 16, "CH_Pz": 17, "CH_Cz" : 18,	"CH_PG1": 19,	"CH_PG2": 20,	"CH_AFz": 21,	"CH_FCz": 22,	"CH_CPz": 23,
    # DAC D
    "CH_CP3": 24, "CH_CP4": 25, "CH_FC3": 26,	"CH_FC4": 27,	"CH_TP7": 28,	"CH_TP8": 29,	"CH_FT7": 30,	"CH_FT8": 31,
    # Reserved:
    "MAX_DAC_CHANNEL_WORD": 32,
}

"""
Class to control communication between PC and EEG generator device
"""

class CommPCtoMC():

    ser_comm_port_obj = None

    def __init__(self, str_com_port = 'COM6'):
        try:
            self.ser_comm_port_obj = serial.Serial(str_com_port)  # open serial port
            print("PC to device communication interface initialized")
        except Exception as err:
            logging.exception(f'Can not open port "{str_com_port}".')
            raise

    def __str__(self):
        return f"Using port: {self.ser_comm_port_obj.name}"
            

    def send_word(self, config_word = channel_config_enum_dict["MAX_DAC_CHANNEL_WORD"], data_word = 0):
        """
        Sends a single word to the device
        """
        # The com protocol is designed to recieve a word of 32 bytes each time.
        # First 16 bytes for Config identification
        # Lates 16 bytes for data/instruction

        config_MSB = 0
        config_LSB = 8

        data_MSB = 0xFf
        data_LSB = 0xff

        cw = [config_MSB, config_LSB, data_MSB, data_LSB]

        print (serial.to_bytes(cw))
        self.ser_comm_port_obj(serial.to_bytes(cw))
