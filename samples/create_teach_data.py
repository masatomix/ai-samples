#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import requests
import json
from MecabFacade import MecabFacade
import configparser
import codecs
from IREXTeachDataCreator import IREXTeachDataCreator
import itertools

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO

logger = getLogger(__name__)
handler = StreamHandler()
handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(handler_format)

handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

config = configparser.ConfigParser()
config.read("./config/config.ini")


def main(args):
    sent = []
    sents = []
    strings = get_training_texts()
    for line in strings:
        if line == '':
            sents.append(sent)
            sent = []
            continue
        morph_info = line.strip().split('\t')
        sent.append(morph_info)

    train_num = int(len(sents))
    train_sents = sents[:train_num]  # 一文、一文が配列になってる

    # with codecs.open('teach_data.txt', encoding='utf-8') as f:
    #     sent = []
    #     sents = []
    #     for line in f:
    #         if line == '\n':
    #             sents.append(sent)
    #             sent = []
    #             continue
    #         morph_info = line.strip().split('\t')
    #         sent.append(morph_info)
    #
    # train_num = int(len(sents))
    # train_sents = sents[:train_num]  # 一文、一文が配列になってる

    ok_total = 0
    ng_total = 0

    slice1 = slice(int(args[1]), int(args[2]))
    for train_sentence in train_sents[slice1]:
        buf = ""
        for morph in train_sentence:
            buf = buf + morph[0]
        logger.info(buf)

        h = IREXTeachDataCreator("-Ochasen")

        results = h.create_teach_data(buf)
        for result in results:
            logger.debug(result)

        ok, ng = assertEquals(train_sentence, results)
        ok_total = ok_total + ok
        ng_total = ng_total + ng
        h.save_teach_data(results, "./result")

    logger.info("Total: {0}".format(ok_total + ng_total))
    logger.info("   OK: {0}".format(ok_total))
    logger.info("   NG: {0}".format(ng_total))
    logger.info(" 割合: {0:3.1f} %".format(ok_total / (ok_total + ng_total) * 100.0))


def get_training_texts():
    text = requests.get('https://raw.githubusercontent.com/Hironsan/IOB2Corpus/master/hironsan.txt').text
    return text.split("\n")


'''
形態素に区切られた文章どうしの比較を行い、正解件数と誤り件数を返す。ただし
渡された形態素自体が異なる場合は、誤りは0件を返すことにした。
'''
def assertEquals(expecteds, actuals):
    ok = 0
    ng = 0
    for expected, actual in itertools.zip_longest(expecteds, actuals):

        m1_surface = ""
        m2_surface = ""

        if expected != actual:
            logger.info("-- 差分 --")
            if expected is not None:
                logger.info(" 期待値: " + '\t'.join(expected))
                m1_surface = expected[0]
            else:
                logger.info(" 期待値: NULL")
            if actual is not None:
                logger.info(" 実際　:" + '\t'.join(actual))
                m2_surface = actual[0]
            else:
                logger.info(" 実際　: NULL")

            if (m1_surface == m2_surface):
                ng = ng + 1
            else:
                pass
        else:
            ok = ok + 1
    return ok, ng


if __name__ == "__main__":
    main(sys.argv)
