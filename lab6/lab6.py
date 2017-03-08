#!/usr/bin/env python

import argparse
import json
import os
import pexpect
import re
import subprocess
from threading import Thread
import time

class Router:
    '''
        Opens pexpect channel, cleans up terminal length, sends commands
    '''
    def __init__(self, ip_addr=None, user=None, password=None,
        name=None, port=22):

        MAX_TIMEOUT = 3
        self.ip_addr = ip_addr
        self.user = user
        self.password = password
        self.port = port
        self.name = name

        self.ssh_conn = pexpect.spawn('ssh -l {} {} -p {}'
            .format(self.user, self.ip_addr, self.port))
        self.ssh_conn.timeout = MAX_TIMEOUT
        self.ssh_conn.expect('[P|p]assword:')
        self.send_cmd(self.password)
        self.send_cmd('terminal length 0')

    def send_cmd(self, cmd):
        '''
            Sends string to IOS device, returns string output
        '''
        self.ssh_conn.sendline(cmd.rstrip())
        self.ssh_conn.expect('[#|>]')
        return self.ssh_conn.before

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
    ping_response = subprocess.call(['ping', '-c', '2', '-t', '1',
        ip_addr], stdout=open(os.devnull, 'wb'))
    if ping_response == 0:
        result = True
    return result

def deploy_bgp(router, bgp_info):
    '''
        Deploys BGP, adds neighbors, restricts advertised prefixes
    '''
    router.send_cmd('configure terminal')
    for prefix in bgp_info[router.name]['bgp']['AdvPrefixes']:
        router.send_cmd('ip prefix-list OUTBOUND permit {}'.format(prefix))
    router.send_cmd('router bgp {}'.format(
        bgp_info[router.name]['bgp']['LocalAS']))
    router.send_cmd('bgp router-id {}'.format(
        bgp_info[router.name]['bgp']['RouterID']))
    router.send_cmd('redistribute connected')
    for neighbor in bgp_info[router.name]['neighbors']:
        router.send_cmd('neighbor {} remote-as {}'.format(
            neighbor['ip'], neighbor['RemoteAS']))
        router.send_cmd('neighbor {} shutdown'.format(neighbor['ip']))
        router.send_cmd('neighbor {} prefix-list OUTBOUND out'.format(
            neighbor['ip']))
        router.send_cmd('no neighbor {} shutdown'.format(neighbor['ip']))
    router.send_cmd('end')

def show_ip_bgp_nei(router):
    '''
        Some text munging to extract BGP neighbor, AS, and state information
        A better solution would be textFSM,
        but it violates the pip install requirement
    '''

    result = []
    pre = router.send_cmd('show ip bgp neighbors').split('\n')
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
    print '{:20s}{:20s}{:20s}'.format(
        'BGP Neighbor IP', 'BGP Neighbor AS', 'BGP Neighbor State')
    for item in result:
        print '{:20s}{:20s}{:20s}'.format(item[0], item[1], item[2])

def main():
    '''
        TLEN 5410 Lab 6
        Build iBGP peering mesh between two routers using configuration
        details stored in external configuration files. Leverages pexpect
        to connect to Cisco routers. Assumes IOS routers already have
        IP configuration and ssh access enabled.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("ssh", help="ssh config file")
    parser.add_argument("bgp", help="bgp config file")
    args = parser.parse_args()

    ssh_info = load_json(args.ssh)
    bgp_info = load_json(args.bgp)

    for router in ssh_info:
        if test_ping(router['interface']['f0/0']['ip']):
            print router['name'] + ' is reachable'
        else:
            print router['name'] + ' is unreachable'
            exit(1)

    router_list = []

    for router in ssh_info:
        router_list.append(Router(router['interface']['f0/0']['ip'],
            router['credentials']['username'],
            router['credentials']['password'],
            router['name']))

    for router in router_list:
        thread = Thread(deploy_bgp(router, bgp_info))
        thread.start()

    print 'Waiting for BGP to converge...'
    time.sleep(60) #wait for BGP to converge

    for router in router_list:
        show_ip_bgp_nei(router)

if __name__ == '__main__':
    main()
