#!/usr/bin/env python

import argparse
import collections
import os
import subprocess
import time

def launch(host, commandline, stdout=None, stderr=None, wait=False):
    """ Runs a command either locally or on a remote host via SSH """
    cwd = os.getcwd()
    if host == 'localhost':
        pass
    else:
        commandline = "ssh -f %s 'cd %s; %s'" % (host, cwd, commandline)

    print commandline
    process = subprocess.Popen(commandline, shell=True, stdout=stdout, stderr=stderr)
    if wait:
        process.wait()

def kill(host, process_name_match):
    """ Kills a process by name, either locally or on a remote host via SSH """
    if host == 'localhost':
        commandline = "pgrep -f \"%s\" | xargs kill -s SIGINT" % process_name_match
    else:
        commandline = "ssh %s 'pgrep -f \"%s\" | xargs kill -s SIGINT'" % (host, process_name_match)

    print commandline
    try:
        process = subprocess.call(commandline, shell=True)
    except Exception, e:
        print "Unable to kill '%s' on %s" % (process_name_match, host)


def parse_args():
    parser = argparse.ArgumentParser(prog="launch", description="DHT Simulation Launcher")

    parser.add_argument("--run-tests", action="store_true",
            help="run tests")

    parser.add_argument("--nameserver", type=str, required=True,
            help="address (host:port) of nameserver to launch")

    parser.add_argument("--no-launch-nameserver", dest="launch_nameserver",
            action="store_false",
            help="indicate that the nameserver is already running separately, " +
                "and this script should not attempt to launch or kill it")

    parser.add_argument("node", type=str, nargs='*',
            help="address (host:port) of nodes to launch")

    return parser.parse_args()


class HostPort(collections.namedtuple('HostPort', ['host','port'])):
    def __str__(self):
        return "%s:%d" % (self.host, self.port)

def parse_host_port(hp_str, default_port=8000):
    if ":" in hp_str:
        host, port = hp_str.split(":")
        port = int(port)
    else:
        host = hp_str
        port = default_port
    return HostPort(host,port)


if __name__ == "__main__":

    args = parse_args()

    nameserver = parse_host_port(args.nameserver)
    nodes = [parse_host_port(hp) for hp in args.node]

    try:

        # Launch nameserver
        if args.launch_nameserver:
            launch(nameserver.host, "./nameserver.py --port=%d" % nameserver.port)
            time.sleep(1)

        # Launch nodes
        for node in nodes:
            launch(node.host, "./node.py --port=%d --nameserver=%s" % (node.port, nameserver))

        # Either run client for tests, or wait for input
        if args.run_tests:
            time.sleep(1)
            launch("localhost", "./client.py --nameserver=%s" % (str(nameserver)), wait=True)
        else:
            raw_input("Running. Press Enter to shut down.")

    finally:

        # Kill each node
        for node in nodes:
            kill(node.host, "./node.py")

        # Kill nameserver
        if args.launch_nameserver:
            kill(nameserver.host, "./nameserver.py")
