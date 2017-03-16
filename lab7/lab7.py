#!/usr/bin/env python

import argparse
import os
import pexpect
import re
import sqlite3
import subprocess
import time

class OOB:
    '''
        Simulated OOB connection (leverages dynamips console port)
        Builds channel, cleans up termiinal length, sends commands
    '''
    def __init__(self, ip_addr=None, name=None, port=2000):

        MAX_TIMEOUT = 5
        self.ip_addr = ip_addr
        self.name = name
        self.port = port

        self.oob_conn = pexpect.spawn('telnet {} {}'
            .format(self.ip_addr, self.port))
        self.oob_conn.timeout = MAX_TIMEOUT
        self.send_cmd('')   #Send Enter to grab prompt (console specific)
        self.send_cmd('terminal length 0')

    def send_cmd(self, cmd):
        '''
            Sends string to IOS device, returns string output
        '''
        self.oob_conn.sendline(cmd + '\r')
        self.oob_conn.expect('[#|>]')
        return self.oob_conn.before.strip()

def deploy_ospf(oob, cursor):
    '''
        Deploy OSPFv2 using interface based IOS config
    '''

    name = (oob.name,)
    cursor.execute('SELECT proc_id, area_id, area_ints, backbone_ints FROM ospf where name=?', name)
    query = cursor.fetchone()

    proc_id = query[0]
    area_id = query[1]
    area_ints = query[2].split(',')
    backbone_ints = query[3].split(',')

    oob.send_cmd('configure terminal')
    if not area_ints == ['']:
        for interface in area_ints:
            oob.send_cmd('interface {}'.format(interface))
            oob.send_cmd('ip ospf {} area {}'.format(
                proc_id, area_id))
            
    if not backbone_ints == ['']:
        for interface in backbone_ints:
            oob.send_cmd('interface {}'.format(interface))
            oob.send_cmd('ip ospf {} area 0'.format(
                proc_id))

    oob.send_cmd('end')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("db", help="sqlite3 db file")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    c = conn.cursor()

    oob_list = []
    for router in c.execute('SELECT name FROM ospf'):
        oob_list.append( OOB('127.0.0.1', router[0], 
            2000 + int(router[0].lstrip('R'))))

    for oob in oob_list:
        deploy_ospf(oob, c)

if __name__ == '__main__':
    main()
