#!/bin/zsh
set -e
BASE="http://v2d7c.sheepserver.net/cgi"
GEN="http://v2d7c.sheepserver.net/gen/244"
NB="electricsheep.244"

#BASE="http://sheep.arces.net/generation-243/"
#GEN="http://sheep.arces.net/generation-243"
#NB="electricsheep.243"

if [ ! -d "$1" ]; then
    echo USAGE: "$0" dstdir
    exit
fi

cd $1

for PAGE in `seq 0 5`; do
    wget "$BASE/best.cgi?menu=best&p=$PAGE" -c -O - | \
        grep -o 'dead.cgi[?]id=[1234567890]*' | \
        grep -o '[1234567890]*' | \
        while read id; do
            NAME="$NB.$(printf '%05d' $id).flam3"
            if ! [ -f $NAME ]; then wget $GEN/$id/$NAME; fi
        done
done

