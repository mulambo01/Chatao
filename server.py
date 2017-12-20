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
from md5 import md5

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

def getclock():
 time=datetime.now()
 clock="["+str(time.hour+100)[1::]+":"+str(time.minute+100)[1::]+":"+str(time.second+100)[1::]+"] "
 return clock
#procedure to finish client connections
def down(index):
 clock=getclock()
 print clock+"Client "+str(index)+" fell."
#the value 1 indicates that the socket was in using but now is free, 0 means that the socket is virgin
 msg=bcolors.FAIL+clock+"User "+nick[index]+" exits."+bcolors.ENDC
 try:
  con[index].close()
 except Exception as error:
  print "Error! "+str(error)
 con[index]="1"
 client[index]="1"
 nick[index]="1"
 key[index]="1"
 j=0
 while(j<limit and con[j]!="0"):
  if(con[j]!="1" and j!=index):
   try:
    con[j].sendall(encrypt(msg,j))
   except Exception as error:
    print "Error! "+str(error)
  j=j+1

def joindata(index):
 band=250
 try:
  data=""
  rec=con[index].recv(band)
  con[index].sendall("1")
  while(rec!="end"):
   data=data+rec
   rec=con[index].recv(band)
   con[index].sendall("1")
  return data
 except Exception as error:
  return "Error! "+str(error)

def is_number(var):
  try:
    float(var)
    return True
  except:
    return False

#function that will manage the connection called by the index
#all the connections will have a dedicated thread running this function
def receive(index):
 try:
  conn=con[index]
  conn.sendall(publascii)
  keyreceiv=joindata(index)
  keyreceiv=decrypt(keyreceiv)
  keyreceiv=keyreceiv.replace("\\n","\n")
  key[index]=RSA.importKey(str(keyreceiv))
  keyreceiv=0
  nick[index]=decrypt(joindata(index))
  Nick=nick[index]
  if(is_number(str(Nick))):
   conn.sendall(encrypt(bcolors.FAIL+"Your nick can\'t be a number!\n\n\n"+bcolors.ENDC, index))
   down(index)
  print client[index],Nick,index
  j=0
  while(j<limit and con[j]!="0"):
   clock=getclock()
   if(con[j]!="1" and j!=index):
    message=bcolors.FAIL+clock+"User "+Nick+" came into the room."+bcolors.ENDC
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
    clock=getclock()
    msg=clock+Nick+": "+msg
    print msg, index
    j=0
    while(j<limit and con[j]!="0"):
     if(con[j]!="1" and j!=index):
      con[j].sendall(encrypt(msg,j))
     j=j+1
 except Exception as error:
  try:
   down(index)
   print "Error! "+str(error)
  except Exception as error:
   print "Error! "+str(error)

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
   except Exception as error:
    print "Error! "+str(error)
  i=i+1
 connect.shutdown(socket.SHUT_RDWR)
 connect.close()
 quit()
