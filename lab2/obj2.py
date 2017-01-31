#!/usr/bin/env python

'''
TLEN 5410 Lab 2 Objective 2

SNMP Dashboard Generator
'''
import subprocess

def snmpgetv1(community, host, oid):
    '''
    Generic wrapper for SNMP get version 1
    '''

    result = subprocess.check_output(["snmpget", "-v", "1",
                                      "-c", community, host, oid])

def snmpgetv2(community, host, oid):
    '''
    Generic wrapper for SNMP get version 2
    '''

    result = subprocess.check_output(["snmpget", "-v", "2c",
                                      "-c", community, host, oid])

def snmpgetv3(community, user, host, oid):
    '''
    Generic wrapper for SNMP get version 3
    '''

    result = subprocess.check_output(["snmpget", "-v", "3",
                                      "-c", community, "-u", user, host, oid])

def main():
    '''
    Define host list
    Define OID list
    Iterate (Profit!)
    '''

    router1 = '198.51.100.3'
    router2 = '198.51.100.4'
    router3 = '198.51.100.5'

    sys_contact = '.1.3.6.1.2.1.1.4.0'
    sys_name = '.1.3.6.1.2.1.1.5.0'
    sys_location = '.1.3.6.1.2.1.1.6.0'
    if_number = '.1.3.6.1.2.1.2.1.0'
    sys_uptime = '.1.3.6.1.2.1.1.3.0'

    oids = [sys_contact, sys_name, sys_location, if_number, sys_uptime]

    for oid in oids:
        snmpgetv1('public', router1, oid)
    for oid in oids:
        snmpgetv2('public', router2, oid)
    for oid in oids:
        snmpgetv3('public', 'public', router3, oid)

if __name__ == '__main__':
    main()
