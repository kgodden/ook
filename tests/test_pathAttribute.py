from unittest import TestCase

import ook
from datetime import datetime

regex1 = '(?P<client>\w+)/(?P<experiment>\w+)/(?P<camera>\w+)/\w+_(?P<channel>\w+)/\w+_(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<frame>\d{1}).*'
path1 = 'ridge/ccm20/new_dir15/new_dir15_Stills/new_dir15_0002/image_D2015-10-24T14-13-38-286378Z_1'

regex2 = '(\./)?(?P<client>\w+)/(?P<experiment>\w+)/(?P<camera>\w+)/(?P<channel>\w+)/(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<frame>\d{1}).*'
path2 = 'ridge/sync_test/camera1/structured_light/0000/image_D2015-10-27T13-26-52-302857Z_9.jpg'


class TestPathAttribute(TestCase):
    def test___init__(self):
        ook.PathAttribute(regex1)

    def test_names(self):
        attribute = ook.PathAttribute(regex1)
        values = attribute.names()
        self.assertEquals(values, ['client', 'experiment', 'camera', 'channel', 'dir', 'timestamp', 'frame'])

    def test_evaluate(self):
        attribute = ook.PathAttribute(regex1)
        values = attribute.evaluate(path1)
        self.assertEquals(values, ['ridge', 'ccm20', 'new_dir15', 'Stills', '0002', '2015-10-24T14-13-38-286378', '1'])

        attribute = ook.PathAttribute(regex2)
        values = attribute.evaluate(path2)
        self.assertEquals(values,
                          ['ridge', 'sync_test', 'camera1', 'structured_light', '0000', '2015-10-27T13-26-52-302857',
                           '9'])

        # test with timestamp as a fractional seconds number
        attribute = ook.PathAttribute(regex2,
                                      {'timestamp': lambda v: ook.to_timestamp(
                                          datetime.strptime(v, '%Y-%m-%dT%H-%M-%S-%f'))}
                                      )

        values = attribute.evaluate(path2)
        self.assertEquals(values,
                          ['ridge', 'sync_test', 'camera1', 'structured_light', '0000', '1445952412.302857', '9'])
