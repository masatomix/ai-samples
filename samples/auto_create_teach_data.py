#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import configparser
from nlp import IREXTeachDataCreator
from nlp import TextReader
import itertools

from logging import getLogger, StreamHandler, Formatter, DEBUG
import logging.config


logger = getLogger(__name__)

config = configparser.ConfigParser()
config.read("./config/config.ini")


def main(args):
    """
    ネットにアップされた教師データ(IOBデータ)を取得(1)し、形態素データ部の文章部分を抽出して文章を復元。
    IREXTeachDataCreator をつかって
      その文章部から形態素データを自分で作成、またその形態素データ毎にIOBデータを付与(2)
    (1)と(2)はほぼ同じになると考えられ、それらを比較。同じであれば(2)の作成に使用したGooラボのデータで
    教師データを作成できるって事になる。だからそのテスト。
    最終的にresultディレクトリに教師データを出力します。
    """
    logging.config.fileConfig('config/logging.conf')

    # c = TextReader(path='teach_data.txt', train_test_ratio=1.0)
    c = TextReader('https://raw.githubusercontent.com/Hironsan/IOB2Corpus/master/hironsan.txt', train_test_ratio=1.0)
    train_sents = c.train_sents()

    ok_total = 0
    ng_total = 0

    slice1 = slice(int(args[1]), int(args[2]))
    for train_sentence in train_sents[slice1]:
        buf = ""
        for morph in train_sentence:
            buf = buf + morph[0]
        logger.info(buf)

        h = IREXTeachDataCreator(options="-Ochasen",padding=False)

        #  自分で教師データを作る
        results = h.create_teach_data(buf)
        for result in results:
            logger.debug(result)

        ok, ng = assertEquals(train_sentence, results)
        ok_total = ok_total + ok
        ng_total = ng_total + ng
        h.save_teach_data(results, "./result")

    logger.info("---------------------------------------")
    logger.info("Total: {0}".format(ok_total + ng_total))
    logger.info("   OK: {0}".format(ok_total))
    logger.info("   NG: {0}".format(ng_total))
    logger.info(" 割合: {0:3.1f} %".format(ok_total / (ok_total + ng_total) * 100.0))

    logger.info(" 文章総数: {0} 文".format(len(train_sents)))



def assertEquals(expecteds, actuals):
    """
    形態素に区切られた文章どうしの比較を行い、正解件数と誤り件数を返す。ただし
    渡された形態素自体が異なる場合は、誤りは0件を返すことにした。
    :param expecteds:
    :param actuals:
    :return:
    """
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

            # 表層は一致なのに、他が間違ってる場合はエラーカウント。そうでない場合は、カウント対象外。
            if (m1_surface == m2_surface):
                ng = ng + 1
            else:
                pass
        else:
            ok = ok + 1
    return ok, ng


if __name__ == "__main__":
    main(sys.argv)
