#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import configparser

config = configparser.ConfigParser()
config.read("./config/config.ini")


def main(args):
    sentence = "鈴木さんがきょうの9時30分に横浜に行きます。"

    print("sentence: [{0}]".format(sentence))


    payload_obj = {
        "app_id": config["payload"]["app_id"],
        "sentence": sentence
    }

    entities = create_entities(payload_obj)
    print("固有表現抽出結果:")
    for entity in entities:
        print(entity)

    morphs = create_morphs(payload_obj)
    print("形態素解析結果:")
    for sentence in morphs:
        for morph in sentence:
            print(morph)


def create_morphs(payloadObj):
    payload = json.dumps(payloadObj, ensure_ascii=False)

    headers = {
        "Accept": "application/json",
        "Content-type": "application/json"
    }

    proxies, verify = get_proxy()
    r = requests.post(
        'https://labs.goo.ne.jp/api/morph',
        data=payload.encode('utf-8').decode('latin-1'),
        headers=headers,
        proxies=proxies,
        verify=verify)
    return r.json()["word_list"]



def create_entities(payloadObj):
    payload = json.dumps(payloadObj, ensure_ascii=False)

    headers = {
        "Accept": "application/json",
        "Content-type": "application/json"
    }

    proxies, verify = get_proxy()
    r = requests.post(
        'https://labs.goo.ne.jp/api/entity',
        data=payload.encode('utf-8').decode('latin-1'),
        headers=headers,
        proxies=proxies,
        verify=verify)
    return r.json()["ne_list"]


def get_proxy():
    verify = True
    proxies = None

    if config["proxy"].getboolean("proxy"):
        proxies = {
            "http": config["proxy"]["http"],
            "https": config["proxy"]["https"]
        }
        verify = False

    return proxies, verify

if __name__ == "__main__":
    main(sys.argv)
