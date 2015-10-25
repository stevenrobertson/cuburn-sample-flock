import os
import sys
import random

from cuburn.genome.util import json_encode


# record of the experiments I tried
class Blender(object):
    def __init__(self):
        self.nodes = []
        self.edgeset = {}
        self.rev_edgeset = {}

    def read_existing(self):
        self.nodes = [n[:-5] for n in os.listdir('nodes')]
        for n in os.listdir('edges'):
            if '=' in n:
                self.add_edge(*(n[:-5].split('=')))

    def add_edge(self, s, d):
        self.edgeset.setdefault(s, set()).add(d)
        self.rev_edgeset.setdefault(d, set()).add(s)

    def select(self, n):
        # The "weighted walking" algorithm that proved to be the best
        # according to the experiments below
        sorted_nodes = list(self.nodes)
        s = None
        for i in range(n):
            random.shuffle(sorted_nodes)
            sorted_nodes.sort(key=lambda n: len(self.rev_edgeset.get(n, [])))
            d = sorted_nodes[0]
            if not s or d in self.edgeset.get(s, []) or s == d:
                for s in sorted_nodes[1:]:
                    if d not in self.edgeset.get(s, []):
                        break
            self.add_edge(s, d)
            yield s, d
            s = d

def main(num_edges):
    blender = Blender()
    blender.read_existing()
    if not blender.nodes:
        print 'No nodes found. Run convert.py first?'
        return

    for s, d in blender.select(num_edges):
        with open('edges/%s=%s.json' % (s, d), 'w') as fp:
            link = dict(src='nodes/%s@0.25' % s, dst='nodes/%s@-0.25' % d)
            blend = dict(duration=1.4 + 1.2 * random.random())
            fp.write(json_encode(dict(link=link, blend=blend, type='edge')))

# below this is the record of some experiments I ran to choose the best blend

class WalkingBlender(Blender):
    def select(self, n):
        s = random.choice(self.nodes)
        for i in range(n):
            d = random.choice(self.nodes)
            while d in self.edgeset.get(s, []):
                d = random.choice(self.nodes)
            self.add_edge(s, d)
            yield s, d
            s = d

class WeightedBlender(Blender):
    def select(self, n):
        sorted_nodes = list(self.nodes)
        for i in range(n):
            random.shuffle(sorted_nodes)
            sorted_nodes.sort(key=lambda n: len(self.rev_edgeset.get(n, [])))
            d = sorted_nodes[0]
            for s in sorted_nodes[1:]:
                if d not in self.edgeset.get(s, []):
                    self.add_edge(s, d)
                    yield s, d
                    break

class FakeFullyConnectedBlender(Blender):
    def select(self, n):
        for i in self.nodes:
            for j in self.nodes:
                self.add_edge(i, j)
                yield i, j

def test_fairness():
    import numpy as np

    for b in [WalkingBlender(), WeightedBlender(), Blender(),
              FakeFullyConnectedBlender()]:

        print '\n'
        print type(b)

        for round in range(5):
            b.nodes = map(str, range(30))
            list(b.select(70))

            node_playcounts = dict([(n, 0) for n in b.nodes])
            edge_playcounts = dict([((s, d), 0)
                                    for s in b.edgeset
                                    for d in b.edgeset[s]])

            deadends = 0

            for i in range(100):
                src = None
                for i in range(1000):
                    if src not in b.nodes:
                        src = random.choice(b.nodes)
                        deadends += 1
                    node_playcounts[src] += 1
                    if src in b.edgeset:
                        dst = random.choice(list(b.edgeset[src]))
                        edge_playcounts[(src, dst)] += 1
                        src = dst
                    else:
                        src = None

            pctiles = [0, 20, 50, 80, 100]
            print '\nround %d:' % round
            print 'node plays:', '\t'.join([
                '%6g' % np.percentile(node_playcounts.values(), p)
                for p in pctiles])
            print 'edge plays:', '\t'.join([
                '%6g' % np.percentile(edge_playcounts.values(), p)
                for p in pctiles])
            print 'node links:', '\t'.join([
                '%6g' % np.percentile(map(len, b.edgeset.values()), p)
                for p in pctiles])
            print 'rev links: ', '\t'.join([
                '%6g' % np.percentile(map(len, b.rev_edgeset.values()), p)
                for p in pctiles])
            print 'dead-ends: ', deadends
            #print
            #print ', '.join(['%s: %d' % n for n in sorted(node_playcounts.items())])
            #print ', '.join(['%s->%s: %d' % (s,d,n) for ((s,d),n) in sorted(edge_playcounts.items(), key=lambda (k,n): n)])
            #print sorted(b.edgeset.items())
            #print sorted(b.rev_edgeset.items())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_fairness()
        sys.exit(0)

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
