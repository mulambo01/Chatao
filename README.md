# Chatao
To run the client and the server you need to have the lib pycrypto installed in your system. The script "install.sh" will install that lib and configure everything. To do that:
<br>
<b>$ bash install.sh</b>
<br>
You can choose install everything only in the current folder (without root permission) or install in the system.

# Running the server:
If you chose install the package locally, you have to run the server without daemon and using the complete path to the program, so the command line is:
<br>
<b>$ path_to_directory/server.py number_port</b>
<br>
To execute it in background and ignore the output:
<br>
<b>$ path_to_directory/server.py number_port &> /dev/null &</b>
<br>
<br>
If you chose the default instalation, you can use:
<br>
<b>$ chataosrv number_port</b>
<br>
The other option is start the service with systemd:
<br>
<b># systemctl start chatao.service</b>
<br>
The default port is 7000.

# Running the client:
If you chose the local instalation, run:
<br>
<b>$ path_to_directory/client.py address_server port_server nickname</b>
<br>
Otherwise:
<br>
<b>$ chatao address_server port_server nickname</b>
<br>

# How the chat works?
Step 1: the client sends a connection request.
<br>Step 2: the server chooses a index to identify that client and stores the address of socket in a array and make a dedicated thread to manage this connection. Then it returns this request with a message containg its public RSA key (128 bytes by default).
<br>Step 3: the client encrypts a message containg its public RSA key with the key sent by the server.
<br>Now the connection is safe.
<br>Step 4: the server stores the key in a array identified by the index.
<br>Step 5: the client sends the nickname chosen by the user.
<br>Step 6: the server stores the chosen nickname in another array by the same index.
<br>Step 7: to finish the start protocol, the server sends a message notifying all the online users that this guy has arrived.
<br>Step 8: when the user sends a message, it will be encrypted with the public key sent by server, the server will decrypt it and send to the others users with their keys.

# Using your own key:
The process for generating the key automatically in the server and in the client uses some functions of the libcrypto. I don't know how reliable this module is, so you can use your own key to encrypt your messages although it will be useless if the server doesn't do the same thing.
To do that, you will need to put the key in the directory called "clientKey" for the use of the client and "serverKey" for the use of the server.
A safe method to genete your own RSA key is using the package openssl. If you're using a GNU/Linux distribution, you can install that package and run:
<br>
<b>$ openssl genrsa -out key.pem 1024</b>
<br>
After that you need to put the file in the correct directory.
<br>
<br>
Made by <b>pixote</b>.
