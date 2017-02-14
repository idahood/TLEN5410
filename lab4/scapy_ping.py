#!/usr/bin/env python

import argparse
from scapy.all import *

def main():
    '''
        Build a simple ICMP request using scapy
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="The host to ping IE 192.168.1.1")
    args = parser.parse_args()

    send(IP(dst=args.host)/ICMP())

if __name__ == "__main__":
    main()
