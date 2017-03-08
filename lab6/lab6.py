#!/usr/bin/env python

import argparse
import json
import os
import pexpect
import re
import subprocess
import time

class Router:
    '''
        Opens pexpect channel, cleans up terminal length, sends commands
    '''
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
    ping_response = subprocess.call(['ping', '-c', '2', '-t', '1', ip_addr], stdout=open(os.devnull, 'wb'))
    if ping_response == 0:
        result = True
    return result

def deploy_bgp(router, bgp_info):
    '''
        Deploys BGP, adds neighbors, restricts advertised prefixes
    '''
    router.sendCmd('configure terminal')
    for prefix in bgp_info[router.name]['bgp']['AdvPrefixes']:
        router.sendCmd('ip prefix-list OUTBOUND permit {}'.format(prefix))
    router.sendCmd('router bgp {}'.format(bgp_info[router.name]['bgp']['LocalAS']))
    router.sendCmd('bgp router-id {}'.format(bgp_info[router.name]['bgp']['RouterID']))
    router.sendCmd('redistribute connected')
    for neighbor in bgp_info[router.name]['neighbors']:
        router.sendCmd('neighbor {} remote-as {}'.format(neighbor['ip'],neighbor['RemoteAS']))
        router.sendCmd('neighbor {} shutdown'.format(neighbor['ip']))
        router.sendCmd('neighbor {} prefix-list OUTBOUND out'.format(neighbor['ip']))
        router.sendCmd('no neighbor {} shutdown'.format(neighbor['ip']))
    router.sendCmd('end')

def show_ip_bgp_nei(router):
    '''
        Some text munging to extract BGP neighbor, AS, and state information.
        A better solution would be textFSM, but it violates the pip install requirement
    '''

    result = []
    pre = router.sendCmd('show ip bgp neighbors').split('\n')
    for line in pre:
        if re.match('^BGP neighbor is ', line):
            words = re.split('[ |,]', line)
            neighbor = words[3]
            asn = words [8]
            for line in pre:
                if re.match('^  BGP state = ', line):
                    words = re.split('[ |,]', line)
                    state = words[5]
                    result.append((neighbor, asn, state))
    print router.name
    print '{:20s}{:20s}{:20s}'.format('BGP Neighbor IP', 'BGP Neighbor AS', 'BGP Neighbor State')
    for r in result:
        print '{:20s}{:20s}{:20s}'.format(r[0], r[1], r[2])

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

    for r in router_list:
        deploy_bgp(r, bgp_info)

    print 'Waiting for BGP to converge...'
    time.sleep(60) #wait for BGP to converge

    for r in router_list:
        show_ip_bgp_nei(r)

if __name__=='__main__':
    main()
