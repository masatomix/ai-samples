#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import requests
import json
from MecabFacade import MecabFacade
import configparser

from logging import getLogger, StreamHandler, DEBUG, INFO

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

config = configparser.ConfigParser()
config.read("./config/config.ini")


def main(args):
    # サンプルの文章
    sentence = "欧州連合（ＥＵ）の欧州委員会は18日、欧州委による独禁法違反。"

    logger.info("sentence: [{0}]".format(sentence))

    # 文章を、形態素解析する
    morphs = create_morphs(sentence)
    logger.info("形態素解析結果:")
    for morph in morphs:
        logger.info(morph)

    payload_obj = {
        "app_id": config["payload"]["app_id"],
        "sentence": sentence
    }

    # 文章を、GooラボのAPIで固有表現抽出する
    entities = create_entities(payload_obj)
    logger.info("\n固有表現抽出結果:")
    for entity in entities:
        logger.info(entity)

    logger.info("")

    buf = ""
    morph_index = 0
    entity_index = 0

    # 形態素単位で、Gooラボからとってきた固有表現と突合し、IOBラベルをつけていく。
    while len(morphs) > morph_index:

        buf = buf + morphs[morph_index][0]
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
            # それ以外の部分一致は、I_
            else:
                morphs[morph_index].append("I_" + entities[entity_index][1])
            morph_index = morph_index + 1
            logger.debug(messageBuf + "部分一致した。bufにappend。完全一致するまでつづける。つぎのmorphへ。")
            continue

        # 部分一致しない場合は、entity_index番号を進める
        else:
            buf = ""
            # ただし、次がない場合は、morph側を進める
            if len(entities) == entity_index + 1:
                morphs[morph_index].append("O")
                entity_index = 0
                morph_index = morph_index + 1
                logger.debug(messageBuf + "部分一致しない。つぎのentityもないので、bufをリセット。つぎのmorphへ。")
                logger.debug('----')
            else:
                logger.debug(messageBuf + "部分一致しない。bufをリセットし、次のentity_indexへ")
                entity_index = entity_index + 1

    logger.info("\nIOBタグ付けした結果データ:")
    for morph in morphs:
        logger.info(morph)


def create_morphs(sentence):
    m = MecabFacade("-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd")
    # m = MecabFacade()
    return m.parse(sentence).results()


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
