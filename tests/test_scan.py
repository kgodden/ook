from unittest import TestCase
from datetime import datetime
import ook

__author__ = 'Kevin'

regex1 = '(\./)?(?P<experiment>\w+)/(?P<camera>\w+)/(?P<channel>\w+)/(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<frame>\d{1}).*'
images_path = './ridge'


class TestScan(TestCase):
    def test_scan(self):
        idx = ook.Index(images_path)
        idx.scan([ook.PathAttribute(regex1, {'timestamp': lambda v: ook.to_timestamp(datetime.strptime(v, '%Y-%m-%dT%H-%M-%S-%f'))}),
                  ook.FileSizeAttribute(),
                  ook.ImageAttribute(),
                  ])

        f = idx.filter(lambda i: True)

        self.assertEquals(26, sum(1 for _ in f.images()))