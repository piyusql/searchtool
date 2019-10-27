cd /usr/src
wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz
tar xzf Python-3.7.3.tgz
cd Python-3.7.3
./configure --enable-optimizations
make altinstall
rm /usr/src/Python-3.7.3.tgz
python3.7 -V
ln -s /usr/local/bin/python3.7 /usr/bin/python3
