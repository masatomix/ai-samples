#!/usr/bin/env python
# -*- coding: utf-8 -*-


import MeCab
from logging import getLogger

log = getLogger(__name__)


class MecabFacade(object):
    """
    MecabのFacade。実行結果を表形式で返すメソッドを提供
    https://www.masatom.in/pukiwiki/%BC%AB%C1%B3%B8%C0%B8%EC%BD%E8%CD%FD/%B7%C1%C2%D6%C1%C7%B2%F2%C0%CF%A5%A8%A5%F3%A5%B8%A5%F3Mecab/Python%A4%AB%A4%E9%B8%C6%A4%D3%BD%D0%A4%B9/
    """

    def __init__(self, options='-Ochasen', padding=True):
        """
        :param options: Chasenのオプションを設定
        :param padding: 空文字で埋めるかどうか
        """
        self.__options = options
        self.__results = []
        self.__padding = padding

    def parse(self, text):
        """
        処理したい文章を受け取って、Mecabでパースする
        :param text: 対象文字列
        :return: this
        """

        # m = MeCab.Tagger("-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd")
        m = MeCab.Tagger(self.__options)

        m.parse('')  # なんだかおまじないらしい。
        node = m.parseToNode(text)
        node = node.next

        results = []
        while node:
            word = []
            word.append(node.surface)
            featuresTmp = node.feature.split(",")
            if self.__padding:
                features = self.padding(featuresTmp, 9, '')  # 9列に満たない場合は、''で埋める
            else:
                features = featuresTmp
            word.extend(features)
            results.append(word)
            log.debug(f'{node.surface}, {node.feature}')
            node = node.next

        results.pop()  # 最後はいらないので除去
        self.__results = results
        return self

    def results(self):
        return self.__results

    def padding(self, inputArray, length, padding):
        """
        引数の長さより小さい配列について、配列の後ろにpaddingの文字をAppendする
        長さが、引数の配列の報が大きい場合、lengthの長さに短くされた配列を返す。
        :param inputArray: 長さが足りない配列
        :param length: 求める長さ
        :param padding: 求める長さまで、後ろをPaddingする時の文字列
        :return: Paddingされた配列。
        """
        results = []
        count = 0
        while count < length:
            if count < len(inputArray):
                results.append(inputArray[count])
            else:
                results.append(padding)
            count = count + 1
        return results
