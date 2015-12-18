__author__ = 'Kevin Godden'

import csv
import os

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

        path = (os.path.join(self.index_path, '.ook', '.flat'))

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
