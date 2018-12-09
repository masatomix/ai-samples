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
