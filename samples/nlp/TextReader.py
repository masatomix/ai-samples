#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import requests


class TextReader(object):
    """
    形態素解析データとIOBタグをつけた、ファイルやURLから、データを作成する
    """

    def __init__(self, url=None, path=None, train_test_ratio=0.9):
        """
        結局のところ、データ(下にサンプルをつけた)を行単位で読んでいき、
        タブ区切りのデータを取得して、それらをタブでsplit つまり
          morph_info = line.strip().split('\t')
          sent.append(morph_info)
        する。

        さらに、改行のみの行を文章の区切りとして、
        if line == '\n':
            sents.append(sent)
        って、sents[i] に文章ごとに格納する。

        :param url:
        :param path:
        :param train_test_ratio:
        """

        sent = []
        sents = []

        if path:
            """
            ファイルから
            """
            # 下記コードは、ローカルのテキストファイルから読み込む例。
            with codecs.open(path, encoding='utf-8') as f:
                for line in f:
                    if line == '\n':
                        sents.append(sent)
                        sent = []
                        continue
                    morph_info = line.strip().split('\t')
                    sent.append(morph_info)
        else:
            """
            URLから
            """
            text = requests.get(url).text
            strings = text.split("\n")
            for line in strings:
                if line == '':
                    sents.append(sent)
                    sent = []
                    continue
                morph_info = line.strip().split('\t')
                sent.append(morph_info)
        '''
        sents[0] の sents[0][0]が、
        ['さて', '接続詞', '*', '*', '*', '*', '*', 'さて', 'サテ', 'サテ'] ってデータ。
        '''

        train_num = int(len(sents) * train_test_ratio)
        self.__train_sents = sents[:train_num]  # 一文、一文が配列になってる
        self.__test_sents = sents[train_num:]  # 一文、一文が配列になってる

    def train_sents(self):
        return self.__train_sents

    def test_sents(self):
        return self.__test_sents

    def iob_sents(self, name):
        if name == 'train':
            return self.__train_sents
        elif name == 'test':
            return self.__test_sents
        else:
            return None


