#!/usr/bin/python

class ProtocolDict():
    # Protocol Dictionary (matches what the generator protocol interface describes)
    channel_enum_dict_ = {
        # DAC A
        "Fp1": 0, "Fz": 1, "Fp2": 2, "F3": 3, "F4": 4, "C3": 5, "C4": 6, "P3": 7,
        # DAC B
        "P4": 8, "O1": 9, "O2": 10, "F7": 11, "F8": 12, "T7": 13, "T8": 14, "P7": 15,
        # DAC C
        "P8": 16, "Pz": 17, "Cz": 18, "PG1": 19, "PG2": 20, "AFz": 21, "FCz": 22, "CPz": 23,
        # DAC D
        "CP3": 24, "CP4": 25, "FC3": 26, "FC4": 27, "TP7": 28, "TP8": 29, "FT7": 30, "FT8": 31
    }

    # Used to look for channels in the edf file. Some may have aliases (two names for the same channel). See Contect EEG image, T3/T7 channels
    possible_channels_array_ = ["Fp1", "Fz", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2", "F7", "F8", "T7", "T3", "T8", "T4",
                                "P7", "T5", "P8", "T6", "Pz", "Cz", "PG1", "PG2", "AFz", "FCz", "CPz", "CP3", "CP4", "FC3", "FC4", "TP7", "TP8", "FT7", "FT8"]

    # Some connectors in the Contec EEg have two names assigned. This dict will be used to map those aliases to the name we give those
    alias_dict_ = {"T3": "T7", "T5": "P7", "T4": "T8", "T6": "P8"}
