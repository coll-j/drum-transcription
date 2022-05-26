# -*- coding: utf-8 -*-
"""TA: Onset Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TJsOuo12hcmTzf0L-7-JbuxeRQlwqSmi
"""

import librosa
import numpy as np
import mir_eval

import os
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator
from sklearn.metrics import make_scorer

AUDIO_DIR = "./MDBDrums/MDB Drums/audio/drum_only"
CLASS_ANNOTATION_DIR = "./MDBDrums/MDB Drums/annotations/class"
BEATS_ANNOTATION_DIR = "./MDBDrums/MDB Drums/annotations/beats"

"""# Grid search"""

grid_params = {
    "pre_max": [i for i in range(1, 2)],
    "post_max": [i for i in range(1, 2)],
    "pre_avg": [i for i in range(1, 2)],
    "post_avg": [i for i in range(1, 2)],
    # "delta": [0.1, 0.2, 0.3],
    "delta": [0.1],
    "wait": [i for i in range(1, 2)],
}


def process_audio():
  sigs = []
  truths = []

  for audio in os.listdir(AUDIO_DIR):
    audio_path = os.path.join(AUDIO_DIR, audio)
    txt_path = os.path.join(CLASS_ANNOTATION_DIR, audio).replace("Drum.wav", "class.txt")
    print(txt_path)
    # audio_path = "/content/drums.wav"
    sig, sr = librosa.load(audio_path, sr=44100)
    sigs.append(sig)

    df = pd.read_csv(
      os.path.join(txt_path),
      sep= '\t',
      lineterminator='\n',
      header=None
      )
    ground_truth = np.unique(df[0].values)
    truths.append(ground_truth)

  return sigs, truths


class OnsetDetection(BaseEstimator):
  def __init__(self, delta=0.1, post_avg=1, pre_avg=1, post_max=1, pre_max=1, wait=1):
    self.delta = delta
    self.post_avg = post_avg
    self.pre_avg = pre_avg
    self.post_max = post_max
    self.pre_max = pre_max
    self.wait = wait

  def fit(self, data_x, data_y):
    return self

  def set_params(self, **parameters):
    for parameter, value in parameters.items():
      setattr(self, parameter, value)
    return self

  def predict(self, sigs):
    preds = []
    for sig in sigs:
      pred = librosa.onset.onset_detect(y=sig, sr=44100, units='time', 
                                       pre_max=self.pre_max, 
                                       post_max=self.post_max, 
                                       pre_avg=self.pre_avg, 
                                       post_avg=self.post_avg, 
                                       delta=self.delta, 
                                       wait=self.wait)
      preds.append(pred)
    
    return preds

def evaluate(ground_truth, onset_times):
  assert len(ground_truth) == len(onset_times)
  evals = []
  for i in range(len(ground_truth)):
    eval = mir_eval.onset.evaluate(ground_truth[i], onset_times[i])
    evals.append(eval['F-measure'])

  return np.array(evals).mean()

onset_scorer = make_scorer(evaluate, greater_is_better=True)
sigs, truths = process_audio()

search = GridSearchCV(OnsetDetection(),
                   scoring=onset_scorer,
                   param_grid=grid_params,
                   verbose=2)

search.fit(sigs, truths)

print("Best params:")
print(search.best_params_, search.best_score_)
