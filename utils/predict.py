from subprocess import call as sub_process_call
from librosa import load as load_audio, power_to_db
from librosa.onset import onset_detect
from librosa.feature import melspectrogram
from tensorflow.python.keras.models import load_model
from numpy import max, array
from os.path import dirname, join as path_join
from math import ceil
from utils.bpm_detection import detect_bpm

cwd = dirname(dirname(__file__))
model = load_model(path_join(cwd, "models", "LSTM"))


def get_onsets(audio_path, sr=44100):
  sig, sr = load_audio(audio_path, sr=sr)
  onset_times = onset_detect(
    sig, sr=sr, wait=1, pre_avg=7, post_avg=7, pre_max=1, post_max=1, delta=0.1, units="time")

  return onset_times

def parse_spectrogram(onset_times, fn_wav, sr=44100, n_fft=2048):
  delta = 0.15 # second
  specs = []
  for onset in onset_times:
    onset = onset-0.025
    onset = 0 if onset < 0 else onset
    sig, Fs = load_audio(fn_wav, offset=onset, duration=delta, sr=sr)
    S = melspectrogram(y=sig, sr=sr, n_fft=n_fft, fmin=20, fmax=20000)
    if S.shape[1] == 13:
      ps_db= power_to_db(S, ref=max)

      specs.append(ps_db)

  return array(specs)

def predict_classes(spectrograms: array):
  pass
  preds = model.predict(spectrograms)
  
  return preds[:, 0].round(), preds[:, 1].round(), preds[:, 2].round()

def create_tab(result_dict, bpm):
  last_hit = ceil(result_dict["onset_times"].max())
  num_beat = ceil(bpm * (last_hit/60))
  bars = []
  for i in range(ceil(num_beat/4)):
    bars.append("----------------")
    pass

  HH = list("|".join(bars))
  SD = list("|".join(bars))
  KD = list("|".join(bars))

  gap_per_hit = (60/bpm)/4 # gap per 1e&a dkk

  idx = 0
  for i in range(len(result_dict["onset_times"])):
    try:
      onset = result_dict["onset_times"][i]
      curr_KD = result_dict["KD"][i]
      curr_SD = result_dict["SD"][i]
      curr_HH = result_dict["HH"][i]

      if i == 0:
        start = onset
      else:
        idx = int(((onset - start)/gap_per_hit) + 1) # actual pos
        idx = int(idx + (idx/16)) # escaping the bars

      if curr_KD == 1:
        KD[idx] = "o"
      if curr_SD == 1:
        SD[idx] = "o"
      if curr_HH == 1:
        HH[idx] = "x"
    except Exception as e:
      print(e)
      pass

  return "".join(HH), "".join(SD), "".join(KD)

def do_transcription(audio_file, bpm=None, sr=44100):
  dst = audio_file.__str__().replace(".mp3", ".wav")
  sub_process_call(['ffmpeg', '-i', audio_file.__str__(), dst])

  audio_file = dst

  onset_times = get_onsets(audio_file, sr=sr)
  
  specs = parse_spectrogram(onset_times, audio_file, sr=sr)

  preds_kd, preds_sd, preds_hh = predict_classes(specs)

  if not bpm:
    bpm = detect_bpm(audio_file.__str__()).round()

  HH, SD, KD = create_tab({
    "onset_times": onset_times,
    "KD": preds_kd,
    "SD": preds_sd,
    "HH": preds_hh
  }, bpm)

  return HH, SD, KD, bpm