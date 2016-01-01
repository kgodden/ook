__author__ = 'Kevin Godden'

import csv
import os
import time
import re
import fnmatch
from datetime import datetime
from decimal import Decimal
import operator


def to_timestamp(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return Decimal(delta.days*86400+delta.seconds)+Decimal(delta.microseconds/1000000.0).quantize(Decimal('.000001'))

# idx.add_attributes(
#   PathAttribute(
#       '(?P<session>\w+)/(?P<camera>\w+)/\w+_(?P<type>\w+)/\w+_(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<channel>\d{1}).*',
#       {
#           'session': lambda m: m.groups('session'),
#           'camera': lambda m: m.groups('camera'),
#           'type': lambda m: m.groups('type'),
#           'dir': lambda m: m.groups('dir'),
#
#             'timestamp': lambda v: to_timestamp(datetime.strptime(m.groups('timestamp'), '%Y-%m-%dT%H-%M-%S-%f'))
#           'channel': lambda m: m.groups('channel'),
#
#           }
# ))

# idx.add_attributes(
#   PathAttribute(
#       '(?P<session>\w+)/(?P<camera>\w+)/\w+_(?P<type>\w+)/\w+_(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<channel>\d{1}).*',
#       {
#             'timestamp': lambda v: to_timestamp(datetime.strptime(m.groups('timestamp'), '%Y-%m-%dT%H-%M-%S-%f'))
#
#           }
# ))

class PathAttribute(object):
    def __init__(self, regtxt, example, transforms={}):
        # compile regex
        # determine order
        self.reg = re.compile(regtxt)

        self.groups = sorted(self.reg.groupindex.items(), key=lambda o: o[1])
        print self.groups

    def names(self):
        return [group[0] for group in self.groups]

    def evaluate(self, path):
        m = self.reg.match(path)

        if not m:
            print 'No match - %s' % full
            return []

        return [m.group(group[0]) for group in self.groups]



class Image(object):
    def __init__(self):
        self.microseconds = None

    def near(self, other, diff):
        delta = float(self.timestamp - other.timestamp)

        val = delta * 1e6

        return abs(val) < diff


class Index(object):
    def __init__(self, path=None, left=None, predicate=None):
        self.index_path = path
        self.left = left
        self.predicate = predicate

    def images(self):
        if self.predicate:
            generator = (i for i in self.left.images() if self.predicate(i))

            while True:
                yield next(generator)

        path = (os.path.join(self.index_path, '.ook', 'flat'))

        while True:
            print('opening index' + path)

            fields = []

            with open(path) as csvfile:

                csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csv_reader:
                    if row[0] == 'h':
                        fields = [field for field in row]
                        continue

                    image = Image()

                    for i in range(1, len(row)):
                        setattr(image, fields[i], row[i])

                    yield image

                raise StopIteration

    def filter(self, predicate):
        return Index(left=self, predicate=predicate)

    def scan(self):
        print 'looking in ' + self.index_path

        ook_dir = os.path.join(self.index_path, '.ook')

        if not os.path.exists(ook_dir):
            os.makedirs(ook_dir)

        ii = 0

        start = time.time()
        interval_start = time.time()

        # 1/115/115_Stills/115_0045_c\image_D2015-11-03T16-17-36-558784Z_0.jpg
        # session/camera/Channel/image
        regtxt = '(?P<session>\w+)/(?P<camera>\w+)/\w+_(?P<type>\w+)/\w+_(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<channel>\d{1}).*'

        reg = re.compile(regtxt)

        first = True


        attribute_maps = {
            'timestamp': lambda v: to_timestamp(datetime.strptime(v, '%Y-%m-%dT%H-%M-%S-%f'))
            }

        last_values = None

        with open('%s/flat' % ook_dir, 'w') as out:
            for root, dirs, filenames in os.walk(self.index_path):
                for name in fnmatch.filter(filenames, '*.jpg'):
                    p = os.path.relpath(root, self.index_path)

                    full = os.path.join(p, name)
                    full = '/'.join(full.split('\\'))

                    m = reg.match(full)

                    if not m:
                        print 'No match - %s' % full
                        continue

                    attributes = {key: value for (key, value) in m.groupdict().iteritems()}
                    values = [(attribute_maps[key])(value) if key in attribute_maps else value for (key, value) in
                              attributes.iteritems()]

                    if first:
                        first = False

                        out.write("h,name,path,")
                        out.write("".join(['%s,' % val for val in attributes]))
                        out.write('\n')

                        print attributes

                    ##(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.join(root, name))

                    ##t = datetime.strptime(m.group('timestamp'), '%Y-%m-%dT%H-%M-%S-%f')

                    #out.write("i,%s,%s,%d," % (name, p, size))
                    out.write("i,%s,%s," % (name, p))
                    #out.write("".join(['%s,' % val for val in m.groups()]))

                    values_copy = list(values)

                    if False and last_values:
                        for i in range(len(values)):
                            if values[i] == last_values[i]:
                                values[i] = '.'

                    last_values = values_copy

                    out.write("".join(['%s,' % val for val in values]))
                    out.write('\n')

                    ii += 1
                    if ii % 5000 == 0:
                        duration = time.time() - interval_start
                        interval_start = time.time()
                        print "Reading %d, %d images/s" % (ii, 5000 / duration)

        duration = time.time() - start

        print '%d images indexed in %d seconds, %d images/s' % (ii, duration, ii / duration)
