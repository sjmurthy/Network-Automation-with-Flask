import paramiko
import time
import ConfigParser
import subprocess
from threading import Thread
import sys
import os
from prettytable import PrettyTable

def bgp(i):
    ip=config.get(routers[i], 'ip')
    username=config.get(routers[i],'user')
    password=config.get(routers[i],'pass')

    ping_output=subprocess.check_output(['ping','-c','4',ip])
    ping_output=ping_output.decode('utf-8')
    print("Output of the Ping Test is:/\n")
    print("----------------------------------")
    print(ping_output)
    print("-----------------------------------")
    for each in ping_output.splitlines():
        each=each.decode()
        if "ttl" in each:
            ping_ip="success"

    if ping_ip == "success":
        print("Ping succesfull on : " + routers[i])
        print("Router" + routers[i] + " is reachable .Establishing an SSh session")
        bgpconflist=[]
        bgpconflist=bgpconf(i)
        # print(bgpconflist)
        if (bgpconflist[0]=="no"):
            print("pls make sure that bgpconf file is present ")
            sys.exit()
        else:

            try:

                bgpnetwork=bgpconflist[4].split('\n')
                #rint(bgpnetwork +"reached here")
                m=len(bgpnetwork)
                session=paramiko.SSHClient()
                session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                session.connect(ip, username=username, password=password)
                connection=session.invoke_shell()
                connection.send("terminal length 0\n")
                time.sleep(1)
                connection.send("\n")
                connection.send("configure terminal\n")
                time.sleep(1)
                connection.send("\n")
                connection.send("router bgp "+bgpconflist[0]+"\n")
                time.sleep(1)
                p=0
                while (p<m):
                  connection.send("network "+bgpnetwork[p]+"\n")
                  time.sleep(1)
                  p=p+1
                connection.send("neighbor "+bgpconflist[2]+" remote-as "+bgpconflist[3]+"\n")
                time.sleep(1)
                connection.send("end\n")

                router_output=connection.recv(65535)
                print(router_output)
                print("suucessfully configured BGP on" + routers[i])
                connection.send("show ip bgp neighbors\n")
                time.sleep(2)
                showconf=connection.recv(65535)
                split=showconf.splitlines()
                neighborlist=[]
                remoteas=[]
                bgpstate=[]
                for lines in split:
                    if "BGP neighbor is"in lines:
                        neighborsplit=lines.split(' ')
                        neighborlist.append(neighborsplit[3].replace(",",""))
                        remoteas.append(neighborsplit[7].replace(",",""))
                    if "BGP state" in lines:
                        bgplist=lines.split(' ')
                        bgpstate.append(bgplist[5].replace(",",""))
                table=PrettyTable(["BGP neighbor IP","BGP neighbor AS","BGP neighbor state"])
                ngbs=len(neighborlist)
                d=0
                while (d<ngbs):
                    table.add_row([str(neighborlist[d]),str(remoteas[d]),str(bgpstate[d])])
                    d=d+1
                print("BGP state-table for " +routers[i])
                print(table)
               #print(bgpstate)
               #print(neighborlist)
               #print(remoteas)


                session.close()
            except:
                print("Unexpected error occured while opening the terminal.")
    else:
        print("Ping Unsuccesfull.Connection cannot be made for "+routers[i])
        exit()
def bgpconf(i):
    if os.path.isfile('bgp.conf'):
        config1= ConfigParser.ConfigParser()
        config1.read('bgp.conf')
        bgplist=config1.sections()
        bgpconf=[]
        bgpconf.append(config1.get(bgplist[i],'localAS'))
        bgpconf.append(config1.get(bgplist[i],'routerID'))
        bgpconf.append(config1.get(bgplist[i],'neighborIP'))
        bgpconf.append(config1.get(bgplist[i],'neighborAS'))
        bgpconf.append(config1.get(bgplist[i],'networkAD'))
        return bgpconf
    else :
        bgpconf=[]
        bgpconf.append("no")
        return bgpconf
if os.path.isfile('sshinfo.conf'):
    config = ConfigParser.ConfigParser()
    config.read('sshinfo.conf')
    routers=config.sections()
    print("The routers to configure are "+ str(routers))
    length=len(routers)
    i=0
    threads = []
    for router in routers:
        t=Thread(target=bgp,args=(i,))
        i=i+1
        threads.append(t)
       # print("reached here")
    for x in threads:
        x.start()
    for x in threads:
        x.join()
else:
    print("Please make sure that the config file sshinfo.conf is present int he folder")
    quit()
print("end of program")
