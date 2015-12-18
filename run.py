__author__ = 'Kevin Godden'

import argparse
import os
from ook import ook


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="The root path to the images directory tree")
    parser.add_argument("-w", "--where", help="The where value")
    args = parser.parse_args()

    path = args.path

    print 'looking in ' + path

    code = compile(args.where, '<string>', 'eval')

    idx = ook.Index(path)

    for image in idx:
        if eval(code):
            print('%s %s' % (image.name, image.timestamp))


if __name__ == '__main__':
    run()


