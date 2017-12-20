#!/usr/bin/python2
import readline #this module improves the function raw_input()
from multiprocessing import Process
import signal
import time, socket, sys, commandlist, ast, os
path=os.path.realpath(__file__)
path=path.split("/")
path[-1]=""
path="/".join(path)
sys.path.append(path+'pycrypto-2.6.1/lib/python2.7/site-packages/')
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
from md5 import md5

PID=os.getpid()
listening=["0"]*1

class bcolors:
 HEADER = '\033[95m'
 OKBLUE = '\033[94m'
 OKGREEN = '\033[92m'
 WARNING = '\033[93m'
 FAIL = '\033[91m'
 ENDC = '\033[0m'
 BOLD = '\033[1m'
 UNDERLINE = '\033[4m'

if(len(sys.argv)<4):
 print "Use:", sys.argv[0],"SERVER PORT NICKNAME"
 quit()
sizekey=128

try:
 arq=open(path+"clientKey/key.pem", "r")
 key=arq.read()
 key=RSA.importKey(key)
 publickey=key.publickey()
 publicascii=str(publickey.exportKey())
 arq.close()
except:
 print "If you want to use your own key, save the private key as \"key.pem\" in the directory called \"clientKey\".\nThe default size is 1024 bits."
 print "You can generate your own key using the program \"openssl\". When you have it installed in your machine, run \"openssl genrsa -out key.pem 1024\" and put the file in the correct directory."
 random_generator = Random.new().read
 key = RSA.generate(sizekey*8, random_generator)
 publickey = key.publickey()
 publicascii=str(publickey.exportKey())
#the key has a limit of 128 bytes, so to solve that problem, the big messages need
#to be splited, encrypted singly and reconnected with this spacer in the middle
spacer="@@@"

def decrypt(msg):
 newmsg=msg.split(spacer)
 decrypted=""
 i=0
 while(i<len(newmsg)):
  decrypted = decrypted+str(key.decrypt(ast.literal_eval(str(newmsg[i]))))
  i=i+1
 return decrypted

host=sys.argv[1]
port=int(sys.argv[2])
tcp=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((host, port))

band=5
def senddata(data):
 i=0
 while(i<int(len(data)/band)):
  tcp.send(data[i*band:(i+1)*band:])
  tcp.recv(1)
  i=i+1
 if(len(data)%band!=0):
  tcp.send(data[i*band::])
  tcp.recv(1)
 tcp.send("end")
 tcp.recv(1)

serverKey=str(tcp.recv(5000))
serverKey=serverKey.replace("\\n","\n")
serverKey=RSA.importKey(str(serverKey))

def encrypt(msg):
 encr=""
 i=0
 while(i<len(msg)/sizekey and len(msg)>sizekey):
  block=msg[i*sizekey:i*sizekey+sizekey:]
  encr=encr+str(serverKey.encrypt(block,sizekey))+spacer
  i=i+1
 block=msg[i*sizekey::]
 encr=encr+str(serverKey.encrypt(block,sizekey))
 return str(encr)

nick=sys.argv[3]

senddata(encrypt(publicascii))
senddata(encrypt(nick))
print bcolors.OKGREEN+"You are connected!"+bcolors.ENDC
def receive(tcp):
 while(1):
  msg=tcp.recv(10000)
  if not msg:
   print bcolors.FAIL+"The connection was closed."+bcolors.ENDC
   os.kill(PID, signal.SIGUSR1)
   break
  try:
   print bcolors.OKBLUE+decrypt(msg)+bcolors.ENDC
  except Exception as error:
   print "Error! "+str(error)

def main():
#thread to receive messages
 
 listening[0]=Process(target=receive, args=(tcp,))
 print sys.getsizeof(listening[0])
 listening[0].start()
 while(1):
  msg=raw_input()
  if msg in commandlist.list:
   c, m = commandlist.sendcommand(msg)
   if c == 1:
    tcp.send(m)
  elif msg[-4:len(msg)]=="/del":
   print bcolors.FAIL+bcolors.BOLD+"INPUT BUFFER IS CLEAN"+bcolors.ENDC+bcolors.ENDC
  elif not(msg in commandlist.avoid):
   try:
    tcp.send(encrypt(msg))
   except Exception as error:
    print "Error! "+str(error)
try:
 main()
except(KeyboardInterrupt):
 print bcolors.FAIL+"Disconnected"+bcolors.ENDC
 tcp.close()
 listening[0].terminate()
 quit()
