#!/usr/bin/env python

import argparse
import subprocess
from lab6 import load_json
from lab6 import test_ping
from lab6 import Router
from threading import Thread

def show_run(router):
    pre = router.send_cmd('show run').split('\n')
    pre.pop(0) #remove command
    pre.pop(-1) #remove router name

    with open('{}.cfg'.format(router.name), 'w') as config_file:
        for line in pre:
            config_file.write(line + '\n')

def main():
    '''
        TLEN 5410 Lab 6 Extra Credit
        Download router startup configuration, and upload to S3
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("ssh", help="ssh config file")
    args = parser.parse_args()

    ssh_info = load_json(args.ssh)

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
        thread = Thread(show_run(router))
        thread.start()

    subprocess.call('s3cmd', 'put', '*.cfg', 's3://TLEN5410')

if __name__ == '__main__':
    main()
