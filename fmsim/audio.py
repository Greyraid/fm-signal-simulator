import numpy as np
from scipy.io import wavfile
from scipy import signal

def load_audio(path: str, target_fs: int) -> tuple[np.ndarray, int]:
    fs, audio = wavfile.read(path)
    
    # Convert stereo to mono
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    
    # Convert to float
    audio = audio.astype(np.float32)

    # Normalize to -1 to 1
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
    
    #Resample if needed
    if fs != target_fs:
        gcd = np.gcd(fs, target_fs)
        up = target_fs // gcd #scales up the sampling rate by a factor
        down = fs // gcd #discard samples to scale down the sampling rate by a factor
        audio = signal.resample_poly(audio, up, down)
        fs = target_fs

    return audio.astype(np.float32), fs