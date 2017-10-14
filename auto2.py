from flask import Flask ,render_template,request
import sys
import os
import sqlite3
import paramiko
import time
import subprocess
from prettytable import PrettyTable


app = Flask(__name__)
db=sqlite3.connect('ospfconf.sql3')
db.row_factory=sqlite3.Row

@app.route('/')
def index():
    return render_template("index.html")
@app.route('/neighbor')
def neighbor():
        cursor=db.cursor()
        query="select * from ospf where routerid=?"
        routerid="R2"
        t=(routerid,)
        cursor.execute(query,t)
        rows=cursor.fetchall()
        #print("reached rows")
        #print(rows)
        for row in rows:
            connection(routerid,row,"1","0")
        return render_template("neighbor.html")
@app.route('/ping')
def ping():
        cursor=db.cursor()
        query="select * from ospf where routerid=?"
        routerid="R3"
        t=(routerid,)
        cursor.execute(query,t)
        rows=cursor.fetchall()
        for row in rows:
            loopbackip=row[6]
        print(loopbackip)
        query="select * from ospf where routerid=?"
        routerid="R1"
        t=(routerid,)
        cursor.execute(query,t)
        rows=cursor.fetchall()
        for row in rows:
            pinger=connection(routerid,row,"2",loopbackip)
        if pinger == "success":
            return("Ospf has been successfully configured")
        else:
            return("Ping was unsuccessful.Check the config")


@app.route('/sendR1', methods=['GET', 'POST'])
def sender1():
    if request.method == 'POST':
        Router_1_username= request.form['username']
        print(Router_1_username)
        Router_1_password =request.form['password']
        print(Router_1_password)
        Router_1_ssh=request.form['ssh']
        print(Router_1_ssh)
        Router_1_processid = request.form['processid']
        print(Router_1_processid)
        Router_1_areaid = request.form['areaid']
        print(Router_1_areaid)
        Router_1_loopbackip =request.form['loopbackip']
        print(Router_1_loopbackip)
        insertrecord(db,"R1",Router_1_username,Router_1_password,Router_1_ssh,Router_1_processid,Router_1_areaid,Router_1_loopbackip ,"none","none","none","none","none","none","none")
        #queryresults(db, "R1")

        return render_template("reply.html")

    return render_template('form1.html')
@app.route('/sendR2', methods=['GET', 'POST'])
def sender2():
    if request.method == 'POST':
        Router_2_username= request.form['username']
        print(Router_2_username)
        Router_2_password =request.form['password']
        print(Router_2_password)
        Router_2_ssh=request.form['ssh']
        print(Router_2_ssh)
        Router_2_processid =request.form['processid']
        print(Router_2_processid)
        Router_2_loopbackip =request.form['loopbackip']
        print(Router_2_loopbackip)
        Router_2_loopbackarea =request.form['loopbackarea']
        print(Router_2_loopbackarea)
        Router_2_network1ip=request.form['network1ip']
        print(Router_2_network1ip)
        Router_2_wmask1=request.form['wmask']
        print(Router_2_wmask1)
        Router_2_areaid1=request.form['areaid']
        print(Router_2_areaid1)
        Router_2_network2ip=request.form['network2ip']
        print(Router_2_network2ip)
        Router_2_wmask2=request.form['wmask2']
        print(Router_2_wmask2)
        Router_2_areaid2=request.form['areaid2']
        print(Router_2_areaid2)
        insertrecord(db,"R2",Router_2_username,Router_2_password,Router_2_ssh,Router_2_processid,"none",Router_2_loopbackip ,Router_2_loopbackarea,Router_2_network1ip,Router_2_wmask1,Router_2_areaid1,Router_2_network2ip,Router_2_wmask2,Router_2_areaid2)
        #queryresults(db, "R2")
        return render_template("reply.html")

    return render_template('form2.html')
@app.route('/sendR3', methods=['GET', 'POST'])
def sender3():
    if request.method == 'POST':
        Router_3_username= request.form['username']
        print(Router_3_username)
        Router_3_password =request.form['password']
        print(Router_3_password)
        Router_3_ssh=request.form['ssh']
        print(Router_3_ssh)
        Router_3_processid=request.form['processid']
        print(Router_3_processid)
        Router_3_areaid=request.form['areaid']
        print(Router_3_areaid)
        Router_3_loopbackip=request.form['loopbackip']
        print(Router_3_loopbackip)
        insertrecord(db,"R3",Router_3_username,Router_3_password,Router_3_ssh,Router_3_processid,Router_3_areaid,Router_3_loopbackip ,"none","none","none","none","none","none","none")
        #queryresults(db, "R3")
        return render_template("reply.html")
    return render_template('form3.html')
