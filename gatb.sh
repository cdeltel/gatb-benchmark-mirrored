#!/bin/bash

# requirement: reads are FASTA and interleaved, e.g.
# >left mate of read 1
# ACTGTAG..
# >right mate of read 1
# CTGCTGCAA
# >left mate of read 2
# ...
# (this is necessary for superscaffolder)

genome_size=10000 # can be obtained by examining histograms.dat from kmergenie
min_abundance=3 # should be computed by kmergenie (not trivial)
prefix=assembly

if [ $# -lt 1 ]
  then
    echo "Usage: $0 read_file"
    exit 0
fi


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# ------------------------------
# kmergenie

echo "running kmergenie"

best_k=$( $DIR/kmergenie/kmergenie $1 -e 1  | grep "^best" | awk '{print $3}')
# -e 1 is for tiny genomes, -e 10 is for bacterial, -e 1000 is for eukaryotic. some day this is will be auto-computed by kmergenie

echo "best k: $best_k"

if [ $best_k -lt 1 ]
then
    echo "kmergenie could not detect a best k; aborting"
    exit 1
fi

# ------------------------------
# minia

echo "compiling minia to support k=$best_k"

make k=$best_k -C $DIR/minia/

echo "running minia"

$DIR/minia/minia $1 $best_k $min_abundance $genome_size $prefix

# ------------------------------
# superscaffolder

# superscaffolder wants clean id in reads and contigs
python $DIR/superscaffolder/scripts/reformatfasta.py $1 "$1"_relabeled
python $DIR/superscaffolder/scripts/reformatfasta.py $prefix.contigs.fa $prefix.contigs.fa_relabeled
python $DIR/superscaffolder/superscaffolding.py $prefix.contigs.fa_relabeled "$1"_relabeled

echo "pipeline finished!!"
