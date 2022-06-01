import librosa
import tensorflow as tf
import numpy as np
import os
import math
import tensorflow as tf
from utils.bpm_detection import detect_bpm

# model_kd = tf.keras.models.load_model('models\conv2d_kd')
# model_sd = tf.keras.models.load_model('models\conv2d_sd')
# model_hh = tf.keras.models.load_model('models\conv2d_hh')
model = tf.keras.models.load_model('models\LSTM')


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
  pass
  # for spec in spectrograms:
  # preds_kd = model_kd.predict(spectrograms)
  # preds_sd = model_sd.predict(spectrograms)
  preds = model.predict(spectrograms)
  
  # return preds_kd.round(), preds_sd.round(), preds_hh.round()
  return preds[:, 0].round(), preds[:, 1].round(), preds[:, 2].round()

def create_tab(result_dict, bpm):

  last_hit = math.ceil(result_dict["onset_times"].max())
  num_beat = math.ceil(bpm * (last_hit/60))
  bars = []
  for i in range(math.ceil(num_beat/4)):
    bars.append("----------------")
    pass

  HH = list("|".join(bars))
  SD = list("|".join(bars))
  KD = list("|".join(bars))

  gap_per_hit = (60/bpm)/4

  idx = 0
  for i in range(len(result_dict["onset_times"])):
    onset = result_dict["onset_times"][i]
    curr_KD = result_dict["KD"][i]
    curr_SD = result_dict["SD"][i]
    curr_HH = result_dict["HH"][i]

    if idx == 0:
      idx = 1
      start = onset
    else:
      idx = int(((onset - start)/gap_per_hit) + 1)
      idx = int(idx + (idx/16))

    try:
      if curr_KD == 1:
        KD[idx] = "x"
      if curr_SD == 1:
        SD[idx] = "x"
      if curr_HH == 1:
        HH[idx] = "x"
    except:
      pass
    # idx += 1

  return "".join(HH), "".join(SD), "".join(KD)

def do_transcription(audio_file, sr=44100):
  # drum_path = split_drum(audio_file)
  print("test 1")
  onset_times = get_onsets(audio_file, sr=sr)
  print("test 2")
  
  specs = parse_spectrogram(onset_times, audio_file, sr=sr)
  print("test 3")
  
  preds_kd, preds_sd, preds_hh = predict_classes(specs)
  print(preds_kd, preds_sd, preds_hh)
  print("test 4")

  bpm = detect_bpm(audio_file.__str__()).round()
  print("test 5")

  HH, SD, KD = create_tab({
    "onset_times": onset_times,
    "KD": preds_kd,
    "SD": preds_sd,
    "HH": preds_hh
  }, bpm)
  return HH, SD, KD, bpm