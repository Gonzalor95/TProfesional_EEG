#!/usr/bin/python

import os
import sys
import serial

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import CommPCtoMC
import unittest
from unittest import mock
from unittest.mock import patch



## Instanciar con CommPCtoMC.CommPCtoMC('None') ya que con el default falla si no hay nada conectado

class TestCommPCtoMC(unittest.TestCase):

    def test_creating_CommPCtoMC_object_with_None_parameter(self):
        commPCtoMC = CommPCtoMC.CommPCtoMC(None)

        result = commPCtoMC.__str__()
        expected = "Using port: None"

        self.assertEqual(result,expected)


if __name__ == '__main__':
    os.system('cls') ## Clear screen
    unittest.main()