#!/usr/bin/env python
"""Basically a dumb wrapper for NMAP.

This module accepts a CIDR input, runs an NMAP ping sweep against the range,
and then notifies if the state of active hosts on the network has changed.

Returns True if state is unchanged.

"""

import argparse
import pickle
import subprocess
import xml.etree.ElementTree as ET
from time import time

def get_hosts(path):
    """Parse NMAP XML output file and return list of active hosts"""
    now = ET.parse(path) #Parse XML
    root = now.getroot()
    host_list = []
    for host in root.findall("host"):
        for address in host.findall("address"):
            host_list.append(address.attrib["addr"])
    return host_list

def main():
    """Yarr there be some crappy file handling here"""
    parser = argparse.ArgumentParser()
    parser.add_argument("cidr", help="The CIDR block to scan IE 192.168.0.0/24")
    args = parser.parse_args()

    tmp_file = "/tmp/" + str(time()) + ".xml"

    old_host_list = []
    try:
        open("lab1.p", "r")
        old_host_list = pickle.load(open("lab1.p", "rb"))
    except IOError:
        pass

    subprocess.check_output(["nmap", "-sn", args.cidr, "-oX", tmp_file])
    #Dump some XML from NMAP

    host_list = get_hosts(tmp_file)

    subprocess.call(["rm", tmp_file])    #Cleanup temp file

    pickle.dump(host_list, open("lab1.p", "wb"))

    if old_host_list != host_list:
        print "Change in host list!"
        print "Current hosts:"
        for host in host_list:
            print host
        return False

    else:
        print "No host differences"
        return True

if __name__ == "__main__":
    main()
