__author__ = 'Kevin Godden'

import csv
import os
import time
import re
import fnmatch
import math
from datetime import datetime
from decimal import Decimal

#del show(i):
#    name = i.path + i.
def to_timestamp(dt):

    # return str(calendar.timegm(dt.timetuple()))

    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return str(Decimal(delta.days*86400+delta.seconds)+Decimal(delta.microseconds/1000000.0).quantize(Decimal('.000001')))


class PathAttribute(object):
    def __init__(self, regtxt, transforms=None):
        # compile regex
        self.reg = re.compile(regtxt)
        self.transforms = transforms

        # determine attribute order
        self.groups = sorted(self.reg.groupindex.items(), key=lambda o: o[1])

    def names(self):
        return [group[0] for group in self.groups]

    def evaluate(self, rel_path, base_path):
        m = self.reg.match(rel_path)

        if not m:
            raise ValueError('No match - %s' % rel_path)

        values = [self.transforms[group[0]](m.group(group[0]))
                  if self.transforms and group[0] in self.transforms else
                  m.group(group[0])
                  for group in self.groups]

        return values


class FileSizeAttribute(object):
    def __init__(self):
        pass

    @staticmethod
    def names():
        return ['file_size']

    @staticmethod
    def evaluate(rel_path, base_path):
        return [str(os.stat(os.path.join(base_path, rel_path)).st_size)]


class ImageAttribute(object):
    def __init__(self):
        pass

    @staticmethod
    def names():
        return ['min', 'mean', 'max']

    @staticmethod
    def evaluate(rel_path, base_path):
        import cv2
        img = cv2.imread(os.path.join(base_path, rel_path), 0)
        vals = [img.min(), math.trunc(img.mean()), img.max()]
        return [str(v) for v in vals]


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

    def scan(self, attributes):
        print 'looking in ' + self.index_path

        ook_dir = os.path.join(self.index_path, '.ook')

        if not os.path.exists(ook_dir):
            os.makedirs(ook_dir)

        ii = 0

        start = time.time()
        interval_start = time.time()

        first = True

        last_values = None

        with open('%s/flat' % ook_dir, 'w') as out:
            for root, dirs, filenames in os.walk(self.index_path):
                for name in fnmatch.filter(filenames, '*.jpg'):
                    rel_path = os.path.relpath(root, self.index_path)
                    #print root
                    #print self.index_path
                    #print name

                    rel_path = os.path.join(rel_path, name)

                    if '.paused' in rel_path:
                        continue

                    rel_path = '/'.join(rel_path.split('\\'))

                    values = []

                    for a in attributes:
                        try:
                            values.extend(a.evaluate(rel_path, self.index_path))
                        except ValueError:
                            print "No match - " + rel_path

                    if first:
                        first = False

                        names = []

                        for a in attributes:
                            names.extend(a.names())

                        out.write("h,name,path,")
                        out.write("".join(['%s,' % val for val in names]))
                        out.write('\n')

                        print names

                    # #(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.join(root, name))

                    # #t = datetime.strptime(m.group('timestamp'), '%Y-%m-%dT%H-%M-%S-%f')

                    # out.write("i,%s,%s,%d," % (name, p, size))
                    out.write('i,%s,%s,' % (name, os.path.dirname(rel_path)))
                    # out.write("".join(['%s,' % val for val in m.groups()]))

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
