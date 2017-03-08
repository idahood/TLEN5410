#!/usr/bin/env python

import argparse
import json
import os
import subprocess
from pprint import pprint

def load_json(filename):
    '''
        Expects json formatted file and returns json data
    '''
    result = None
    with open(filename) as data:
        result = json.load(data)

    return result

def test_ping(ip_addr):
    '''
        Attempts to ping an IP address. Returns True if succesful
    '''
    result = False
    ping_response = subprocess.call(['ping', '-c', '1', '-t', '1', ip_addr], stdout=open(os.devnull, 'wb'))
    if ping_response == 0:
        result = True
    return result

def main():
    '''
        TLEN 5410 Lab 6
        Build iBGP peering mesh between two routers using configuration details stored in external
            configuration files. Leverages paramiko/pexpect to connect to Cisco routers. Assumes
            Cisco routers already have IP configuration and ssh access enabled.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("ssh", help="ssh config file")
    parser.add_argument("bgp", help="bgp config file")
    args = parser.parse_args()

    ssh_info = load_json(args.ssh)
    bgp_info = load_json(args.bgp)

    pprint(ssh_info)
    pprint(bgp_info)

    for i in ssh_info:
        if not test_ping(i['ip']['f0/0'].split('/')[0]):
            print i['name'] + " unreachable"
            exit(1)

if __name__=='__main__':
    main()
