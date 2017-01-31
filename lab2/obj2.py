#!/usr/bin/env python

'''
TLEN 5410 Lab 2 Objective 2

SNMP Dashboard Generator
'''
import subprocess

class Router:
    '''
    SNMP router object, contains OID list, SNMP pollers, and results
    '''

    oids = {'sys_contact': '.1.3.6.1.2.1.1.4.0',
            'sys_name': '.1.3.6.1.2.1.1.5.0',
            'sys_location': '.1.3.6.1.2.1.1.6.0',
            'if_number': '.1.3.6.1.2.1.2.1.0',
            'sys_uptime': '.1.3.6.1.2.1.1.3.0'}

    results = {'sys_contact': None,
               'sys_name': None,
               'sys_location': None,
               'if_number': None,
               'sys_uptime': None}

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr

    def snmpgetv1(self, community, host, oid):
        '''
        Generic wrapper for SNMP get version 1
        '''

        output = subprocess.check_output(["snmpget", "-v", "1",
                                          "-c", community, host, oid])

        #Text mangling to get right of equal sign
        result = output.rsplit('=')[-1].strip()
        #Text mangling to get portion right of data type
        return result.split(':', 1)[-1].strip()

    def snmpgetv2(self, community, host, oid):
        '''
        Generic wrapper for SNMP get version 2
        '''

        output = subprocess.check_output(["snmpget", "-v", "2c",
                                          "-c", community, host, oid])

        #Text mangling to get right of equal sign
        result = output.rsplit('=')[-1].strip()
        #Text mangling to get portion right of data type
        return result.split(':', 1)[-1].strip()

    def snmpgetv3(self, community, user, host, oid):
        '''
        Generic wrapper for SNMP get version 3
        '''

        output = subprocess.check_output(["snmpget", "-v", "3",
                                          "-c", community, "-u", user, host, oid])

        #Text mangling to get right of equal sign
        result = output.rsplit('=')[-1].strip()
        #Text mangling to get portion right of data type
        return result.split(':', 1)[-1].strip()

    def display_dashboard(self):
        '''
        Print dashboard per lab spec
        '''

        print 'Contact: ' + self.results['sys_contact']
        print 'Name: ' + self.results['sys_name']
        print 'Location: ' + self.results['sys_location']
        print 'Number: ' + self.results['if_number']
        print 'Uptime: ' + self.results['sys_uptime'] + '\n'

def main():
    '''
    Define host list
    Define OID list
    Iterate (Profit!)
    '''

    router1 = Router('198.51.100.3')
    router2 = Router('198.51.100.4')
    router3 = Router('198.51.100.5')

    for oid in router1.oids:
        router1.results[oid] = router1.snmpgetv1('public', router1.ip_addr, router1.oids[oid])
    for oid in router2.oids:
        router2.results[oid] = router2.snmpgetv2('public', router2.ip_addr, router2.oids[oid])
    for oid in router3.oids:
        router3.results[oid] = router3.snmpgetv3('public', 'public', router3.ip_addr, router3.oids[oid])

    print 'SNMPv1'
    router1.display_dashboard()
    print 'SNMPv2c'
    router2.display_dashboard()
    print 'SNMPv3'
    router3.display_dashboard()

if __name__ == '__main__':
    main()
