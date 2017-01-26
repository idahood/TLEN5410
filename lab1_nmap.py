#!/usr/bin/env python

import pickle
import subprocess
import xml.etree.ElementTree as ET
from time import time

cidr = "10.0.0.0/24"
current = "/tmp/" + str(time()) + ".xml"

old_host_list = []
try:
    open("lab1.p", "r")
    old_host_list = pickle.load(open("lab1.p", "rb"))
except:
    pass

subprocess.call(["nmap", "-sn", cidr, "-oX", current])  #Dump some XML from NMAP

now = ET.parse(current) #Parse XML
root = now.getroot()
host_list = []
for host in root.findall("host"):
    for address in host.findall("address"):
        host_list.append(address.attrib["addr"])

subprocess.call(["rm", current])    #Cleanup temp file

pickle.dump(host_list, open("lab1.p", "wb"))

if old_host_list != host_list:
    print "Change in host list!"
    print "Current hosts:"
    for host in host_list:
        print host

else:
    print "No host differences"
