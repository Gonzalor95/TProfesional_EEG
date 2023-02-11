#!/usr/bin/python

import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import random
import serial
import CommPCtoMC
import unittest
from unittest import mock
from unittest.mock import patch
import matplotlib.pyplot as plt



## Instanciar con CommPCtoMC.CommPCtoMC('None') ya que con el default falla si no hay nada conectado

class TestCommPCtoMC(unittest.TestCase):

    def test_creating_CommPCtoMC_object_with_None_parameter(self):
        commPCtoMC = CommPCtoMC.CommPCtoMC(None)

        result = commPCtoMC.__str__()
        expected = "Using port: None"

        self.assertEqual(result,expected)


class TestMiscFunctions(unittest.TestCase):

    @unittest.skip("Comment to see, but only a test to demostrate")
    def test_dummy_plot(self):

        plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'ro')
        plt.axis([0, 6, 0, 20])
        plt.xlabel('entry a')
        plt.ylabel('entry b')
        plt.title('Dummy plot')
        plt.show()

        self.assertTrue(True)

    def test_plot_pulse_function(self):

        x = [1, 2, 3, 4]
        y = [1, 4, 9, 16]


        plt.plot(x, y)
        plt.xlabel('entry a')
        plt.ylabel('entry b')
        plt.title('Dummy plot')
        plt.show()

        self.assertTrue(True)



if __name__ == '__main__':
    os.system('cls') ## Clear screen
    unittest.main()