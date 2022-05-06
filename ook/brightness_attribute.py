__author__ = 'Kevin Godden'

import os
import numpy as np
from PIL import Image
import scipy.stats


class BrightnessAttribute(object):
    def __init__(self):
        pass

    @staticmethod
    def names():
        return ['brightness', 'filtered_brightness', 'percentage_above']

    @staticmethod
    def evaluate(rel_path, base_path):
        img = Image.open(os.path.join(base_path, rel_path))
        img = img.convert('L')
        half = 0.5
        imp = img.resize([int(half *   for s in img.size])

        im = np.array(img)
        flat_image = im.flatten()
        intensity = scipy.stats.gmean(flat_image, axis=0)

        filter = flat_image > 40

        filter_image = flat_image[filter]
        filter_intensity = scipy.stats.gmean(filter_image, axis=0)

        #max_intensity = flat_image.max()

        #print "%s, %s" % (rel_path, str(im_kurt))

        count_above = len(flat_image[flat_image > 250])

        percentage_above = count_above * 100 / len(flat_image)

        return [str(round(intensity,2)), str(round(filter_intensity,2)), str(round(percentage_above,2))]
