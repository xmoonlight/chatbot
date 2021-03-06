# -*- coding: utf-8 -*-
'''
Подготовка списка слов для тренировки модели
встраиваний слова wordchar2vector.

(c) by Koziev Ilya inkoziev@gmail.com для чат-бота https://github.com/Koziev/chatbot
'''

from __future__ import print_function

import codecs
import itertools
import os
from sys import platform
import pandas as pd

from utils.tokenizer import Tokenizer

result_path = '../tmp/known_words.txt'  # путь к файлу, где будет сохранен полный список слов для обучения
result2_path = '../tmp/dataset_words.txt'  # путь к файлу со списком слов, которые употребляются в датасетах

n_misspelling_per_word = 0 # кол-во добавляемых вариантов с опечатками на одно исходное слово


# Из этого текстового файла возьмем слова, на которых будем тренировать модель встраивания.
if platform == "win32":
    corpus_path = r'f:\Corpus\word2vector\ru\SENTx.corpus.w2v.txt'
else:
    corpus_path = os.path.expanduser('~/Corpus/word2vector/ru/SENTx.corpus.w2v.txt')

paraphrases_path = '../data/premise_question_relevancy.csv'
synonymy_path = '../data/synonymy_dataset.csv'
pqa_path = '../data/premise_question_answer.csv'
pqa_multy_path = '../data/qa_multy.txt'
eval_path = '../data/evaluate_relevancy.txt'
premises = ['../data/premises.txt', '../data/premises_1s.txt']
interpretations = ['../data/interpretation_auto_4.txt',
                   '../data/interpretation_auto_5.txt',
                   '../data/interpretation.txt']
smalltalk_path = '../data/smalltalk.txt'
# ---------------------------------------------------------------

tokenizer = Tokenizer()

known_words = set()
dataset_words = set()

print('Parsing {}'.format(smalltalk_path))
with codecs.open(smalltalk_path, 'r', 'utf-8') as rdr:
    for line in rdr:
        phrase = line.replace(u'T:', u'').replace(u'Q:', u'').strip()
        words = tokenizer.tokenize(phrase)
        known_words.update(words)
        dataset_words.update(words)

# Берем слова из большого текстового файла, на котором тренируется w2v модели.
print('Parsing {}'.format(corpus_path))
with codecs.open(corpus_path, 'r', 'utf-8') as rdr:
    line_count = 0
    for line0 in rdr:
        line = line0.strip()
        words = line.split(u' ')
        known_words.update(words)
        line_count += 1
        if line_count>1000000:
            break

# Добавим слова из основного тренировочного датасета
print('Parsing {}'.format(paraphrases_path))
df = pd.read_csv(paraphrases_path, encoding='utf-8', delimiter='\t', quoting=3)
for phrase in itertools.chain(df['premise'].values, df['question'].values):
    words = tokenizer.tokenize(phrase.lower())
    known_words.update(words)
    dataset_words.update(words)

print('Parsing {}'.format(synonymy_path))
df = pd.read_csv(synonymy_path, encoding='utf-8', delimiter='\t', quoting=3)
for phrase in itertools.chain(df['premise'].values, df['question'].values):
    words = tokenizer.tokenize(phrase.lower())
    known_words.update(words)
    dataset_words.update(words)

print('Parsing {}'.format(pqa_path))
df = pd.read_csv(pqa_path, encoding='utf-8', delimiter='\t', quoting=3)
for phrase in itertools.chain( df['premise'].values, df['question'].values, df['answer'].values ):
    words = tokenizer.tokenize(phrase)
    known_words.update(words)
    dataset_words.update(words)

# Добавим слова, которые употребляются в датасете для оценки
print('Parsing {}'.format(eval_path))
with codecs.open(eval_path, 'r', 'utf-8') as rdr:
    for line in rdr:
        phrase = line.replace(u'T:', u'').replace(u'Q:', u'').strip()
        words = tokenizer.tokenize(phrase)
        known_words.update(words)
        dataset_words.update(words)

# Добавим слова, которые употребляются в датасете с выводами
print('Parsing {}'.format(pqa_multy_path))
with codecs.open(pqa_multy_path, 'r', 'utf-8') as rdr:
    for line in rdr:
        phrase = line.replace(u'T:', u'').replace(u'Q:', u'').replace(u'A:', u'').strip()
        words = tokenizer.tokenize(phrase)
        known_words.update(words)
        dataset_words.update(words)

for p in premises:
    print('Parsing {}'.format(p))
    with codecs.open(p, 'r', 'utf-8') as rdr:
        for line in rdr:
            phrase = line.strip()
            words = tokenizer.tokenize(phrase)
            known_words.update(words)
            dataset_words.update(words)

# Датасеты интерпретации
for p in interpretations:
    print('Parsing {}'.format(p))
    with codecs.open(p, 'r', 'utf-8') as rdr:
        for line in rdr:
            phrase2 = line.strip()
            for phrase in phrase2.split('|'):
                words = tokenizer.tokenize(phrase)
                known_words.update(words)
                dataset_words.update(words)

print('There are {} known words, {} dataset words'.format(len(known_words), len(dataset_words)))

stop_words = {u'_num_'}

with codecs.open(result_path, 'w', 'utf-8') as wrt:
    for word in sorted(known_words):
        if word not in stop_words and not word.startswith(u' '):
            wrt.write(u'{}\n'.format(word))

with codecs.open(result2_path, 'w', 'utf-8') as wrt:
    for word in sorted(dataset_words):
        if word not in stop_words and not word.startswith(u' '):
            wrt.write(u'{}\n'.format(word))
