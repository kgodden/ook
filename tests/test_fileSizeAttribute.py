from unittest import TestCase

__author__ = 'Kevin'

import ook


class TestFileSizeAttribute(TestCase):
    def test_names(self):
        attribute = ook.FileSizeAttribute()
        values = attribute.names()
        self.assertEquals(['file_size'], values)

    def test_evaluate(self):
        attribute = ook.FileSizeAttribute()
        size = attribute.evaluate('ridge/sync_test/camera1/structured_light/0000/image_D2015-10-27T13-26-52-302857Z_9.jpg')
        self.assertEquals(121278, size)
