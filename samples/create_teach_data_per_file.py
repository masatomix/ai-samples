#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import glob
import pandas as pd
import re
from nlp import TeachDataCreator

from logging import getLogger
import logging.config



def main(args):
    logger = getLogger()
    logging.config.fileConfig("config/logging.conf")

    """
    inputディレクトリにある *.txt ファイル内の文章を形態素解析して、さらに、input/teach_data_per_file.tsv に基づいてタグ付けをし、
    最終的にresultディレクトリに 形態素解析結果とタグ付け結果を、ファイルに出力する。
    :param args:
    :return:
    """

    # 固有表現情報ファイルを読み込み
    df = pd.read_table('input/teach_data_per_file.tsv')

    creator = TeachDataCreator(options="-Ochasen", padding=False)

    paths = glob.glob(os.path.join("./input/", "*.txt"))
    for path in paths:
        with open(path) as f:
            s = f.read()
            # s = re.sub(r" +", " ", s)  # 改行はのこし、連続のスペースを一つにする。
            s = re.sub(r"\s+", " ", s) # 改行も残さず、連続のスペースを一つにする。
        entities_df = df[df['filename'] == os.path.basename(path)]
        entities_df = entities_df.astype({'value': 'str'})

        results = creator.create_teach_data(s, entities=entities_df[['value', 'tag']].values)
        # results = creator.create_teach_data(s)
        creator.save_teach_data(results, "./result", file_name=os.path.basename(path))

        os.makedirs("./tmp/", exist_ok=True)
        with open(os.path.join("./tmp/", os.path.basename(path)), mode='w') as f:
            f.write(s)

    creator.concat_teach_data("./result")


if __name__ == "__main__":
    main(sys.argv)
