from unittest import TestCase
import ook


class TestImageBrightnessAttribute(TestCase):
    def test_names(self):
        attribute = ook.ImageAttribute()
        values = attribute.names()
        self.assertEquals(['min', 'mean', 'max'], values)

    def test_evaluate(self):
        attribute = ook.ImageAttribute()
        vals = attribute.evaluate('ridge/sync_test/camera1/white_light/0001/image_D2015-10-27T13-32-19-905038Z_9.jpg', '.')
        self.assertEquals('7', vals[0])
        self.assertEquals('54', vals[1])
        self.assertEquals('234', vals[2])
