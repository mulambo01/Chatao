#!/bin/bash
PWD1=$PWD
tar -zxvf "pycrypto-2.6.1.tar.gz"
cd pycrypto-2.6.1 ; ./configure && python2 setup.py build
cd $PWD1 ; chmod +x client.py server.py ; mkdir clientKey serverKey
echo -n "Do you wanna install in your system (need to be root)? [Y/n] "
read ANS
if [ "$ANS" = "N" -o "$ANS" = "n" ]
then
cd $PWD1/pycrypto-2.6.1 ; python2 setup.py install --prefix ./
echo "The program is all installed in this folder."
else
cd $PWD1/pycrypto-2.6.1 ; python2 setup.py install
echo -e "Creating symbolic links:\n/usr/bin/chataosrv\n/usr/bin/chatao"
ln -sf $PWD1/server.py /usr/bin/chataosrv
ln -sf $PWD1/client.py /usr/bin/chatao
echo -e "Creating a systemd service file:\n/etc/systemd/system/chatao.service"
#default port
PORT="7000"
echo -e "[Unit]\nDescription=Chatao server\n[Service]\nType=simple\nExecStart=/usr/bin/python2 $PWD1/server.py $PORT\nExecReload=/bin/kill -HUP \$MAINPID\n[Install]\nWantedBy=multi-user.target" > $PWD1/chatao.service
ln -sf $PWD1/chatao.service /etc/systemd/system/chatao.service
echo "Success"
fi
