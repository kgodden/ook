from unittest import TestCase

__author__ = 'Kevin'

import ook

regex1 = '(?P<experiment>\w+)/(?P<camera>\w+)/\w+_(?P<channel>\w+)/\w+_(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<frame>\d{1}).*'
path1 = 'ccm20/new_dir15/new_dir15_Stills/new_dir15_0002/image_D2015-10-24T14-13-38-286378Z_1'


class TestPathAttribute(TestCase):
    def test___init__(self):
        ook.PathAttribute(regex1, '')


class TestPathAttribute(TestCase):
    def test_names(self):
        attribute = ook.PathAttribute(regex1, '')
        values = attribute.names()
        self.assertEquals(values, ['experiment', 'camera', 'channel', 'dir', 'timestamp', 'frame'])


class TestPathAttribute(TestCase):
    def test_evaluate(self):
        attribute = ook.PathAttribute(regex1, '')
        values = attribute.evaluate(path1)
        self.assertEquals(values, ['ccm20', 'new_dir15', 'Stills', '0002', '2015-10-24T14-13-38-286378', '1'])
