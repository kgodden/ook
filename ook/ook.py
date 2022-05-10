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
    """
        Extracts attributes from an image file's file-path using a supplied
        regular expression.  The named attributes are specified as named capture
        groups within the expression, e.g.:

        '(\./)?(?P<experiment>\w+)/(?P<camera>\w+)/(?P<channel>\w+)/(?P<dir>\d+)/image_D(?P<timestamp>.*)Z_(?P<frame>\d{1}).*'

        to match a filename like this:

        'sync_test/camera1/structured_light/0000/image_D2015-10-27T13-26-52-302857Z_9.jpg'

        will produce the following named attributes:

        experiment  : sync_test
        camera      : camera1
        channel     : structured_light
        dir         : 0000
        timestamp   : 2015-10-27T13-26-52-302857
        frame       : 9

        A dict of named transform lambdas can be provided along with the regex,
        if a lambda exists in the dict for a named attribute, then the it will
        be applied to the attribute before it is returned.

        For example to transform the timestamp string into a proper time by calling
        strptime():

               attribute = ook.PathAttribute(regex2,
                                      {'timestamp': lambda v: ook.to_timestamp(
                                          datetime.strptime(v, '%Y-%m-%dT%H-%M-%S-%f'))}
                                      )
    """
    def __init__(self, regtxt, transforms=None):
        """
            Initialises a FileAttribute

        :param regtxt: The regex string to match against the file paths.
        :param transforms: A dictionary of lambdas to a applied to the raw extracted attributes.
        :return:
        """

        # compile regex
        self.reg = re.compile(regtxt)
        self.transforms = transforms

        # determine attribute order based on the group order
        # withing the regex, this is so that we can report the
        # attributes in the same order as specified in the regex.
        self.groups = sorted(self.reg.groupindex.items(), key=lambda o: o[1])

    def names(self):
        """
            Gets an ordered list of the attribute names, these correspond
            to the named capture groups in the supplied regex.

        :return: A list of attribute names
        """
        return [group[0] for group in self.groups]

    def evaluate(self, rel_path, base_path):
        """
            Evaluates the attribute based on the passed image file path.

        :param rel_path: The relative path to the image in question.
        :param base_path: The absolute path to the base images directory.
        :return: A list of the extracted attributes.
        """

        # Apply the regex to the path
        m = self.reg.match(rel_path)

        if not m:
            raise ValueError #ValueError('No match - %s' % rel_path)

        # We have a match and some captures, now let's make an ordered
        # list of features, if a transform has been specified for a feature
        # we apply it to the raw feature otherwise we just return the raw
        # text.
        values = [self.transforms[group[0]](m.group(group[0]))
                  if self.transforms and group[0] in self.transforms else
                  m.group(group[0])
                  for group in self.groups]

        return values


class FileSizeAttribute(object):
    """
        Extracts an image file's size (in bytes) as an attribute.
    """

    def __init__(self):
        pass

    @staticmethod
    def names():
        """
            Gets a list of attribute names to be extracted.
        :return:  A single named attribute file_size
        """
        return ['file_size']

    @staticmethod
    def evaluate(rel_path, base_path):
        """
            Calculates the size of the image file indicated
            by the path and returns it as an attribute.
        :param rel_path: The relative path to the image in question.
        :param base_path: The absolute path to the base images directory.
        :return: A list containing a single element - the file size as a string.
        """
        return [str(os.stat(os.path.join(base_path, rel_path)).st_size)]


class ImageAttribute(object):
    """
        Uses opencv to extract some attributes from an image, currently
        min, mane and max image brightness.
    """
    def __init__(self):
        pass

    @staticmethod
    def names():
        """

        :return: An ordered list of attribute names extracted by
            this image feature.
        """
        return ['min', 'mean', 'max']

    @staticmethod
    def evaluate(rel_path, base_path):
        """
            Evaluates this feature using opencv to extract some image
            statistics.

        :param rel_path: The relative path to the image in question.
        :param base_path: The absolute path to the base images directory.
        :return: The extracted image features.
        """
        import cv2

        # Read the image
        img = cv2.imread(os.path.join(base_path, rel_path), 0)

        # And collect the stats
        vals = [img.min(), math.trunc(img.mean()), img.max()]

        # return as a list of strings
        return [str(v) for v in vals]

def dump(obj):
   for attr in dir(obj):
       if hasattr( obj, attr ):
           print( "obj.%s = %s" % (attr, getattr(obj, attr)))

class Image(object):
    """ Represents an indexed image file.  The index returns objects
        of this type.
    """

    def __init__(self):
        self.microseconds = None

    def near(self, other, diff):
        """
            Determines if this image is 'near' another image in time.

        :param other: The other image
        :param diff: microsecond threshold value used to determine if this
                        image us near the other image in time.
        :return: True / False --> Near / Not Near
        """

        # If this image does not have a timestamp attribute
        # then we can't say whether it's near anything!
        if not hasattr(self, 'timestamp'):
            return False

        # Compute the microsecond delta between the two images'
        # timestamps.
        delta = float(self.timestamp) - float(other.timestamp)

        return abs(delta) < diff


