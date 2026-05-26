import numpy as np

def fm_demod(iq: np.ndarray) -> np.ndarray:
    '''
    Demodulate an FM IQ signal using phase diference.

    iq is an array of Complex IQ samples.
    '''

    if len(iq) < 2:
        raise ValueError("IQ ignal must contain at least 2 samples.")
    
    demodulated = np.angle(iq[1:] * np.conj(iq[:-1]))

    return demodulated.astype(np.float32)

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    '''
    Normalize audio to the range [-1, 1]
    '''
    max_val = np.max(np.abs(audio))

    if max_val == 0:
        return audio.astype(np.float32)
    
    return (audio / max_val).astype(np.float32)