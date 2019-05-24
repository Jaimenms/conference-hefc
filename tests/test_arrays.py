import unittest
import numpy as np

class TestArrays(unittest.TestCase):

    def test_arrays(self):

        a = np.matrix('1 2; 3 4')
        b = np.matrix('-2 -3;-4 -5')
        c = np.invert(a)

        self.assertEqual(c[0, 0], b[0, 0])
        self.assertEqual(c[1,1],b[1,1])
