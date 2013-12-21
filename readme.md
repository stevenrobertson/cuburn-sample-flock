# Cuburn sample flock

How to make your own collection of gorgeous fractal flames.

## Step 1: get cuburn running

Check out cuburn, chase down all the dependencies including the ones I forgot
to list, and render your first still image. If you don't have a flame handy to
test with, proceed to step 3 to get one.

    cd ~/code
    git clone https://github.com/stevenrobertson/cuburn.git

## Step 2: make a flock directory

A great way to do it is to clone this repo and then delete the samples:

    git clone https://github.com/stevenrobertson/cuburn-sample-flock.git ~/myflock
    cd ~/myflock
    rm nodes/* edges/* sheep/*

The samples you just deleted are taken from the Electric Sheep project, licensed
under CC Attribution. Visit http://electricsheep.org for details. You can use
these to make sure that rendering is working OK:

    python2 ~/code/cuburn/main.py -P 1080p -o out/ --still sheep/electricsheep.244.80674.flam3
    eog out/

## Step 3: produce some nodes

A node is effectively an animation control point. In a flam3-style flock, nodes
are the equivalent of uploaded .flam3 files; they contain the primary
definitions of the parameter values in the flock.

(There's no limitation on this in the software; edges are free to add
variations or even entire transforms that blend out of and then back into unity
over the course of a transform. But that must be done by hand.)

One easy way to get some starter nodes is by ripping off Electric Sheep. Note
that this command will pull all nodes, including some that are CC-BY-NC, so
don't go sell your beautiful digital artwork made from this script without
talking to Scott Draves first.

    ./scripts/download-electric-sheep-flam3-files.sh sheep/

Now that you have '.flam3' files, you can produce the corresponding nodes by
importing them into cuburn's omnivorous parser and asking for a node back.
A script does it for you:

    PYTHONPATH=~/code/cuburn python2 ./scripts/convert.py sheep/*.flam3
    ls nodes

Note that it's also created "half-loops" in the edges/ directory for each node
it imports. These are edges that start at -0.25 turns (that is, 90°) and extend
to 0.25 turns. They don't join up with themselves since they're only half a
loop. Hack the script if you want something different.

## Step 4: produce some edges

An edge is a smooth blend between two nodes. The simplest edges are simple
indeed, consisting of only a src and dest node (and an angle for half-loops).
The properties are actually read from the node files themselves, rather than
being duplicated into the edge definition, which helps keep everything simple.

A script spits out a bunch of these simple nodes. You might want to do node
selection by hand, or come up with an algorithm that walks the node graph
elegantly, and in those cases the script is easy to hack. But simply spitting
out some random links works OK too:

    PYTHONPATH=~/code/cuburn python2 ./scripts/blend.py 50
    ls edges

## Step 5: set up your renderfarm

I hacked (hacked!!!!) together some tools to distribute work over multiple
machines and cards. After setting them up, they're the most convenient way
to render a flock, even if you only have a single machine; there's very
little nannying involved once it's running.

First, edit the fixed IP address of the distribution server in the file
(yeah, it's that hacky):

    vi ~/code/cuburn/dist/addrs.py

If your machines all use the same card, edit the server to set up your
card architecture (the client and server don't actually need a card
installed, which is useful if you want to run them on, say, a NAS box,
but it *does* still need CUDA installed to precompile the kernel):

    diff --git a/dist/server.py b/dist/server.py
    index a3a9eee..6159ba9 100644
    --- a/dist/server.py
    +++ b/dist/server.py
    @@ -55,7 +55,7 @@ def setup_worker_listener(addrs, tq, rq):
                 print ' >', ' '.join(addr)
                 if task.hash not in compcache:
                     try:
    -                    rsp = Renderer.compile(task.anim, arch='sm_21')
    +                    rsp = Renderer.compile(task.anim, arch='sm_35')
                     except:
                         # Store exceptions, so that we don't try to endlessly
                         # recompile bad genomes


Alternatively, if your cards are heterogeneous, hack the workers to ignore
precompilation altogether:

    diff --git a/dist/worker.py b/dist/worker.py
    index 3847587..5caf058 100644
    --- a/dist/worker.py
    +++ b/dist/worker.py
    @@ -43,7 +43,8 @@ def main(worker_addr):
                 addr, task, cubin, packer = sock.recv_pyobj()
                 gprof = profile.wrap(task.profile, task.anim)
                 if hash != task.hash:
    -                rdr = PrecompiledRenderer(task.anim, gprof, packer, cubin)
    +                rdr = render.Renderer(task.anim, gprof)
                 for t in task.times:
                     evt, buf = rmgr.queue_frame(rdr, task.anim, gprof, t)
                     while not evt.query():

Once sufficient hacking has happened, start three processes. The first is the
distribution server:

    python ~/code/cuburn/dist/server.py

The second is a worker, running on a system with a card. This one takes the
card number as an argument:

    python ~/code/cuburn/dist/worker.py 0

And finally, the client, which makes render requests and saves the results.
Let's start by doing a random walk of the flock (with a seed of '4') to
determine render order, and then kicking off the render:

    python ~/code/cuburn/scripts/walk.py 4 > walk-4-order.txt
    python ~/code/cuburn/dist/client.py -p profiles/lores_preview.json `cat walk-4-order.txt`

Boom, rendering.

## Step 5: troubleshoot your setup

There's no way that worked on the first try. Do some clever debugging.

## Step 6: preview the results with sheep_player

I don't know why this is still on bitbucket but it is:

    git clone https://bitbucket.org/srobertson/sheep_player.git ~/code/sheep_player/
    python2 ~/code/sheep_player/sheep_player.py out/lores_preview

Like all of these tools, customize them by hacking them.

## Step 7: perform reference-quality rendering

Once you're satisfied, it's time to kick off the big render at high quality:

    python2 ~/code/cuburn/dist/client.py -p profiles/4k.json `cat walk-4-order.txt`

Since this will use 444 colorspace by default (and can even use 10-bit color,
if you rebuild your x264 and change the output config in the profile), you
will probably also want something less reference-quality for playback:

    python2 scripts/recode.sh out/4k out/4k_yuv420

Then start some good music and enjoy the show.

    python2 ~/code/sheep_player/sheep_player.py out/4k_420

## Step 8: get funky

Some advanced features.

### See what an animation definition looks like

flam3 XML files can be imported as nodes, and nodes can be linked to form
edges, and finally the nodes and edges are blended into a collection called
an animation. It's the animation that's actually used to drive compilation
of a custom kernel. There's not much you can or should do with the actual
animation data; *everything* can be controlled by inserting, removing,
overriding, and otherwise messing about in nodes and edges. But it's still
useful to see how the animation gets put together, especially in terms of
how transforms are blended via spline interpolation:

    python2 ~/code/cuburn/main.py --print edges/electricsheep.244.00216=electricsheep.244.80674.json

### Control blend order

The selection of which transforms get blended into one another has a huge
impact on the aesthetics of an edge. The default algorithm for picking which
transforms to join is 'weightflip', which sorts the transform list for the src
node by weight, sorts the dst node inversely by weight, and then joins across,
padding as needed. This usually looks pretty good.

For self-loops, including half-loops, we don't actually want that behavior;
instead, we want the natural order on both sides, so that the flame stays
"stable" inside the loop. That's why a self-loop has blend.xform_sort set:

    # nodes/electricsheep.244.00216.json
    { "blend": {"duration": 0.5, "xform_sort": "natural"}
    , "link":
      { "dst": "nodes/electricsheep.244.00216@0.25"
      , "src": "nodes/electricsheep.244.00216@-0.25"
      }
    , "type": "edge"
    }

You can see the options, like every setting, in cuburn/genome/specs.py.

If you're dissatisfied with a sort decision, you can override it manually
using 'xform_map', which gets applied before 'xform_sort' and removes any
affected transforms from the candidate list:

    { "blend": {"xform_map": [["1", "1"], ["pad", "3"]]},
    ...
    }

### Insert knots into edges

You can add something new from the edge definition. Inserted knots have an
affinity to one node or another; they'll show up in the middle of whatever
blended xform pair the sort order decides to use.

Here we've added the julia variation to whichever blended transform contains
the transform named '0' from the source node; in practice this ends up being
transform '0_2' in the final animation. This only specifies a single node -
a value of 2 happening at t=0.5 within the animation - so the behavior at
the edges of the transforms is automatically handled to smoothly take the
value back down to 0 for a seamless transition with the nodes.

This example also shows off dot-notation for nested dictionaries, which is
simple and convenient, and the syntax for fully-specifying splines, which
is complicated and overwrought (see cuburn/genome/spectypes.py).

    # edges/electricsheep.244.00216=electricsheep.244.00216.json
    { "blend": {"duration": 2.22367}
    , "link":
      { "dst": "nodes/electricsheep.244.00216@-0.25"
      , "src": "nodes/electricsheep.244.00216@0.25"
      }
    , "type": "edge"
    , "xforms.src.0.variations.julia.weight": [0.5, 2]
    }

(I'll add a filename convention for alternate versions of edges too and update
sheep_player to respect it at some point.)

### Inherit the earth

Back when I originally thought this was going to be a community project, I
wanted an easy way for people to be able to extend each other's nodes by hand,
instead of relying on a faceless machine-god to do genomics. That dream is
gone, but the code remains, so you can do this:

    # nodes/electricsheep.244.00216-extended.json
    { "base": "nodes/electricsheep.244.00216"
    , "type": "node"
    , "xforms.0.variations.julia.weight": 0.02
    }

And then this:

    python2 ~/code/cuburn/main.py --print nodes/electricsheep-244.00216-extended.json

And you can see that the node has been inherited. You can replace, insert, and
remove individual knots using this mechanism, and both nodes and edges are
subject to inheritance, which makes it really easy to tune and experiment. The
whole thing was originally intended to make it easy to store the entire
revision history of a project in Git, which, oh, how convenient, this is a
Git repo.

Enjoy.

-- steven@strobe.cc
