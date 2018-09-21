# -*- coding: utf-8 -*-
"""
Аппликатор модели wordchar2vector для чатбота.
Используется для генерации векторов тех слов, которые заранее
не обработаны (см. скрипт wordchar2vector.py в режиме --train 0 --vectorize 1)
"""

from __future__ import print_function

import six
import numpy as np
import os
import codecs
import random
import json
import logging

import keras.callbacks
from keras.layers.core import Activation, RepeatVector, Dense, Masking
from keras.layers import recurrent
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.layers import Embedding
from keras.layers.wrappers import Bidirectional
from keras.layers import Dense, Dropout, Input, Permute, Flatten, Reshape
from keras.layers import Conv1D, GlobalMaxPooling1D, GlobalAveragePooling1D
from keras.layers import TimeDistributed
from keras.models import Model
from keras.models import model_from_json

from trainers.wordchar2vector_trainer import FILLER_CHAR  # символ для выравнивания слов по одинаковой длине
from trainers.wordchar2vector_trainer import BEG_CHAR  # символ отмечает начало цепочки символов слова
from trainers.wordchar2vector_trainer import END_CHAR  # символ отмечает конец цепочки символов слова

class Wordchar2VectorModel:
    def __init__(self):
        #super(Wordchar2VectorModel, self).__init__()
        self.logger = logging.getLogger('Wordchar2VectorModel')
        self.model = None
        self.model_config = None
        self.word2vector = dict()

    def load(self, models_folder):
        self.logger.info('Loading Wordchar2VectorModel model files')

        with open(os.path.join(models_folder, 'wordchar2vector.config'), 'r') as f:
            self.model_config = json.load(f)

        # грузим готовую модель
        with open(self.model_config['arch_filepath'], 'r') as f:
            self.model = model_from_json(f.read())

        self.model.load_weights(self.model_config['weights_path'])

        # прочие параметры
        self.vec_size = self.model_config['vec_size']
        self.max_word_len = self.model_config['max_word_len']
        self.char2index = self.model_config['char2index']
        self.nb_chars = len(self.char2index)

    def vectorize_word(self, word, X_batch, irow):
        for ich, ch in enumerate(word):
            if ch not in self.char2index:
                self.logger.error(u'Char "{}" code={} word="{}" missing in char2index'.format(ch, ord(ch), word))
            else:
                X_batch[irow, ich] = self.char2index[ch]

    def build_vector(self, word):
        if word in self.word2vector:
            return self.word2vector[word]

        X_data = np.zeros((1, self.max_word_len + 2), dtype=np.int32)
        self.vectorize_word(word, X_data, 0)

        y_pred = self.model.predict(x=X_data, verbose=0)

        word_vect = y_pred[0, :]
        self.word2vector[word] = word_vect
        return word_vect





