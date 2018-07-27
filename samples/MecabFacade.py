#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MeCab


class MecabFacade(object):

    def __init__(self, options='-Ochasen'):
        self.__options = options
        self.__results = []

    def parse(self, text):
        # m = MeCab.Tagger("-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd")
        m = MeCab.Tagger(self.__options)

        m.parse('')  # なんだかおまじないらしい。
        node = m.parseToNode(text)
        node = node.next

        results = []
        while node:
            word = []
            word.append(node.surface)
            word.extend(node.feature.split(","))
            results.append(word)
            # print (node.feature)
            node = node.next

        results.pop()  # 最後はいらないので除去
        self.__results = results
        return self

    def results(self):
        return self.__results
