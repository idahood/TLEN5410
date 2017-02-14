#!/usr/bin/env python

import argparse
from scapy.all import *

def main():
    '''
        Send a telnet SYN using scapy
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="The destination host IE 192.168.1.1")

    args = parser.parse_args()

    message = ( (IP(dst=args.host)) / TCP(dport=23,flags='S') )
    message.show()
    answer, unanswer = sr(message)
    answer.show()

if __name__ == "__main__":
    main()
