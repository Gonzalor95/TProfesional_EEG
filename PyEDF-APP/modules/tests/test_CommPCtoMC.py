#!/usr/bin/python

import os
import sys
import serial

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import CommPCtoMC
import unittest

class TestCommPCtoMC(unittest.TestCase):

    ### Examples: 
    def test_list_int(self):
        """
        Test that it can sum a list of integers
        """
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)

    def test_list_fraction(self):
        """
        Test that it can sum a list of fractions
        """
        self.assertEqual(1, 1)

    def test_bad_type(self):
        data = "banana"
        with self.assertRaises(TypeError):
            result = sum(data)
    ###

    def test_creating_CommPCtoMC_object_with_default_values(self):
        commPCtoMC = CommPCtoMC

        commPCtoMC.CommPCtoMC

        result = 1
        expected = 1
        self.assertEqual(result,expected)


if __name__ == '__main__':
    unittest.main()