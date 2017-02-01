#!/usr/bin/env python

'''
TLEN 5410 Lab 2 Obiective 5

SNMP Dashboard Generator
'''

import subprocess

class Router:
    '''
    SNMP router obiect
    '''

    def __init__(self, ip_addr, community):
        '''
        To do:
        There are some pretty horrible failure scenarios here.
        Add some error handling for being unable to reach IP
        '''

        self.oids = {'ifIndex': '.1.3.6.1.2.1.2.2.1.1',
                     'ifName': '.1.3.6.1.2.1.31.1.1.1.1',
                     'ifAlias': '1.3.6.1.2.1.31.1.1.1.18',
                     'ifOperStatus': '.1.3.6.1.2.1.2.2.1.8',
                     'ifPhysAddress': '.1.3.6.1.2.1.2.2.1.6',
                     'ifAdminStatus': '.1.3.6.1.2.1.2.2.1.7',
                     'ifInUcastPkts': '.1.3.6.1.2.1.2.2.1.11',
                     'ipAdEntIfIndex': '1.3.6.1.2.1.4.20.1.2',
                     'ipAdEntAddr': '.1.3.6.1.2.1.4.20.1.1',
                     'ipAdEntNetMask': '1.3.6.1.2.1.4.20.1.3'}

        self.ip_addr = ip_addr
        self.community = community

        #Thar be dragons here. We are assuming an ordered return based on ifIndex
        #To do:
        #map this? I should ask someone smart

        self.ifIndex = self.snmpbulkwalkv2(self.oids['ifIndex'])
        self.ifName = self.snmpbulkwalkv2(self.oids['ifName'])
        self.ifAlias = self.snmpbulkwalkv2(self.oids['ifAlias'])
        self.ifOperStatus = self.snmpbulkwalkv2(self.oids['ifOperStatus'])
        self.ifPhysAddress = self.snmpbulkwalkv2(self.oids['ifPhysAddress'])
        self.ifAdminStatus = self.snmpbulkwalkv2(self.oids['ifAdminStatus'])
        self.ifInUcastPkts = self.snmpbulkwalkv2(self.oids['ifInUcastPkts'])
        self.ipAdEntIfIndex = self.snmpbulkwalkv2(self.oids['ipAdEntIfIndex'])
        self.rawIpAdEntAddr = self.snmpbulkwalkv2(self.oids['ipAdEntAddr'])
        self.rawIpAdEntNetMask = self.snmpbulkwalkv2(self.oids['ipAdEntNetMask'])
        self.ipAdEntAddr = [None] * len(self.ifIndex)
        self.ipAdEntNetMask = [None] * len(self.ifIndex)

        #This suuuuuucks, a transform for the IP-MIB to IF-MIB mapping.
        #There is probably a clever solution using lambdas with the ifIndex as a dict key

        for i, j in enumerate(self.ipAdEntIfIndex):
            self.ipAdEntAddr[self.ifIndex.index(j)] = self.rawIpAdEntAddr[i]
            self.ipAdEntNetMask[self.ifIndex.index(j)] = self.rawIpAdEntNetMask[i]

    def snmpbulkwalkv2(self, oid):
        '''
        Generic wrapper for SNMP bulkget version 2
        '''

        output = subprocess.check_output(["snmpbulkwalk", "-v", "2c",
            "-c", self.community, self.ip_addr, oid]).split('\n')
        result = []
        for line in output:
            #Text mangling to get right of equal sign
            line = line.rsplit('=')[-1].strip()
            #Text mangling to get portion right of data type
            result.append(line.split(':', 1)[-1].strip())
        if result[-1] == '': result.pop()   #Some magic due to how split works
        return result

    def display_dashboard(self):
        '''
        Print dashboard per lab spec
        '''

        for i, j in enumerate(self.ifIndex):
            print '    {:<10s}{:<20s}{:<8s}{:<20s}{:<8s}{:<10s}{:<16s}{:<16s}'.format(self.ifName[i], self.ifAlias[i], self.ifOperStatus[i], self.ifPhysAddress[i], self.ifAdminStatus[i], self.ifInUcastPkts[i], self.ipAdEntAddr[i], self.ipAdEntNetMask[i])

def main():
    '''
    Highly dependent on the Router class object
    '''

    router1 = Router('198.51.100.3', 'public')
    router2 = Router('198.51.100.4', 'public')
    router3 = Router('198.51.100.5', 'public')

    print '    {:<10s}{:<20s}{:<8s}{:<20s}{:<8s}{:<10s}{:<16s}{:<16s}'.format('Name', 'Description','Oper', 'PhysAddress', 'Admin', 'InUPkts', 'IPv4 Addr', 'IPv4 Mask')

    print "R1"
    router1.display_dashboard()
    print "R2"
    router2.display_dashboard()
    print "R3"
    router3.display_dashboard()

if __name__ == '__main__':
    main()
