import unittest

from popcoder import util


class TestUtil(unittest.TestCase):

    def test_seconds_to_timecode(self):
        self.assertEqual(util.seconds_to_timecode(1), '00:00:01')

    def test_percent_to_px(self):
        self.assertEqual(util.percent_to_px(100, 0.5), 0.5)
