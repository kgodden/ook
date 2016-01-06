
from unittest import TestCase

import ook
from datetime import datetime

# sync_test\camera1\white_light\0000
regex1 = '(?P<experiment>\w+)/(?P<camera>\w+)/(?P<channel>\w+)/(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<frame>\d{1}).*'
images_path = './ridge'


class TestIndex(TestCase):
    def test_scan(self):
        idx = ook.Index(images_path)
        idx.scan([ook.PathAttribute(regex1, {'timestamp': lambda v: ook.to_timestamp(datetime.strptime(v, '%Y-%m-%dT%H-%M-%S-%f'))})])

    def test_filter(self):
        idx = ook.Index(images_path)
        self.assertEquals(26, sum(1 for _ in idx.images()))

        idx1 = idx.filter(lambda p: True)
        self.assertEquals([i.name for i in idx.images()], [i.name for i in idx1.images()])

        idx2 = idx.filter(lambda p: p.name == 'image_D2015-10-27T13-31-54-576940Z_9.jpg')
        self.assertEquals(1, sum(1 for _ in idx2.images()))

        image = next(idx2.images())
        self.assertEquals('image_D2015-10-27T13-31-54-576940Z_9.jpg', image.name)
        self.assertEquals('sync_test/camera1/white_light/0000', image.path)
        self.assertEquals('sync_test', image.experiment)
        self.assertEquals('camera1', image.camera)
        self.assertEquals('white_light', image.channel)
        self.assertEquals('0000', image.dir)
        self.assertEquals('1445952714.576940', image.timestamp)
        self.assertEquals('9', image.frame)



        idx2 = idx.filter(lambda p: p.camera == 'camera1')
        self.assertEquals(3, sum(1 for _ in idx2.images()))

        idx3 = idx.filter(lambda p: p.camera == 'camera1' and p.channel == 'white_light')
        self.assertEquals(2, sum(1 for _ in idx3.images()))

        idx4 = idx.filter(lambda p: p.camera == 'camera1' and p.channel == 'white_light' and p.dir == '0000')
        self.assertEquals('image_D2015-10-27T13-31-54-576940Z_9.jpg', next(idx4.images()).name)
