from unittest import TestCase

import ook

# sync_test\camera1\white_light\0000
regex1 = '(?P<experiment>\w+)/(?P<camera>\w+)/(?P<channel>\w+)/(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<frame>\d{1}).*'
images_path = './ridge'

class TestIndex(TestCase):
    def test_scan(self):
        index = ook.Index(images_path)
        index.scan([ook.PathAttribute(regex1)])
