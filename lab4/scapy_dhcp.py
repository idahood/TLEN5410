#!/usr/bin/env python

import argparse
from scapy.all import *

def main():
    '''
        Send a DHCP Discover message using scapy
    '''

    message = (( Ether(src="12:48:98:50:94:c8", dst="ff:ff:ff:ff:ff:ff") ) /
              ( IP(src="0.0.0.0", dst="255.255.255.255") ) / 
              ( UDP(sport=68, dport=67) ) /
              ( BOOTP(chaddr="1248985094c8", xid=RandInt()) ) /
              ( DHCP(options=[("message-type", "discover"), "end"]) ))

    message.show()
    sendp(message, iface='tap0')

if __name__ == "__main__":
    main()
