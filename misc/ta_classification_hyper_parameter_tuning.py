# -*- coding: utf-8 -*-
"""TA: Classification Hyper-parameter Tuning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1llMwY-2ntVjlXZtBLIgbBxm2ed1Uqjz2
"""

import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import *
from tensorflow.keras.regularizers import *
from tensorflow.keras.callbacks import EarlyStopping

import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

training_file_mdb = open("./datasets/MDB_44100.pickle", "rb")
training_set_mdb = pickle.load(training_file_mdb)
training_file_mdb.close()

training_file_idmt = open("./datasets/IDMT_44100.pickle", "rb")
training_set_idmt = pickle.load(training_file_idmt)
training_file_idmt.close()

training_set = {}
training_set["X"] = np.append(training_set_mdb["X"], training_set_idmt["X"], axis=0)
training_set["y"] = np.append(training_set_mdb["y"], training_set_idmt["y"], axis=0)

x_train, x_test, y_train, y_test = train_test_split(training_set['X'], training_set['y'], random_state=42, test_size=0.2)
x_train.shape, x_test.shape, y_train.shape, y_test.shape

x_test, x_val, y_test, y_val = train_test_split(x_test, y_test, random_state=42, test_size=0.5)
x_test.shape, x_val.shape, y_test.shape, y_val.shape

def train_test_model(params):
  tf.keras.backend.clear_session()
  
  model = Sequential()
  model.add(Input(shape=(x_train.shape[1], x_train.shape[2])))
  model.add(BatchNormalization())
  model.add(Permute((2, 1)))
  model.add(LSTM(units=params['lstm_unit'], activation=params['lstm_activation'], return_sequences=True))
  model.add(Dropout(params['dropout']))
  model.add(LSTM(units=params['lstm_unit']*2, activation=params['lstm_activation'], return_sequences=True))
  model.add(Dropout(params['dropout']))
  model.add(LSTM(units=params['lstm_unit']*4, activation=params['lstm_activation']))
  model.add(Dropout(params['dropout']))
  model.add(Dense(3, activation='sigmoid'))

  
  early = EarlyStopping(monitor='val_loss', min_delta=0, patience=10, verbose=1, mode='auto')
  
  model.compile(
      loss='binary_crossentropy',
      optimizer='adam',
      metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])
  
  history = model.fit(x_train, y_train[:, :3], 
          epochs=200,
          batch_size=8, 
          validation_data=(x_val, y_val[:, :3]),
          callbacks=[early]
         )
  
  eval_result = model.evaluate(x_test, y_test[:, :3])
  tf.keras.models.save_model(model, f"./grid_models/LSTM_{params['lstm_unit']}_unit_{params['lstm_activation']}_activation_{str(params['dropout']).replace('.', ',')}_dropout/")

  return history, eval_result

data = []

lstm_units = [2, 4, 8, 16, 128, 256]
lstm_activations = ['relu', 'tanh']
dropouts = [0.3, 0.2, 0.1, 0.4]

for lstm_unit in lstm_units:
  for lstm_activation in lstm_activations:
    for dropout in dropouts:
            hparams = {
                'lstm_unit': lstm_unit,
                'lstm_activation': lstm_activation,
                'dropout': dropout,
            }
            print("using param:\n", hparams)

            history, eval = train_test_model(hparams)

            history_file = f"{lstm_unit}_{lstm_activation}_{str(dropout).replace('.', ',')}.pck"
            history_file = open(history_file, "wb")
            pickle.dump(history, history_file)
            history_file.close()
            
            hparams['loss'] = eval[0]
            hparams['acc'] = eval[1]
            hparams['precision'] = eval[2]
            hparams['recall'] = eval[3]
            
            data.append(hparams)


grid_search_result = pd.DataFrame(data)
grid_search_result.to_csv("./grid_search_result.csv")

