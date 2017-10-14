import paramiko
import time
import ConfigParser
import subprocess
from threading import Thread
import boto3
import sys
import os
from prettytable import PrettyTable
def storage(i):
    session1=boto3.session.Session()
    s3=session1.resource('s3')
    ip=config.get(routers[i], 'ip')
    username=config.get(routers[i],'user')
    password=config.get(routers[i],'pass')
    q=[]
    for bucket in s3.buckets.all():
        #print(bucket.name)
        q=bucket.name
    print("the bucket chosen to backup for "+routers[i] + " is " +q)
    #print(q)

    session=paramiko.SSHClient()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    session.connect(ip, username=username, password=password)
    connection=session.invoke_shell()
    connection.send("terminal length 0\n")
    time.sleep(1)
    connection.send("\n")
    connection.send("show run\n")
    time.sleep(2)
    showconf=connection.recv(65535)
    f=open(routers[i]+".txt","w+")
    f.write(showconf)
    f.close()
    data=open(routers[i]+".txt",'rb')
    s3.Bucket(q).put_object(Key=routers[i]+".txt",Body=data)
if os.path.isfile('sshinfo.conf'):
    config = ConfigParser.ConfigParser()
    config.read('sshinfo.conf')
    routers=config.sections()
    print("The routers to take backup are "+ str(routers))
    length=len(routers)
    i=0
    threads = []
    for router in routers:
        t=Thread(target=storage,args=(i,))
        i=i+1
        threads.append(t)
       # print("reached here")
    for x in threads:
        x.start()
    for x in threads:
        x.join()
    print("Backup Complete")
else:
    print("Please make sure that the config file sshinfo.conf is present in the folder")
    quit()
