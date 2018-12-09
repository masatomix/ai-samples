

## Vagrantで環境構築して実行してみる

Vagrantがなかったり、自分のPython環境があれば適宜実行してください。

```
$ vagrant up
... 割愛
$ vagrant ssh
...
Last login: Sun Dec  9 21:46:35 2018 from 10.0.2.2

vagrant@ubuntu-xenial:~$ cd /vagrant/samples/
vagrant@ubuntu-xenial:/vagrant/samples$ source ~/venv/bin/activate
(venv) vagrant@ubuntu-xenial:/vagrant/samples$
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
(venv) $ ls -lrt result/*.txt
-rw-r--r-- 1 vagrant vagrant  6210 12月  9 21:56 result/sample2.txt
-rw-r--r-- 1 vagrant vagrant  6503 12月  9 21:56 result/sample.txt
-rw-r--r-- 1 vagrant vagrant 12717 12月  9 21:56 result/result.txt

(venv) $  head -50 result/result.txt
...
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
(venv) $ 
```

作成されました。一部のデータにB-T010というタグ付けがされています。。
(この処理微妙にバグってるんですが、まあヨシとしましょう)


### 教師データをつかった学習と、テスト

```
(venv) $ cp -pfr result/result.txt ./teach_data.txt
(venv) $ python3 crf_training_and_test.py
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



### GooラボのAPI実行サンプル

```
(venv) $ cat config/config.ini    <- config.ini.sampleを見ながら作成する
[payload]
  app_id = 31e6xxxx  <- GooラボのAPIキーをセット

.. 割愛
(venv) $ python3 goolab.py
sentence: [鈴木さんがきょうの9時30分に横浜に行きます。]
固有表現抽出結果:
['鈴木', 'PSN']
['きょう', 'DAT']
['9時30分', 'TIM']
['横浜', 'LOC']
形態素解析結果:
['鈴木', '名詞', 'スズキ']
['さん', '名詞接尾辞', 'サン']
['が', '格助詞', 'ガ']
['きょう', '名詞', 'キョウ']
['の', '格助詞', 'ノ']
['9時', '名詞', 'クジ']
['30分', '名詞', 'サンジュップン']
['に', '格助詞', 'ニ']
['横浜', '名詞', 'ヨコハマ']
['に', '格助詞', 'ニ']
['行', '動詞語幹', 'イ']
['き', '動詞活用語尾', 'キ']
['ます', '動詞接尾辞', 'マス']
['。', '句点', '＄']
(venv) $
```

実行できました。


### GooラボのAPIから固有表現を取得して、教師データを作成するサンプル。
ついでに、答えのデータ( https://raw.githubusercontent.com/Hironsan/IOB2Corpus/master/hironsan.txt )との比較結果も出力する。

```
(venv) $ curl https://raw.githubusercontent.com/Hironsan/IOB2Corpus/master/hironsan.txt -o teach_data.txt
(venv) $ python3 auto_create_teach_data.py 0 30
...
2018/12/09 22:47:32 - root - INFO - ---------------------------------------
2018/12/09 22:47:32 - root - INFO - Total: 654
2018/12/09 22:47:32 - root - INFO -    OK: 609
2018/12/09 22:47:32 - root - INFO -    NG: 45
2018/12/09 22:47:32 - root - INFO -  割合: 93.1 %
2018/12/09 22:47:32 - root - INFO -  文章総数: 501 文
(venv) $
```

実行出来ました。

