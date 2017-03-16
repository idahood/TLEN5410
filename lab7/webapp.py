#!/usr/bin/env python

import pexpect
import sqlite3
from flask import Flask, render_template, request, Markup
from lab7 import OOB

app = Flask(__name__)

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

@app.route('/R<int:n>/nei')
def OSPFNei(n):
    name = 'R{}'.format(n)
    title_text = Markup('{} OSPF Neighbors'.format(name))

    oob = OOB('127.0.0.1', name, 2000 + n)
    pre = oob.send_cmd('sh ip ospf nei').split('\n')
    pre.pop(0)   #Remove cmd 
    pre.pop(0)   #Remove blank line
    pre.pop(0)   #Remove header info
    pre.pop(-1)  #Remove prompt
    result = '<table style="width:100%"><tr><th>Neighbor ID</th><th>State</th><th>Interface</th></tr>'
    for r in pre:
        result += '<tr>'
        t = (r.split()[0], r.split()[2], r.split()[5])
        for i in t:
            result += '<td>{}</td>'.format(i)
        result += '</tr>'

    body_text = Markup('{}:<br>{}</table>'.format(name, result))

    return render_template('template.html', titleText = title_text,
        bodyText=body_text)

@app.route('/ping')
def ping():
    title_text = Markup('R1 Loopback to R3 Loopback ping')
    result = ''
    oob = OOB('127.0.0.1', 'R1', 2001)
    pre = oob.send_cmd('ping 30.0.0.1 so lo0').split('\n')
    pre.pop(0)  #Remove command
    pre.pop(0)  #Remove blank line
    pre.pop(-1) #Remove prompt
    for i in pre:
        result += i.strip() + '<br>'
    if pre[3].strip() == '!!!!!':
        result += 'OSPF has been successfully configured'
    else:
        result += 'You are a bad person!'

    body_text = Markup(result)
    return render_template('template.html', titleText = title_text,
        bodyText=body_text)

def main():
    app.debug = True
    app.run(host = '0.0.0.0', port=80)

if __name__ == '__main__':
    main()
