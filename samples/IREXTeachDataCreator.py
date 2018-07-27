#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
from MecabFacade import MecabFacade
import configparser

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO

logger = getLogger(__name__)
handler = StreamHandler()
handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(handler_format)

handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False


class IREXTeachDataCreator(object):

    def __init__(self, options='-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd'):
        self.__mecab_facade = MecabFacade(options)
        self.__config = configparser.ConfigParser()
        self.__config.read("./config/config.ini")

    def create_morphs(self, sentence):
        return self.__mecab_facade.parse(sentence).results()

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

    def create_teach_data(self, sentence):
        morphs = self.create_morphs(sentence)
        entities = self.create_entities(sentence)

        buf = ""
        morph_index = 0
        entity_index = 0

        match_index = 0

        # 形態素単位で、Gooラボからとってきた固有表現と突合し、IOBラベルをつけていく。
        while len(morphs) > morph_index:

            buf = buf + morphs[morph_index][0]
            # 固有表現が、0件だった場合の考慮。
            target = ""
            if len(entities) > 0:
                target = entities[entity_index][0]

            messageBuf = "[{0}] 対 [{1}]:".format(buf, target)

            # 完全一致した場合は、次の morphにすすめる
            if target == buf:
                # 単純に、完全一致した場合は、B/Iをつけず。
                if buf == morphs[morph_index][0]:
                    morphs[morph_index].append(entities[entity_index][1])
                # 完全一致だけど、前回から積み上げで完全一致した場合は、I_となる
                else:
                    morphs[morph_index].append("I_" + entities[entity_index][1])
                # add
                buf = ""
                entity_index = 0
                morph_index = morph_index + 1

                logger.debug(messageBuf + "完全一致した。bufをリセット。つぎのmorphへ。")
                logger.debug('----')
                continue

            # 前方一致する場合は、bufに追記して、チェック
            elif target.startswith(buf):  # morph文字が、entity文字に部分一致したら、
                # 部分一致した場合は、初めだけB_
                if buf == morphs[morph_index][0]:
                    morphs[morph_index].append("B_" + entities[entity_index][1])
                    match_index = morph_index  # ココから部分一致が始まる
                # それ以外の部分一致は、I_
                else:
                    morphs[morph_index].append("I_" + entities[entity_index][1])
                morph_index = morph_index + 1
                logger.debug(messageBuf + "部分一致した。bufにappend。完全一致するまでつづける。つぎのmorphへ。")
                continue

            # 部分一致しない場合は、entity_index番号を進める
            else:
                # ただしentity側が、次がない場合は、morph側を進める
                if len(entities) == entity_index + 1 or len(entities) == 0:
                    morphs[morph_index].append("O")
                    entity_index = 0
                    morph_index = morph_index + 1
                    buf = ""
                    logger.debug(messageBuf + "部分一致しない。つぎのentityもないので、bufをリセット。つぎのmorphへ。")
                    logger.debug('----')
                elif buf == morphs[morph_index][0]:
                    logger.debug(messageBuf + "部分一致しない。bufをリセットし、次のentity_indexへ")
                    entity_index = entity_index + 1
                    buf = ""

                    # 下記の場合は、bufに追加中に部分一致しなくなったと言うこと
                else:
                    logger.debug(messageBuf + "さっきまで部分一致してたのに、しなくなった。bufをリセットし、"
                                              "次のentity_indexへいくが、部分一致したところまで戻ってやりなおす。")

                    # 間違って追加したIOBタグの除去。範囲は、部分一致が始まったところから、今の番号まで。
                    for count in range(match_index, morph_index):
                        morphs[count].pop(-1)

                    entity_index = entity_index + 1
                    buf = ""
                    morph_index = match_index

        return morphs

    def saveIOB(self,path):
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
