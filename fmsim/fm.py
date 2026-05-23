import numpy as np

def fm_modulate(audio: np.ndarray, fs_iq: int, deviation_hz: float) -> np.ndarray:
    audio = audio.astype(np.float32)

    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    phase = 2 * np.pi * deviation_hz * np.cumsum(audio) / fs_iq
    iq = np.exp(1j * phase)

    return iq.astype(np.complex64)
