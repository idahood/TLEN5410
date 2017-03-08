#!/usr/bin/env python

import argparse
import json
import os
import pexpect
import re
import subprocess
from time import sleep

class Router:
    def __init__(self, ipAddr=None, user=None, password=None, name=None, port=22):
        MAX_TIMEOUT = 3
        self.ipAddr = ipAddr
        self.user = user
        self.password = password
        self.port = port
        self.name = name

        self.sshConn = pexpect.spawn('ssh -l {} {} -p {}'.format(self.user, self.ipAddr, self.port))
        self.sshConn.timeout = MAX_TIMEOUT
        self.sshConn.expect('[P|p]assword:')
        self.sendCmd(self.password)
        self.sendCmd('terminal length 0')

    def sendCmd(self, cmd):
        self.sshConn.sendline(cmd.rstrip())
        self.sshConn.expect('[#|>]')
        return self.sshConn.before

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

def deploy_bgp(router, bgp_info):
    '''
        Deploys BGP, adds neighbors, restricts advertised prefixes
    '''
    router.sendCmd('configure terminal')
    for prefix in bgp_info[router.name]['bgp']['AdvPrefixes']:
        router.sendCmd('ip prefix-list ADVPREFIX permit ' + prefix)
    router.sendCmd('router bgp ' + bgp_info[router.name]['bgp']['LocalAS'])
    router.sendCmd('bgp router-id ' + bgp_info[router.name]['bgp']['RouterID'])
    router.sendCmd('redistribute connected')
    for neighbor in bgp_info[router.name]['neighbors']:
        router.sendCmd('neighbor ' + neighbor['ip'] + ' remote-as ' + neighbor['RemoteAS'])
        router.sendCmd('neighbor ' + neighbor['ip'] + ' shutdown')
        router.sendCmd('neighbor ' + neighbor['ip'] + ' prefix-list ADVPREFIX out')
        router.sendCmd('no neighbor ' + neighbor['ip'] + ' shutdown')
    router.sendCmd('end')

def show_ip_bgp_nei(router):
    pre = router.sendCmd('show ip bgp neighbors').split('\n')
    for line in pre:
        if re.match('^BGP neighbor is ', line):
            print line
        if re.match('^  BGP state = ', line):
            print line

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

    for i in ssh_info:
        if test_ping(i['interface']['f0/0']['ip']):
            print i['name'] + ' is reachable'
        else:
            print i['name'] + ' is unreachable'
            exit(1)

    router_list = []

    for i in ssh_info:
        router_list.append(Router(i['interface']['f0/0']['ip'], i['credentials']['username'], i['credentials']['password'], i['name']))
    '''
    for r in router_list:
        deploy_bgp(r, bgp_info)

    print 'Waiting for BGP to converge...'
    sleep(60) #wait for BGP to converge
    '''
    for r in router_list:
        show_ip_bgp_nei(r)

if __name__=='__main__':
    main()
