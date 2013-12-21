import os
import sys
import random

from cuburn.genome.util import json_encode


def main(num_edges):
    nodes = [n[:-5] for n in os.listdir('nodes')]
    if not nodes:
        print 'No nodes found. Run convert.py first?'
        return
    s = random.choice(nodes)
    for i in range(num_edges):
        d = random.choice(nodes)
        with open('edges/%s=%s.json' % (s, d), 'w') as fp:
            link = dict(src='nodes/%s@0.25'%s, dst='nodes/%s@-0.25'%d)
            blend = dict(duration=1.4 + 1.2 * random.random())
            fp.write(json_encode(dict(link=link, blend=blend, type='edge')))

        s = d

if __name__ == "__main__":
    try:
        num_edges = int(sys.argv[1])
    except:
        print 'USAGE: %s [number of edges to create]' % sys.argv[0]
        print 'Produces edges between two different nodes, from 0.25 on the '
        print 'src to -0.25 on the dst. (You can get fancier if you want by '
        print 'just editing the script a bit.) Make a lot of edges for good '
        print 'coverage, this script doesn\'t do a random walk.'
    else:
        main(num_edges)
