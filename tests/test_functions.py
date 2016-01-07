from unittest import TestCase

__author__ = 'Kevin'
import ook
from datetime import datetime


class TestFunctions(TestCase):
    def test_to_timestamp(self):
        time = datetime.strptime('2015-10-27T13-26-52-302857', '%Y-%m-%dT%H-%M-%S-%f')
        ts = ook.to_timestamp(time)

        # check the fractional representation
        self.assertEquals('1445952412.302857', ts)

        # And convert it back anf make sure it matches
        time = datetime.utcfromtimestamp(float(ts))
        self.assertEquals(str(time), '2015-10-27 13:26:52.302857')

