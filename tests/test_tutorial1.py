import daetools.examples.tutorial1 as tutorial1
import unittest
import tempfile
import json
import sys
import io

from daetools.pyDAE.data_reporters import daeJSONFileDataReporter

class TestTutorial1(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_file = tempfile.NamedTemporaryFile(dir='/tmp')

    def test_run(self):

        suppress_text = io.StringIO()
        sys.stdout = suppress_text

        dr=daeJSONFileDataReporter()
        dr.Connect(self.test_file.name, "tutorial1")
        tutorial1.run(datareporter=dr)

        with open(self.test_file.name) as f:
            data = json.load(f)

        self.assertEqual(data['rho']['Values'][0], 8960)
