#!/bin/bash

sudo apt-get update
sudo apt install -y build-essential

# https://pip.pypa.io/en/latest/installing/
curl https://bootstrap.pypa.io/get-pip.py -O
sudo python get-pip.py
sudo apt install -y python-pip
sudo apt install -y python3-pip

# install mecab
#sudo apt install -y mecab libmecab-dev mecab-ipadic-utf8

# install mecab-ipadic-neologd  -n(更新する) -y(聞かない)
#git clone https://github.com/neologd/mecab-ipadic-neologd.git
#cd mecab-ipadic-neologd/
#sudo ./bin/install-mecab-ipadic-neologd -n -y