def connection(router,row,show,loop):
            session=paramiko.SSHClient()
            session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #rows=cursor.fetchall()
            session.connect(row[3], username=row[1], password=row[2])
            connection=session.invoke_shell()
            connection.send("terminal length 0\n")
            time.sleep(1)
            if (show=='1'):
                connection.send("show ip ospf neighbor\n")
                time.sleep(1)
                ospf_output=connection.recv(65535)
                #print(ospf_output)
                ngp=[]
                state=[]
                interface=[]
                #print(len(ospf_output.splitlines()))
                ospf_output1=ospf_output.splitlines()
                for each in ospf_output1[4:-1]:
                    each=each.decode()
                    each1=each.split()
                    ngp.append(each1[0])
                    state.append(each1[2])
                    interface.append(each1[5])
                table=PrettyTable(["Neighbor ID","State","Interface"])
                ngbs=len(ngp)
                d=1
                while (d<ngbs):
                    table.add_row([str(ngp[d]),str(state[d]),str(interface[d])])
                    d=d+1
                print("OSPF neighbor status")
                print(table)
                    #print(each)
                #print(ngp)
                #print(state)
                #print(interface)
                session.close()
            elif (show=='2'):
                connection.send("ping "+loop+"\n")
                time.sleep(5)
                pingresult=connection.recv(65535)
                #pingresult=pingresult.decode()
                print("this is ping result"+pingresult)
                if "!" in pingresult:
                    return "success"
                else:
                    return "fail"
                session.close()
            else:
                connection.send("\n")
                connection.send("configure terminal\n")
                time.sleep(1)
                connection.send("\n")
                connection.send("router ospf "+row[4]+"\n")
                time.sleep(1)
                if router=="R2" :
                    connection.send("network "+row[8]+" "+row[9]+" area "+row[10]+"\n")
                    time.sleep(1)
                    connection.send("network "+row[11]+" "+row[12]+" area "+row[13]+"\n")
                    #connection.send("network "+row[6] +" 0.0.0.0 area "+row[5]+"\n")
                    time.sleep(1)
                    connection.send("network "+row[6]+" "+"0.0.0.0"+" "+"area "+row[7]+"\n")
                    time.sleep(1)
                else:
                    connection.send("network 0.0.0.0 255.255.255.255 area "+row[5]+"\n")
                    time.sleep(1)
                    connection.send("network "+row[6] +" 0.0.0.0 area "+row[5]+"\n")
                    time.sleep(1)
                router_output=connection.recv(65535)
                print(router_output)
                session.close()

def insertrecord(db,routerid,username,password,ssh,processid,areaid,loopbackip,loopbackarea,network1ip,wmask1,areaid1,network2ip,wmask2,areaid2):
    cursor=db.cursor()
    query="DELETE from ospf where routerid=?"
    t=(routerid,)
    cursor.execute(query,t)
    db.commit()
    query="insert into ospf(routerid,username,password,ssh,processid,areaid,loopbackip,loopbackarea,network1ip,wmask1,areaid1,network2ip,wmask2,areaid2) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    t=(routerid,username,password,ssh,processid,areaid,loopbackip,loopbackarea,network1ip,wmask1,areaid1,network2ip,wmask2,areaid2,)
    cursor.execute(query, t)
    db.commit()
    if routerid=="R1" :
        query="select * from ospf where routerid=?"
        t=(routerid,)
        cursor.execute(query,t)
        rows=cursor.fetchall()
        print("reached rows")
        print(rows)
        for row in rows:
            connection(routerid,row,"0","0")

    if routerid=="R2" :
        query="select * from ospf where routerid=?"
        t=(routerid,)
        cursor.execute(query,t)
        rows=cursor.fetchall()
        print("reached rows")
        print(rows)
        for row in rows:
            connection(routerid,row,"0","0")

    if routerid=="R3" :
        query="select * from ospf where routerid=?"
        t=(routerid,)
        cursor.execute(query,t)
        rows=cursor.fetchall()
        print("reached rows")
        print(rows)
        for row in rows:
            connection(routerid,row,"0","0")

if __name__=="__main__":
    app.run()
