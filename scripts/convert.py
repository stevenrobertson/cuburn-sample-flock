import os
import sys

from cuburn.genome.convert import nodes_from_xml_path
from cuburn.genome.util import json_encode

def convert(path):
    id = os.path.basename(path).rsplit('.', 1)[0]
    print id
    with open('nodes/%s.json' % id, 'w') as fp:
        fp.write(json_encode(list(nodes_from_xml_path(path))[0]))
    with open('edges/%s.json' % id, 'w') as fp:
        out = dict(link=dict(src='nodes/%s@-0.25'%id, dst='nodes/%s@0.25'%id),
                   blend=dict(xform_sort='natural', duration=0.5), type='edge')
        fp.write(json_encode(out))

def main(args):
    map(convert, args[1:])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'USAGE: %s <path to flam3 xml> [<path to another xml> ...]'
        print 'Each flame will be dumped unceremoniously in nodes/, and a'
        print 'half-loop edge (from -0.25 to 0.25) will be placed in edges/.'
    else:
        main(sys.argv)
