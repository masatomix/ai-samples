### GooラボのAPI実行サンプル

```
# cd samples
# pip install -r requirement.txt
# cat config/config.ini    <- config.ini.sampleを見ながら作成する
[payload]
  app_id = 31e6xxxx  <- GooラボのAPIキーをセット

.. 割愛
# python3 goolab.py
```


### GooラボのAPIから固有表現を取得して、教師データを作成するサンプル。
ついでに、答えのデータ( https://raw.githubusercontent.com/Hironsan/IOB2Corpus/master/hironsan.txt )との比較結果も出力する。


```
# cd samples
# pip install -r requirement.txt
# curl https://raw.githubusercontent.com/Hironsan/IOB2Corpus/master/hironsan.txt -o teach_data.txt
# python3 auto_create_teach_data.py 0 30
```


### pycrfsuite を用いた、教師データ作成と、AI実行サンプル。


```
# cd samples
# pip install -r requirement_crf.txt
# curl https://raw.githubusercontent.com/Hironsan/IOB2Corpus/master/hironsan.txt -o teach_data.txt
# python3 crf_training_and_test.py
```

## Vagrantで環境構築して実行してみる

Vagrantがなかったり、自分のPython環境があれば適宜実行してください。

```
$ vagrant up
$ vagrant ssh
...
Last login: Sun Dec  9 21:46:35 2018 from 10.0.2.2

vagrant@ubuntu-xenial:~$ cd /vagrant/samples/
vagrant@ubuntu-xenial:/vagrant/samples$ source ~/venv/bin/activate
(venv) vagrant@ubuntu-xenial:/vagrant/samples$ pip install -r requirement.txt
```

### 教師データの作成
input ディレクトリ内のテキストファイルから形態素解析データを作成し、そこに教師データを付与するサンプル。

(以下、シェルのprefixは割愛しますがvagrant内のLinuxで作業)


```
(venv) $ cat input/teach_data_per_file.tsv
filename	value	tag
sample.txt	Visual	T010
sample.txt	Studio	T010
sample.txt	Robot	T010
sample.txt	UiPath	T010
sample2.txt	Visual	T010
sample2.txt	Studio	T010
sample2.txt	UiPath	T010
sample2.txt	Java	T010
sample2.txt	Eclipse	T010
```

って感じでテキストに出現する固有表現に大使邸、T010というタグをつけています。(タグは任意の種類を作成できると思います)

```
(venv) $ python3 create_teach_data_per_file.py

.....
$ ls -lrt result/*.txt
-rw-r--r-- 1 vagrant vagrant  6210 12月  9 21:56 result/sample2.txt
-rw-r--r-- 1 vagrant vagrant  6503 12月  9 21:56 result/sample.txt
-rw-r--r-- 1 vagrant vagrant 12717 12月  9 21:56 result/result.txt

(venv) $ head result/result.txt
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
(venv) $ 
```

作成されました。

### 教師データをつかった学習と、テスト

```
$ cp -pfr result/result.txt ./teach_data.txt
$ python3 crf_training_and_test.py
	さて	今回	の	ワークショップ	は	Event	Monitoring	や	AI	連携	など	が	あり	まし	た	が	、	自分	的	に	目玉	だっ	た	の	は	「	Debugging	Custom	Activities	」	つまり	「	カスタムアクティビティ	の、	デバッガ	による	デバッグ	方法	について	」	です	。	ちょっと	まえ	UiPath	における	カスタムアクティビティ	の	開発	方法	を	結構	調べ	て	い	た	の	です	が	、	情報	が	なく	て	困っ	て	いた	の	が	開発	し	た	アクティビティ	の	デバッグ	です	。	開発	し	た	アクティビティ	は	nupkg	になっ	て	UiPath	Studio	や	Robot	から	実行	さ	れる	わけ	で	、	Visual	Studio	から	デバッグ	起動	って	出来	ない	なー	って	おもっ	て	まし	た	。
Predicted:	 O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	O	O	O	O	B-T010	B-T010	B-T010	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	O	B-T010	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	B-T010	B-T010	O	B-T010	O	O	O	O	O	O	O	B-T010	B-T010	O	O	O	O	O	O	OO	O	O	O	O	O
Correct:	 O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	O	B-T010	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	B-T010	B-T010	O	B-T010	O	O	O	O	O	O	O	B-T010	B-T010	O	O	O	O	O	O	OO	O	O	O	O	O
...
              precision    recall  f1-score   support

      B-T010       0.81      1.00      0.89        17

   micro avg       0.81      1.00      0.89        17
   macro avg       0.81      1.00      0.89        17
weighted avg       0.81      1.00      0.89        17

UiPath	は	、	2005	年	に	スタート	し	た	「	日本	680	社	*	および	世界	1	,	800	社の	実績	」	を	持つ	RPA	業界	の	リーディング	カンパニー	です
Predicted:	 B-T010	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	O	OO	O	O	O	O	O	O	O	O	O	O
(venv) $
```

実行できましたね。


