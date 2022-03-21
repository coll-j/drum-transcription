import librosa

def test_librosa(file):
    sig, fs = librosa.load(file)

    return sig, fs