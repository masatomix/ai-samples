#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import requests
import json
from MecabFacade import MecabFacade
import configparser
import codecs

from logging import getLogger, StreamHandler, DEBUG, INFO


class IREXTeachDataCreator(object):

    def __init__(self, options='-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd'):
        self.__m = MecabFacade(options)
        self.__config = configparser.ConfigParser()
        self.__config.read("./config/config.ini")

        self.__logger = getLogger(__name__)
        self.__handler = StreamHandler()
        self.__handler.setLevel(DEBUG)
        self.__logger.setLevel(DEBUG)
        self.__logger.addHandler(self.__handler)
        self.__logger.propagate = False

    def create_morphs(self, sentence):
        return self.__m.parse(sentence).results()

    def create_entities(self, sentence):
        payload_obj = {
            "app_id": self.__config["payload"]["app_id"],
            "sentence": sentence
        }

        payload = json.dumps(payload_obj, ensure_ascii=False)

        headers = {
            "Accept": "application/json",
            "Content-type": "application/json"
        }

        proxies, verify = self.get_proxy()
        r = requests.post(
            'https://labs.goo.ne.jp/api/entity',
            data=payload.encode('utf-8').decode('latin-1'),
            headers=headers,
            proxies=proxies,
            verify=verify)
        return r.json()["ne_list"]

    def create_teach_data(self,sentence):
        pass





    def get_proxy(self):
        verify = True
        proxies = None

        if self.__config["proxy"].getboolean("proxy"):
            proxies = {
                "http": self.__config["proxy"]["http"],
                "https": self.__config["proxy"]["https"]
            }
            verify = False

        return proxies, verify
