#!/usr/bin/python


import argparse
import fnmatch
import os
import time
import re
from datetime import datetime
from decimal import *
import ook
import ook.kurtosis_attribute
import ook.brightness_attribute

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="The root path to the images directory tree")
args = parser.parse_args()

path = args.path

#regex1 = '(\./)?(?P<client>\w+)/(?P<experiment>\w+)/(?P<camera>\w+)/(?P<channel>\w+)/(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<frame>\d{1}).*'
#regtxt = '(?P<session>\w+)/(?P<camera>\w+)/\w+_(?P<type>\w+)/\w+_(?P<dir>\d+)(_c)?/image_D(?P<timestamp>.*)Z_(?P<channel>\d{1}).*'
#regtxt = '\w+_(?P<dir>\d+)(_c)?/image_D(?P<timestamp>.*)Z_(?P<channel>\d{1}).*'
regtxt = '(?P<camera>\w+)/\w+_(?P<type>\w+)/\w+_(?P<dir>\d+)(_c)?/image_D(?P<timestamp>.*)Z_(?P<channel>\d{1}).*'

idx = ook.Index(path)
idx.scan([ook.PathAttribute(regtxt, {'timestamp': lambda v: ook.to_timestamp(datetime.strptime(v, '%Y-%m-%dT%H-%M-%S-%f'))}),
          #ook.FileSizeAttribute(),
          #ook.ImageAttribute(),
          #ook.kurtosis_attribute.KurtosisAttribute(),
          ook.brightness_attribute.BrightnessAttribute(),
          ])
