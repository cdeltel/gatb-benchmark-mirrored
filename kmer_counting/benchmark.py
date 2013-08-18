#!/usr/bin/env python

"""
Usage: benchmark <reads_file> <temp_dir>
"""
import sys, os, subprocess, fileinput
from datetime import datetime 
import yaml
from codespeed_client import save_to_speedcenter

if len(sys.argv) < 1:
    sys.exit(
""""arguments: [benchmark].yaml [dataset].yaml [environment].yaml [...]
E.g kmer_counting.yaml datasets/test.yaml environments/cyberstar231-workdir.yaml
Options:
    --only <executable>    Only run benchmarks for <executable>
""")

only = None if "--only" not in sys.argv else sys.argv[sys.argv.index("--only")+1].strip()

yaml_files = filter(lambda x: "yaml" in x, sys.argv)
config = '\n'.join([l for l in fileinput.input(yaml_files)])
b = yaml.load(config)

b["script_dir"] = os.path.dirname(os.path.realpath(__file__))
b["reads"] = ("%(" + b["reads"] + ")s") % b

def run(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    rc = process.wait()
    return rc, stdout, stderr

environment = b["environment"]
benchmark_prefix = b["benchmark"]

def analyze_log(stdout, stderr):
    memory = 0
    time = 0
    for line in stdout.split('\n'):
        if line.startswith("maximal memory used"):
            memory = "%0.2f" % (float(line.split()[-1])/1024.0/1024.0)
            print memory,line
    for line in stderr.split('\n'):
        if line.startswith("real"):
            t = datetime.strptime(line.split()[-1],"%Mm%S.%fs")
            time = "%0.2f" % (t.minute + t.second/60.0)
    return time, memory

for prog_item in b["program"]:
        
    description = prog_item["description"] 
    cmd = (prog_item["command line"] % b ) % b # because %(reads)s redirect to %(ecoli_reads)s
    executable = prog_item["executable"]
    project = prog_item["project"]

    if only and executable != only:
        continue

    print "Runnning",description
    dsk = "DSK" in project
    svn = False
    git = False
    if "DSK SVN" in description:
        svn = True
        svn_folder = "~/dsk" if "svn_dir" not in b else b["svn_dir"]

    if "DSK GATB" in description:
        git = True
        git_folder = "~/gatb-tools/gatb-tools/"

    if svn:
        revision = run("svn info %s | sed -ne 's/^Revision: //p'" % svn_folder)[1].strip()

    if git:
        date = run("cd ~/gatb-tools/ &&  git log -n 1 --pretty='format:%ci'")[1].strip().split()[0]
        revision = run("cd ~/gatb-tools/ &&  git log -n 1 --pretty='format:%h'")[1].strip()
        revision += " " + date

    if "KMC" in description:
        revision = "0.3"

    rc, stdout, stderr = run(cmd)
    if rc > 1 or ('error' in stdout.lower()) or ('error' in stderr.lower()): # old versions of DSK returned 1.. i know..
        sys.exit("Error running command: %s \nstdout: %s\nstderr: %s" % (cmd,stdout,stderr))
    print "stdout:"
    print stdout
    print "stderr:"
    print stderr
    
    time, memory = analyze_log(stdout,stderr)

    print "Sending benchmark data"
    url = "http://codespeed.genouest.org/result/add/"
    branch = "default"

    benchmark = benchmark_prefix + " (time)"
    result_value = time
    save_to_speedcenter(url, project, revision, executable, benchmark, result_value, branch=branch, environment=environment)

    benchmark = benchmark_prefix + " (memory)"
    result_value = memory
    save_to_speedcenter(url, project, revision, executable, benchmark, result_value, branch=branch, environment=environment)
