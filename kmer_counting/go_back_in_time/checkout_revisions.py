import yaml

#dataset="../datasets/test.yaml"
#dataset="../datasets/chr14.yaml"
dataset="../datasets/ecoli.yaml"

#environment = "../environments/rayan-1.bx.psu.edu.yaml"

environment = "../environments/cyberstar231-workdir.yaml"

import sys, os, subprocess
def run(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    rc = process.wait()
    return rc, stdout, stderr


b = yaml.load(open(environment))
temp_dir = b["temp_dir"]

#override dsk svn dir
with open("addentum.yaml",'w') as f:
    f.write("dsk_svn_dir: %s/dsk" % (temp_dir))

with open("list_revisions") as f:
    for line in f:
        if len(line.split()) == 0:
            continue
        revision = line.split()[0]
        if not revision.startswith("r"):
            continue
        if not revision[1:].isdigit():
            continue
        rc, o, e = run("rm -Rf %s/dsk" % temp_dir)
        print "Checking out DSK revision",revision
        rc, o, e = run("cd %s && svn checkout -r %s \
                       svn+ssh://chikhi@scm.gforge.inria.fr/svnroot/projetssymbiose/dsk" \
                       % (temp_dir,revision))
        if rc:
            exit("Error checking out DSK revision %s" % revision)
        print "Checking out Minia revision",revision
        rc, o, e = run("rm -Rf %s/dsk/minia && cd %s/dsk && svn checkout -r %s\
                       svn+ssh://chikhi@scm.gforge.inria.fr/svnroot/projetssymbiose/minia/trunk\
                       && mv trunk minia" % (temp_dir, temp_dir, revision))
        if rc:
            exit("Error checking out Minia revision %s" % revision)
        print "Running benchmark revision",revision
        rc, o, e = run("python ../benchmark.py ../kmer_counting.yaml %s %s addentum.yaml --only dsk-svn" % (dataset,environment))
        if rc:
            exit("Error running benchmark revision %s; \nstderr: %s\nstdout: %s" % (revision,e,o))
        print "bench:", o,e
