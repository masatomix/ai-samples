#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pycrfsuite
from nlp import TextReader

from itertools import chain
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer


def main(args):
    # サイトから、コーパスデータをとってくる
    # c = TextReader('https://raw.githubusercontent.com/Hironsan/IOB2Corpus/master/hironsan.txt',train_test_ratio=0.9)

    c = TextReader(path='teach_data.txt', train_test_ratio=0.7)

    x_train, y_train = do_train(c)

    x_test, y_test = do_test(c)
    do_report(x_train, y_train, x_test, y_test)

    execute('UiPathは、2005年にスタートした「日本680社*および世界1,800社の実績」を持つRPA業界のリーディングカンパニーです')


def execute(sentence):
    tagger = pycrfsuite.Tagger()
    tagger.open('model.crfsuite')

    # ただ一件、テストで処理してみる。
    from nlp import MecabFacade
    f = MecabFacade('-Ochasen ', padding=False)
    rs = f.parse(sentence).results()

    print('\t'.join(sent2tokens(rs)))
    print("Predicted:\t", '\t'.join(tagger.tag(sent2features(rs))))


def do_train(reader):
    train_sents = reader.iob_sents('train')

    # print(train_sents[0][0])
    # print(train_sents[0][1])
    # for train_sent in train_sents:
    #     print(train_sent)
    # print(sent2features(train_sents[0])[0])

    x_train = [sent2features(s) for s in train_sents]  # trains_sents の各要素をsent2featuresをくぐらせて、結果を再度配列化
    y_train = [sent2labels(s) for s in train_sents]  # trains_sents の各要素をssent2label をくぐらせて、結果を再度配列化

    trainer = pycrfsuite.Trainer(verbose=False)

    for xseq, yseq in zip(x_train, y_train):
        trainer.append(xseq, yseq)

    trainer.set_params({
        'c1': 1.0,  # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 50,  # stop earlier
        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })
    trainer.train('model.crfsuite')

    return (x_train, y_train)


def do_test(reader):
    test_sents = reader.iob_sents('test')

    x_test = [sent2features(s) for s in test_sents]
    y_test = [sent2labels(s) for s in test_sents]

    tagger = pycrfsuite.Tagger()
    tagger.open('model.crfsuite')

    for example_sent in test_sents:
        sys.stdout.write('\t')
        print('\t'.join(sent2tokens(example_sent)))
        print("Predicted:\t", '\t'.join(tagger.tag(sent2features(example_sent))))
        print("Correct:\t", '\t'.join(sent2labels(example_sent)))

    return (x_test, y_test)


def do_report(x_train, y_train, x_test, y_test):
    tagger = pycrfsuite.Tagger()
    tagger.open('model.crfsuite')
    y_pred = [tagger.tag(xseq) for xseq in x_test]
    print(bio_classification_report(y_test, y_pred))


def bio_classification_report(y_true, y_pred):
    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
    y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))

    tagset = set(lb.classes_) - {'O'}
    tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}

    return classification_report(
        y_true_combined,
        y_pred_combined,
        labels=[class_indices[cls] for cls in tagset],
        target_names=tagset,
    )


# 以下はほぼ、
# http://bit.ly/2L8EzNu
# 【チュートリアル】機械学習を使って30分で固有表現抽出器を作る の引用です。ありがとうございます！
def is_hiragana(ch):
    return 0x3040 <= ord(ch) <= 0x309F


def is_katakana(ch):
    return 0x30A0 <= ord(ch) <= 0x30FF


def get_character_type(ch):
    if ch.isspace():
        return 'ZSPACE'
    elif ch.isdigit():
        return 'ZDIGIT'
    elif ch.islower():
        return 'ZLLET'
    elif ch.isupper():
        return 'ZULET'
    elif is_hiragana(ch):
        return 'HIRAG'
    elif is_katakana(ch):
        return 'KATAK'
    else:
        return 'OTHER'


def get_character_types(string):
    character_types = map(get_character_type, string)
    character_types_str = '-'.join(sorted(set(character_types)))

    return character_types_str


def extract_pos_with_subtype(morph):
    idx = morph.index('*')

    return '-'.join(morph[1:idx])


def word2features(sent, i):
    word = sent[i][0]

    chtype = get_character_types(sent[i][0])
    postag = extract_pos_with_subtype(sent[i])
    features = [
        'bias',
        'word=' + word,
        'type=' + chtype,
        'postag=' + postag,
    ]
    if i >= 2:
        word2 = sent[i - 2][0]
        chtype2 = get_character_types(sent[i - 2][0])
        postag2 = extract_pos_with_subtype(sent[i - 2])
        iobtag2 = sent[i - 2][-1]
        features.extend([
            '-2:word=' + word2,
            '-2:type=' + chtype2,
            '-2:postag=' + postag2,
            '-2:iobtag=' + iobtag2,
        ])
    else:
        features.append('BOS')

    if i >= 1:
        word1 = sent[i - 1][0]
        chtype1 = get_character_types(sent[i - 1][0])
        postag1 = extract_pos_with_subtype(sent[i - 1])
        iobtag1 = sent[i - 1][-1]
        features.extend([
            '-1:word=' + word1,
            '-1:type=' + chtype1,
            '-1:postag=' + postag1,
            '-1:iobtag=' + iobtag1,
        ])
    else:
        features.append('BOS')

    if i < len(sent) - 1:
        word1 = sent[i + 1][0]
        chtype1 = get_character_types(sent[i + 1][0])
        postag1 = extract_pos_with_subtype(sent[i + 1])
        features.extend([
            '+1:word=' + word1,
            '+1:type=' + chtype1,
            '+1:postag=' + postag1,
        ])
    else:
        features.append('EOS')

    if i < len(sent) - 2:
        word2 = sent[i + 2][0]
        chtype2 = get_character_types(sent[i + 2][0])
        postag2 = extract_pos_with_subtype(sent[i + 2])
        features.extend([
            '+2:word=' + word2,
            '+2:type=' + chtype2,
            '+2:postag=' + postag2,
        ])
    else:
        features.append('EOS')

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]


def sent2labels(sent):
    return [morph[-1] for morph in sent]


def sent2tokens(sent):
    return [morph[0] for morph in sent]


if __name__ == "__main__":
    main(sys.argv)