'''
さて	接続詞	*	*	*	*	*	さて	サテ	サテ	O
今回	名詞	副詞可能	*	*	*	*	今回	コンカイ	コンカイ	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
ワークショップ	名詞	一般	*	*	*	*	ワークショップ	ワークショップ	ワークショップ	O
は	助詞	係助詞	*	*	*	*	は	ハ	ワ	O
Event	名詞	固有名詞	組織	*	*	*	*	O
Monitoring	名詞	一般	*	*	*	*	*	O
や	助詞	並立助詞	*	*	*	*	や	ヤ	ヤ	O
AI	名詞	一般	*	*	*	*	*	O
連携	名詞	サ変接続	*	*	*	*	連携	レンケイ	レンケイ	O
など	助詞	副助詞	*	*	*	*	など	ナド	ナド	O
が	助詞	格助詞	一般	*	*	*	が	ガ	ガ	O
あり	動詞	自立	*	*	五段・ラ行	連用形	ある	アリ	アリ	O
まし	助動詞	*	*	*	特殊・マス	連用形	ます	マシ	マシ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
が	助詞	接続助詞	*	*	*	*	が	ガ	ガ	O
、	記号	読点	*	*	*	*	、	、	、	O
自分	名詞	一般	*	*	*	*	自分	ジブン	ジブン	O
的	名詞	接尾	形容動詞語幹	*	*	*	的	テキ	テキ	O
に	助詞	副詞化	*	*	*	*	に	ニ	ニ	O
目玉	名詞	一般	*	*	*	*	目玉	メダマ	メダマ	O
だっ	助動詞	*	*	*	特殊・ダ	連用タ接続	だ	ダッ	ダッ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
の	名詞	非自立	一般	*	*	*	の	ノ	ノ	O
は	助詞	係助詞	*	*	*	*	は	ハ	ワ	O
「	記号	括弧開	*	*	*	*	「	「	「	O
Debugging	名詞	固有名詞	組織	*	*	*	*	O
Custom	名詞	一般	*	*	*	*	*	O
Activities	名詞	一般	*	*	*	*	*	O
」	記号	括弧閉	*	*	*	*	」	」	」	O
つまり	名詞	一般	*	*	*	*	つまり	ツマリ	ツマリ	O
「	記号	括弧開	*	*	*	*	「	「	「	O
カスタムアクティビティ	名詞	一般	*	*	*	*	*	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
、	記号	読点	*	*	*	*	、	、	、	O
デバッガ	名詞	一般	*	*	*	*	デバッガ	デバッガ	デバッガ	O
による	助詞	格助詞	連語	*	*	*	による	ニヨル	ニヨル	O
デバッグ	名詞	サ変接続	*	*	*	*	デバッグ	デバッグ	デバッグ	O
方法	名詞	一般	*	*	*	*	方法	ホウホウ	ホーホー	O
について	助詞	格助詞	連語	*	*	*	について	ニツイテ	ニツイテ	O
」	記号	括弧閉	*	*	*	*	」	」	」	O
です	助動詞	*	*	*	特殊・デス	基本形	です	デス	デス	O
。	記号	句点	*	*	*	*	。	。	。	O
ちょっと	副詞	助詞類接続	*	*	*	*	ちょっと	チョット	チョット	O
まえ	動詞	自立	*	*	一段	連用形	まえる	マエ	マエ	O
UiPath	名詞	一般	*	*	*	*	*	B-T010
における	助詞	格助詞	連語	*	*	*	における	ニオケル	ニオケル	O
カスタムアクティビティ	名詞	一般	*	*	*	*	*	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
開発	名詞	サ変接続	*	*	*	*	開発	カイハツ	カイハツ	O
方法	名詞	一般	*	*	*	*	方法	ホウホウ	ホーホー	O
を	助詞	格助詞	一般	*	*	*	を	ヲ	ヲ	O
結構	副詞	一般	*	*	*	*	結構	ケッコウ	ケッコー	O
調べ	動詞	自立	*	*	一段	連用形	調べる	シラベ	シラベ	O
て	助詞	接続助詞	*	*	*	*	て	テ	テ	O
い	動詞	非自立	*	*	一段	連用形	いる	イ	イ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
の	名詞	非自立	一般	*	*	*	の	ノ	ノ	O
です	助動詞	*	*	*	特殊・デス	基本形	です	デス	デス	O
が	助詞	接続助詞	*	*	*	*	が	ガ	ガ	O
、	記号	読点	*	*	*	*	、	、	、	O
情報	名詞	一般	*	*	*	*	情報	ジョウホウ	ジョーホー	O
が	助詞	格助詞	一般	*	*	*	が	ガ	ガ	O
なく	形容詞	自立	*	*	形容詞・アウオ段	連用テ接続	ない	ナク	ナク	O
て	助詞	接続助詞	*	*	*	*	て	テ	テ	O
困っ	動詞	自立	*	*	五段・ラ行	連用タ接続	困る	コマッ	コマッ	O
て	助詞	接続助詞	*	*	*	*	て	テ	テ	O
い	動詞	非自立	*	*	一段	連用形	いる	イ	イ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
の	名詞	非自立	一般	*	*	*	の	ノ	ノ	O
が	助詞	格助詞	一般	*	*	*	が	ガ	ガ	O
開発	名詞	サ変接続	*	*	*	*	開発	カイハツ	カイハツ	O
し	動詞	自立	*	*	サ変・スル	連用形	する	シ	シ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
アクティビティ	名詞	一般	*	*	*	*	*	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
デバッグ	名詞	サ変接続	*	*	*	*	デバッグ	デバッグ	デバッグ	O
です	助動詞	*	*	*	特殊・デス	基本形	です	デス	デス	O
。	記号	句点	*	*	*	*	。	。	。	O
開発	名詞	サ変接続	*	*	*	*	開発	カイハツ	カイハツ	O
し	動詞	自立	*	*	サ変・スル	連用形	する	シ	シ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
アクティビティ	名詞	一般	*	*	*	*	*	O
は	助詞	係助詞	*	*	*	*	は	ハ	ワ	O
nupkg	名詞	一般	*	*	*	*	*	O
に	助詞	格助詞	一般	*	*	*	に	ニ	ニ	O
なっ	動詞	自立	*	*	五段・ラ行	連用タ接続	なる	ナッ	ナッ	O
て	助詞	接続助詞	*	*	*	*	て	テ	テ	O
UiPath	名詞	一般	*	*	*	*	*	B-T010
Studio	名詞	一般	*	*	*	*	*	B-T010
や	助詞	並立助詞	*	*	*	*	や	ヤ	ヤ	O
Robot	名詞	一般	*	*	*	*	*	B-T010
から	助詞	格助詞	一般	*	*	*	から	カラ	カラ	O
実行	名詞	サ変接続	*	*	*	*	実行	ジッコウ	ジッコー	O
さ	動詞	自立	*	*	サ変・スル	未然レル接続	する	サ	サ	O
れる	動詞	接尾	*	*	一段	基本形	れる	レル	レル	O
わけ	名詞	非自立	一般	*	*	*	わけ	ワケ	ワケ	O
で	助動詞	*	*	*	特殊・ダ	連用形	だ	デ	デ	O
、	記号	読点	*	*	*	*	、	、	、	O
Visual	名詞	固有名詞	組織	*	*	*	*	B-T010
Studio	名詞	一般	*	*	*	*	*	B-T010
から	助詞	格助詞	一般	*	*	*	から	カラ	カラ	O
デバッグ	名詞	サ変接続	*	*	*	*	デバッグ	デバッグ	デバッグ	O
起動	名詞	サ変接続	*	*	*	*	起動	キドウ	キドー	O
って	助詞	格助詞	連語	*	*	*	って	ッテ	ッテ	O
出来	動詞	自立	*	*	一段	未然形	出来る	デキ	デキ	O
ない	助動詞	*	*	*	特殊・ナイ	基本形	ない	ナイ	ナイ	O
なー	助詞	終助詞	*	*	*	*	なー	ナー	ナー	O
って	助詞	格助詞	連語	*	*	*	って	ッテ	ッテ	O
おもっ	動詞	自立	*	*	五段・ワ行促音便	連用タ接続	おもう	オモッ	オモッ	O
て	助詞	接続助詞	*	*	*	*	て	テ	テ	O
まし	助動詞	*	*	*	特殊・マス	連用形	ます	マシ	マシ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
。	記号	句点	*	*	*	*	。	。	。	O

今回	名詞	副詞可能	*	*	*	*	今回	コンカイ	コンカイ	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
説明	名詞	サ変接続	*	*	*	*	説明	セツメイ	セツメイ	O
で	助詞	格助詞	一般	*	*	*	で	デ	デ	O
Visual	名詞	一般	*	*	*	*	*	B-T010
Studio	名詞	一般	*	*	*	*	*	B-T010
デバッガー	名詞	一般	*	*	*	*	*	O
で	助詞	格助詞	一般	*	*	*	で	デ	デ	O
実行	名詞	サ変接続	*	*	*	*	実行	ジッコウ	ジッコー	O
中	名詞	接尾	副詞可能	*	*	*	中	チュウ	チュー	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
プロセス	名詞	一般	*	*	*	*	プロセス	プロセス	プロセス	O
へ	助詞	格助詞	一般	*	*	*	へ	ヘ	エ	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
アタッチ	名詞	固有名詞	組織	*	*	*	*	O
という	助詞	格助詞	連語	*	*	*	という	トイウ	トユウ	O
やり	動詞	自立	*	*	五段・ラ行	連用形	やる	ヤリ	ヤリ	O
かた	名詞	接尾	一般	*	*	*	かた	カタ	カタ	O
を	助詞	格助詞	一般	*	*	*	を	ヲ	ヲ	O
教え	動詞	自立	*	*	一段	連用形	教える	オシエ	オシエ	O
て	助詞	接続助詞	*	*	*	*	て	テ	テ	O
もらい	動詞	非自立	*	*	五段・ワ行促音便	連用形	もらう	モライ	モライ	O
まし	助動詞	*	*	*	特殊・マス	連用形	ます	マシ	マシ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
。	記号	句点	*	*	*	*	。	。	。	O
起動	名詞	サ変接続	*	*	*	*	起動	キドウ	キドー	O
し	動詞	自立	*	*	サ変・スル	連用形	する	シ	シ	O
て	助詞	接続助詞	*	*	*	*	て	テ	テ	O
いる	動詞	非自立	*	*	一段	基本形	いる	イル	イル	O
プロセス	名詞	一般	*	*	*	*	プロセス	プロセス	プロセス	O
に対して	助詞	格助詞	連語	*	*	*	に対して	ニタイシテ	ニタイシテ	O
、	記号	読点	*	*	*	*	、	、	、	O
あと	名詞	一般	*	*	*	*	あと	アト	アト	O
付け	名詞	接尾	一般	*	*	*	付け	ヅケ	ズケ	O
で	助詞	格助詞	一般	*	*	*	で	デ	デ	O
Visual	名詞	一般	*	*	*	*	*	B-T010
Studio	名詞	一般	*	*	*	*	*	B-T010
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
デバッガ	名詞	一般	*	*	*	*	デバッガ	デバッガ	デバッガ	O
を	助詞	格助詞	一般	*	*	*	を	ヲ	ヲ	O
接続	名詞	サ変接続	*	*	*	*	接続	セツゾク	セツゾク	O
する	動詞	自立	*	*	サ変・スル	基本形	する	スル	スル	O
方法	名詞	一般	*	*	*	*	方法	ホウホウ	ホーホー	O
です	助動詞	*	*	*	特殊・デス	基本形	です	デス	デス	O
。	記号	句点	*	*	*	*	。	。	。	O
まあ	副詞	一般	*	*	*	*	まあ	マア	マー	O
、	記号	読点	*	*	*	*	、	、	、	O
よく	副詞	一般	*	*	*	*	よく	ヨク	ヨク	O
よく	副詞	一般	*	*	*	*	よく	ヨク	ヨク	O
聞い	動詞	自立	*	*	五段・カ行イ音便	連用タ接続	聞く	キイ	キイ	O
てる	動詞	非自立	*	*	一段	基本形	てる	テル	テル	O
と	助詞	接続助詞	*	*	*	*	と	ト	ト	O
UiPath	名詞	一般	*	*	*	*	*	B-T010
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
固有	名詞	一般	*	*	*	*	固有	コユウ	コユー	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
やり方	名詞	一般	*	*	*	*	やり方	ヤリカタ	ヤリカタ	O
と	助詞	格助詞	引用	*	*	*	と	ト	ト	O
いう	動詞	自立	*	*	五段・ワ行促音便	基本形	いう	イウ	イウ	O
より	助詞	格助詞	一般	*	*	*	より	ヨリ	ヨリ	O
は	助詞	係助詞	*	*	*	*	は	ハ	ワ	O
Visual	名詞	固有名詞	組織	*	*	*	*	B-T010
Studio	名詞	一般	*	*	*	*	*	B-T010
で	助詞	格助詞	一般	*	*	*	で	デ	デ	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
デバッグ	名詞	サ変接続	*	*	*	*	デバッグ	デバッグ	デバッグ	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
一般	名詞	一般	*	*	*	*	一般	イッパン	イッパン	O
論	名詞	接尾	一般	*	*	*	論	ロン	ロン	O
ぽい	形容詞	接尾	*	*	形容詞・アウオ段	基本形	ぽい	ポイ	ポイ	O
です	助動詞	*	*	*	特殊・デス	基本形	です	デス	デス	O
。	記号	句点	*	*	*	*	。	。	。	O
Visual	名詞	一般	*	*	*	*	*	B-T010
Studio	名詞	一般	*	*	*	*	*	B-T010
開発	名詞	サ変接続	*	*	*	*	開発	カイハツ	カイハツ	O
に	助詞	格助詞	一般	*	*	*	に	ニ	ニ	O
慣れ	動詞	自立	*	*	一段	連用形	慣れる	ナレ	ナレ	O
てる	動詞	非自立	*	*	一段	基本形	てる	テル	テル	O
ヒト	名詞	一般	*	*	*	*	ヒト	ヒト	ヒト	O
に	助詞	格助詞	一般	*	*	*	に	ニ	ニ	O
は	助詞	係助詞	*	*	*	*	は	ハ	ワ	O
もしかして	副詞	一般	*	*	*	*	もしかして	モシカシテ	モシカシテ	O
当たり前	名詞	形容動詞語幹	*	*	*	*	当たり前	アタリマエ	アタリマエ	O
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
事	名詞	非自立	一般	*	*	*	事	コト	コト	O
だっ	助動詞	*	*	*	特殊・ダ	連用タ接続	だ	ダッ	ダッ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
の	名詞	非自立	一般	*	*	*	の	ノ	ノ	O
かも	助詞	副助詞	*	*	*	*	かも	カモ	カモ	O
。	記号	句点	*	*	*	*	。	。	。	O
まあ	副詞	一般	*	*	*	*	まあ	マア	マー	O
Java	名詞	一般	*	*	*	*	*	B-T010
で	助詞	格助詞	一般	*	*	*	で	デ	デ	O
Eclipse	名詞	一般	*	*	*	*	*	B-T010
の	助詞	連体化	*	*	*	*	の	ノ	ノ	O
ケース	名詞	一般	*	*	*	*	ケース	ケース	ケース	O
で	助詞	格助詞	一般	*	*	*	で	デ	デ	O
も	助詞	係助詞	*	*	*	*	も	モ	モ	O
、	記号	読点	*	*	*	*	、	、	、	O
たとえば	接続詞	*	*	*	*	*	たとえば	タトエバ	タトエバ	O
Maven	名詞	一般	*	*	*	*	*	O
で	助詞	格助詞	一般	*	*	*	で	デ	デ	O
起動	名詞	サ変接続	*	*	*	*	起動	キドウ	キドー	O
し	動詞	自立	*	*	サ変・スル	連用形	する	シ	シ	O
た	助動詞	*	*	*	特殊・タ	基本形	た	タ	タ	O
WEB	名詞	一般	*	*	*	*	*	O
アプリ	名詞	一般	*	*	*	*	*	O
を	助詞	格助詞	一般	*	*	*	を	ヲ	ヲ	O
デバッグ	名詞	サ変接続	*	*	*	*	デバッグ	デバッグ	デバッグ	O
する	動詞	自立	*	*	サ変・スル	基本形	する	スル	スル	O
とき	名詞	非自立	副詞可能	*	*	*	とき	トキ	トキ	O

'''
