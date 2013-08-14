import sys, os, subprocess
def run(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    rc = process.wait()
    return rc, stdout, stderr


with open("list_revisions") as f:
    for line in f:
        if len(line.split()) == 0:
            continue
        revision = line.split()[0]
        if not revision.startswith("r"):
            continue
        if not revision[1:].isdigit():
            continue
        rc, o, e = run("rm -Rf ~/work/dsk")
        print "Checking out DSK revision",revision
        rc, o, e = run("cd ~/work && svn checkout -r %s svn+ssh://chikhi@scm.gforge.inria.fr/svnroot/projetssymbiose/dsk" % revision)
        if rc:
            exit("Error checking out DSK revision %s" % revision)
        print "Checking out Minia revision",revision
        rc, o, e = run("rm -Rf ~/work/dsk/minia && cd ~/work/dsk && svn checkout -r %s svn+ssh://chikhi@scm.gforge.inria.fr/svnroot/projetssymbiose/minia/trunk && mv trunk minia" % revision)
        if rc:
            exit("Error checking out Minia revision %s" % revision)
        print "Running benchmark revision",revision
        rc, o, e = run("python ../benchmark.py dsk_older_versions.yaml ../datasets/test.yaml")
        if rc:
            exit("Error running benchmark revision %s; \nstderr: %s\nstdout: %s" % (revision,e,o))
        print "bench:", o,e
