#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
from nlp import MecabFacade
import configparser
import hashlib
import os
from logging import getLogger

logger = getLogger(__name__)


class IREXTeachDataCreator(object):
    """
    文章を受け取り、その文章をMecabをつかって形態素解析したり(create_morphs)、
    文章を受け取り、その文章をGooラボをつかって固有表現抽出したり(create_entities)する

    また、文章を受け取り、Gooラボに固有表現抽出させ、同じ文章をMecabで形態素解析して、Gooラボの結果を
    IOBタグとして付与する関数(create_teach_data) を提供する。

    またまた、渡された結果データを、指定したディレクトリにテキスト出力する機能(save_teach_data)もつけた。
    """

    def __init__(self, options='-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd', padding=True):
        self.__mecab_facade = MecabFacade(options, padding)
        self.__config = configparser.ConfigParser()
        self.__config.read("config/config.ini")

    def create_morphs(self, sentence):
        """
        Mecab をつかって、文章を形態素解析して、返す。
        :param sentence: 文章
        :return: 形態素解析結果の配列
        """
        return self.__mecab_facade.parse(sentence).results()

    def create_entities(self, sentence):
        """
        Gooラボの APIを呼び出して、文章から固有表現を抽出してもらう。
        :param sentence:  文章
        :return:
        """
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

    def create_teach_data(self, sentence, entities=None):
        """
        文章を形態素解析した結果と、Gooラボが返してきた固有表現抽出結果をもとに、教師データを作成する
        :param sentence:
        :param entities:
        :return:
        """
        morphs = self.create_morphs(sentence)
        if entities is None:
            entities = self.create_entities(sentence)

        logger.debug(entities)

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
                # 単純に、完全一致した場合は、Bをつける。
                if buf == morphs[morph_index][0]:
                    morphs[morph_index].append("B-" + entities[entity_index][1])
                # 完全一致だけど、前回から積み上げで完全一致した場合は、I_となる
                else:
                    morphs[morph_index].append("I-" + entities[entity_index][1])
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
                    morphs[morph_index].append("B-" + entities[entity_index][1])
                    match_index = morph_index  # ココから部分一致が始まる
                # それ以外の部分一致は、I_
                else:
                    morphs[morph_index].append("I-" + entities[entity_index][1])
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

    def save_teach_data(self, morphs, dir):

        os.makedirs(dir, exist_ok=True)
        path = os.path.join(dir, hashlib.md5(repr(morphs).encode('utf-8')).hexdigest() + ".txt")
        morphsStr = ['\t'.join(s) for s in morphs]

        with open(path, mode='w') as f:
            f.write('\n'.join(morphsStr))

    def concat_teach_data(self, dir):
        import glob
        path_pattern = os.path.join(dir, "*.txt")
        paths = glob.glob(path_pattern)

        datas = []
        for path in paths:
            with open(path) as f:
                s = f.read()
                datas.append(s)
                datas.append('\n')
                datas.append('\n')

        save_path = os.path.join(dir, "input001.txt")
        with open(save_path, mode='w') as f:
            f.write(''.join(datas))

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
