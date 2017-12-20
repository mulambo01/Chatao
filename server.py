#!/usr/bin/python2
from datetime import datetime
from thread import start_new_thread
import socket, sys, time, os, ast
path=os.path.realpath(__file__)
path=path.split("/")
path[-1]=""
path="/".join(path)
sys.path.append(path+'pycrypto-2.6.1/lib/python2.7/site-packages/')
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
sizekey=128
try:
 arq=open(path+"serverKey/key.pem", "r")
 serverPriv=arq.read()
 serverPriv=RSA.importKey(serverPriv)
 serverPubl=serverPriv.publickey()
 publascii=str(serverPubl.exportKey())
 arq.close()
except:
 print "If you want to use your own key, save the private key as \"key.pem\" in the directory called \"serverKey\".\nThe default size is 1024 bits."
 print "You can generate your own key using the program \"openssl\". When you have it installed in your machine, run \"openssl genrsa -out key.pem 1024\" and put the file in the correct directory."
 random_generator = Random.new().read
 serverPriv = RSA.generate(sizekey*8, random_generator)
 serverPubl = serverPriv.publickey()
 publascii=str(serverPubl.exportKey())


host=''
port=int(sys.argv[1])

connect=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig=(host, port)
connect.bind(orig)
connect.listen(1)
connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#max number of connetions
limit=200
con=["0"]*limit
client=["0"]*limit
nick=["0"]*limit
key=["0"]*limit
#the message need to be splited to be encrypted
spacer="@@@"

def decrypt(msg):
 newmsg=msg.split(spacer)
 decrypted=""
 i=0
 while(i<len(newmsg)):
  decrypted = decrypted+str(serverPriv.decrypt(ast.literal_eval(str(newmsg[i]))))
  i=i+1
 return decrypted

def encrypt(msg,index):
 encr=""
 i=0
 while(i<len(msg)/sizekey):
  block=msg[i*sizekey:i*sizekey+sizekey:]
  encr=encr+str(key[index].encrypt(block,sizekey))+spacer
  i=i+1
 block=msg[i*sizekey::]
 encr=encr+str(key[index].encrypt(block,sizekey))
 return str(encr)

#procedure to finish client connections
def down(index):
 clock=datetime.now()
 timer="["+str(clock.hour+100)[1::]+":"+str(clock.minute+100)[1::]+":"+str(clock.second+100)[1::]+"] "
 print timer+"Client "+str(index)+" fell."
#the value 1 indicates that the socket was in using but now is free, 0 means that the socket is virgin
 msg=bcolors.FAIL+timer+"User "+nick[index]+" exits."+bcolors.ENDC
 try:
  con[index].close()
 except:
  print "ERROR 1  - "+str(index)
 con[index]="1"
 client[index]="1"
 nick[index]="1"
 key[index]="1"

 j=0
 while(j<limit and con[j]!="0"):
  if(con[j]!="1" and j!=index):
   try:
    con[j].sendall(encrypt(msg,j))
   except:
    print "ERROR 5"
  j=j+1
#function that will manage the connection called by the index
#all the connections will have a dedicated thread running this function
def receive(index):
 try:
  conn=con[index]
  conn.sendall(publascii)
  keyreceiv=str(conn.recv(10000))
  keyreceiv=decrypt(keyreceiv)
  keyreceiv=keyreceiv.replace("\\n","\n")
  key[index]=RSA.importKey(str(keyreceiv))
  keyreceiv=0
  conn.sendall("1")
  nick[index]=decrypt(str(conn.recv(10000)))
  Nick=nick[index]
  print client[index],Nick,index

  clock=datetime.now()
  timer="["+str(clock.hour+100)[1::]+":"+str(clock.minute+100)[1::]+":"+str(clock.second+100)[1::]+"] "
  j=0
  while(j<limit and con[j]!="0"):
   if(con[j]!="1" and j!=index):
    message=bcolors.FAIL+timer+"User "+Nick+" came into the room."+bcolors.ENDC
    con[j].sendall(encrypt(message,j))
   j=j+1
  while(1):
   msg=str(conn.recv(10000))
   if not msg:
    down(index)
    break
   msg=decrypt(msg)
#if the message is /who, all the users in the room will be listed
   if(msg=="/who"):
    j=0
    output=bcolors.OKGREEN+"Users: "
    while(nick[j]!="0"):
     if(nick[j]!="1"):
      output=output+"\n"+nick[j]
     j=j+1
    conn.sendall(encrypt(str(output+bcolors.ENDC),index))
   else:
    clock=datetime.now()
    timer="["+str(clock.hour+100)[1::]+":"+str(clock.minute+100)[1::]+":"+str(clock.second+100)[1::]+"] "
    msg=timer+Nick+": "+msg
    print msg, index
    j=0
    while(j<limit and con[j]!="0"):
     if(con[j]!="1" and j!=index):
      con[j].sendall(encrypt(msg,j))
     j=j+1
 except:
  try:
   down(index)
   print "ERROR 2  - "+str(index)
  except:
   print "ERROR 3  - "+str(index)

def main():
 print bcolors.OKGREEN+"The server is ready!"+bcolors.ENDC
 i=0
#this variable will be used to save cpu
 cpusave=0
 while(1):
  if(con[i]=="0" or con[i]=="1"):
   time.sleep(3)
   con[i], client[i]=connect.accept()
   start_new_thread(receive,(i,))
   if(i==limit-1):
    i=0
   else:
    i=i+1
  elif(i<limit-1):
   i=i+1
  elif(cpusave==0):
   i=0
   cpusave=1
  else:
#here is where the variable act, after a complete loop in the list of connections
#if no address is free, the program will sleep for 2 seconds before repeat the cicle
   i=0
   cpusave=0
   time.sleep(2)

try:
 main()
except(KeyboardInterrupt):
 print "Closing the connection."
 i=0
 while(con[i]!="0" and i<limit):
  if(con[i]!="1"):
   try:
    con[i].shutdown(socket.SHUT_RDWR)
    con[i].close()
   except:
    print "ERROR 4  - "+str(i)
  i=i+1
 connect.shutdown(socket.SHUT_RDWR)
 connect.close()
 quit()