class Index(object):
    """ The main image file index functionality.

        If a path is supplied to its constructor then the index will
        attempt to load an index file called .ook/flat, once opened
        the caller can step through the images index.images() to retrieve
        a generator, for example:

                idx = ook.Index(images_path)    # Load the index
                images = idx.images()           # Get a generator
                image = next(images)            # Get the first image


        If a left index object and a predicate are supplied then this index
        will chain onto the felt index and filter the images based on the
        predicate.

    """
    def __init__(self, path=None, left=None, predicate=None):
        self.index_path = path
        self.left = left
        self.predicate = predicate

    def images(self):
        """
            Implements the images generator.

        :return:
        """

        # If a predicate has been specified, then we make a generator
        # using the 'left' index and the predicate and implement the generator.
        if self.predicate:
            generator = (i for i in self.left.images() if self.predicate(i))

            while True:
                try:
                    yield next(generator)
                except StopIteration:
                    return

        # No predicate supplied, lets load an index from file instead
        # and implement the generator on that line-by-line
        path = (os.path.join(self.index_path, '.ook', 'flat'))

        print('opening index' + path)

        fields = []

        with open(path) as csvfile:

            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csv_reader:
                # Load up the attribute names from the header line
                if row[0] == 'h':
                    fields = [field for field in row]
                    continue

                image = Image()

                # Take the attributes from the CSV line and
                # add them to the image
                for i in range(1, len(row)):
                    setattr(image, fields[i], row[i])

                yield image

            # No more lines!
            #raise StopIteration

    def filter(self, predicate):
        """
            Returns a new index based on this index but filtered
            using the supplied predicate. E.g.:

                    idx = ook.Index(images_path)

                    # filter for all images with _9 in their name
                    idx1 = idx.filter(lambda p: '_9' in p.name)
                    first = next(idx1)

        :param predicate: A lambda to filter the images
        :return: A new index which will apply the predicate to this index.
        """

        return Index(left=self, predicate=predicate)

    def image(self, name):
        """
            Gets the first image in the index that has the passed name.

        :param name: The name of the image to find
        :return: The found image, if any.
        """
        return next(self.filter(lambda p: p.name == name).images())

    def scan(self, attributes):
        """
            Scans through a directory tree of images and create an index file from the
            images found including their attributes as specified by the attributes
            argument.

        :param attributes: A list of attributes to extract from the indexed images.
        :return: Nothing at the moment
        """

        print('looking in ' + self.index_path)

        ook_dir = os.path.join(self.index_path, '.ook')

        # make the .ook dir if it doesn't exist
        if not os.path.exists(ook_dir):
            os.makedirs(ook_dir)

        ii = 0

        start = time.time()
        interval_start = time.time()

        first = True

        last_values = None

        # we write the index datra to ./.ook/flat
        with open('%s/flat' % ook_dir, 'w') as out:

            # recursively search for image files *.jpg
            for root, dirs, filenames in os.walk(self.index_path):
                for name in fnmatch.filter(filenames, '*.jpg'):
                    rel_path = os.path.relpath(root, self.index_path)
                    #print root
                    #print self.index_path
                    #print name

                    rel_path = os.path.join(rel_path, name)

                    if '.paused' in rel_path:
                        continue

                    # figure out the relative path for this image
                    rel_path = '/'.join(rel_path.split('\\'))

                    values = []

                    # extract the attributes
                    for a in attributes:
                        try:
                            values.extend(a.evaluate(rel_path, self.index_path))
                        except ValueError:
                            print("No match - " + rel_path)

                    # if this is the first row, then we write out the attributes
                    # header first, this names all of the attributes in order
                    if first:
                        first = False

                        names = []

                        for a in attributes:
                            names.extend(a.names())

                        out.write("h,name,path,")
                        out.write("".join(['%s,' % val for val in names]))
                        out.write('\n')

                        print(names)

                    # start to write the image row which starts with:
                    # i,<image-name>,<rel-path>
                    out.write('i,%s,%s,' % (name, os.path.dirname(rel_path)))

                    values_copy = list(values)

                    # Experimental code, gnore this
                    if False and last_values:
                        for i in range(len(values)):
                            if values[i] == last_values[i]:
                                values[i] = '.'

                    last_values = values_copy

                    # Write out the attributes
                    out.write("".join(['%s,' % val for val in values]))
                    out.write('\n')

                    ii += 1
                    every_n = 50

                    # every N lines, write out a progress message
                    if ii % every_n == 0:
                        duration = time.time() - interval_start
                        interval_start = time.time()
                        try:
                            print("Reading %d, %d images/s" % (ii, every_n / duration))
                        except:
                            pass

        duration = time.time() - start

        print('%d images indexed in %d seconds, %d images/s' % (ii, duration, ii / duration))
