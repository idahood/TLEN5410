#!/usr/bin/env python

import os
import pexpect
import re
import sqlite3
import subprocess
import time
from flask import Flask, render_template, request, Markup

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

def deploy_ospf(router, ospf_info):
    '''
        Deploy OSPFv2 using interface based IOS config
    '''

    router.send_cmd('configure terminal')
    for interface in ospf_info:
        router.send_cmd('interface {}'.format(interface))
        router.send_cmd('ip ospf {} area {}'.format(
            ospf_info[interface]['process_id'],
            ospf_info[interface]['area']))
    router.send_cmd('end')

app = Flask(__name__)

@app.route('/')
def index():
    return('Hello World')

@app.route('/R<int:n>', methods=['GET', 'POST'])
def Router(n):
    name = 'R{}'.format(n)
    title_text = Markup(name)
    body_text = Markup('<h1>Login Credentials for {}</h1><br>Enter Username:<br><form method=post action=/{}><input type=text name=username></input><br>Enter Password:<br><input type=password name=password> </input<br><h1>OSPF Information for {}</h1><br>OSPF Process ID:<br><input type=text name=proc_id> </input><br>OSPF Area ID:<br><input type=text name=area_id> </input><br>OSPF Area Interfaces (comma separated)<br><input type=text name=area_interfaces> </input><br>OSPF Backbone Interfaces (comma separated):<br><input type=text name=backbone_interfaces> </input><br><input type=submit name=submit value=submit></form>'.format(name, name, name))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        proc_id = request.form['proc_id']
        area_id = request.form['area_id']
        area_interfaces = request.form['area_interfaces']
        backbone_interfaces = request.form['backbone_interfaces']

        conn = sqlite3.connect('lab7.db')
        c = conn.cursor()
        t = (name,)
        c.execute("SELECT name FROM ospf WHERE name=?", t)

        if c.fetchone() == None:
            c.execute('INSERT INTO ospf VALUES (?,?,?,?,?,?,?)', (name,
                username, password, proc_id, area_id, 
                area_interfaces, backbone_interfaces))
        else:
            c.execute('UPDATE ospf SET username = ?, password = ?, proc_id = ?, area_id = ?, area_ints = ?, backbone_ints = ? WHERE name = ?', (username, password, proc_id, area_id, area_interfaces, backbone_interfaces, name))

        conn.commit()

    return render_template('template.html', titleText = title_text,
        bodyText=body_text)

def main():
    app.debug = True
    app.run(host = '0.0.0.0', port=80)

if __name__ == '__main__':
    main()
