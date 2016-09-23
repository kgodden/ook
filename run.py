__author__ = 'Kevin Godden'

import argparse
import ook
import time

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path",
                        help="The root path to the images directory tree")
    parser.add_argument("-f", "--filter",
                        help="The filter to apply (lambda of image in quotes, e.g. lambda i: i.camera =='Port')")

    parser.add_argument("-s", "--sort",
                        help="Optional lambda for post-filter sort")

    args = parser.parse_args()

    path = args.path

    print 'looking in ' + path

    file_filter = args.filter if args.filter else 'lambda i: True'

    code = compile(file_filter, '<string>', 'eval')

    idx = ook.Index(path)

    #for image in idx.filter(eval(code)).images():
    #    print('%s %s' % (image.name, image.file_size))

    #targets = sorted(image for image in idx.filter(eval(code)).images(), key = lambda i: i.file_size))

    t0 = time.time()

    if args.sort:
        sort_expr = compile(args.sort, '<string>', 'eval')
        targets = sorted((i for i in idx.filter(eval(code)).images()), key=eval(sort_expr))
    else:
        targets = idx.filter(eval(code)).images()

    i = 0
    for image in targets:
        print('%s %s' % (image.path+'/'+image.name, image.file_size))
        i += 1

    t1 = time.time()
    delta = t1 - t0

    print '{} items found in {}s'.format(i, delta)


if __name__ == '__main__':
    run()


