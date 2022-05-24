import librosa
import tensorflow as tf
import numpy as np
import os
import pandas as pd
import math
import tensorflow as tf

model_kd = tf.keras.models.load_model('models\conv2d_kd')
model_sd = tf.keras.models.load_model('models\conv2d_sd')
model_hh = tf.keras.models.load_model('models\conv2d_hh')

def get_onsets(audio_path, sr=44100):
  sig, sr = librosa.load(audio_path, sr=sr)
  onset_times = librosa.onset.onset_detect(sig, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1, units="time")

  return onset_times

def parse_spectrogram(onset_times, fn_wav, sr=44100, n_fft=2048):
  delta = 0.15 # second
  specs = []
  for onset in onset_times:
    onset = onset-0.025
    onset = 0 if onset < 0 else onset
    sig, Fs = librosa.load(fn_wav, offset=onset, duration=delta, sr=sr)
    S = librosa.feature.melspectrogram(y=sig, sr=sr, n_fft=n_fft, fmin=20, fmax=20000)
    ps_db= librosa.power_to_db(S, ref=np.max)

    specs.append(ps_db)

  return np.array(specs)

def predict_classes(spectrograms: np.array):
  # for spec in spectrograms:
  preds_kd = model_kd.predict(spectrograms)
  preds_sd = model_sd.predict(spectrograms)
  preds_hh = model_hh.predict(spectrograms)
  
  return preds_kd.round(), preds_sd.round(), preds_hh.round()

def create_tab(df, bpm):
  return \
  "x-x-x-x-x-x-x-x-|x-x-x-x-x-x-x-x-|x-x-x-x-x-x-x-x-|x-x-x-x-x-x-x-x-|", \
  "----o-------o---|----o-------o---|----o-------o---|----o-------o---|", \
  "o---o---o---o---|o---o---o---o---|o---o---o---o---|o---o---o---o---|"

  last_hit = math.ceil(df["onset_times"].max())
  num_beat = math.ceil(bpm * (last_hit/60))
  bars = []
  for i in range(math.ceil(num_beat/4)):
    bars.append("----------------")
    pass

  HH = list("|".join(bars))
  SD = list("|".join(bars))
  KD = list("|".join(bars))

  gap_per_hit = (60/bpm)/4

  for idx, row in df.iterrows():
    if idx == 0:
      idx = 1
      start = row["onset_times"]
    else:
      idx = int(((row["onset_times"] - start)/gap_per_hit) + 1)
      idx = int(idx + (idx/16))

    try:
      if row[" KD "] == 1:
        KD[idx] = "x"
      if row[" SD "] == 1:
        SD[idx] = "x"
      if row[" HH "] == 1:
        HH[idx] = "x"
    except:
      pass

  return "".join(HH), "".join(SD), "".join(KD)

def do_transcription(audio_file, sr=22050):
  # drum_path = split_drum(audio_file)
  # onset_times = get_onsets(audio_file, sr=sr)
  # specs = parse_spectrogram(onset_times, audio_file, sr=sr)
  # preds_kd, preds_sd, preds_hh = predict_classes(specs)

  # df = pd.DataFrame({
  #     "onset_times": onset_times,
  #     " KD ": preds_kd.reshape(-1),
  #     " SD ": preds_sd.reshape(-1),
  #     " HH ": preds_hh.reshape(-1),
  # })
  bpm = 110
  HH, SD, KD = create_tab(pd.DataFrame(), bpm)
  return HH, SD, KD, bpm