import numpy as np

def add_awgn(iq: np.ndarray, snr_db: float, seed: int | None = None) -> np.ndarray:
    '''
    Add complex additive white Gaussian noise to IQ samples.

    The noise power is calculated from the measured signal power and the requested signal to noise ration in dB
    '''
    rng = np.random.default_rng(seed)

    signal_power = np.mean(np.abs(iq) ** 2)
    snr_linear = 10 ** (snr_db / 10)
    noise_power = signal_power / snr_linear

    noise_std = np.sqrt(noise_power / 2)

    noise = noise_std * (
        rng.normal(size=len(iq)) + 1j * rng.normal(size=len(iq))
    )

    return (iq + noise).astype(np.complex64)

def add_frequency_offset(iq: np.ndarray, fs_iq: int, offset_hz: float) -> np.ndarray:
    '''
    Shift the IQ signal in frequency by mixing it with a complex sinusoid.

    Positive offset_hz moves the signal up in frequency. Negative offset_hz moves it down in frequency
    '''  
    n = np.arange(len(iq))
    rotator = np.exp(1j * 2 * np.pi * offset_hz * n / fs_iq)

    return (iq * rotator).astype(np.complex64)

def add_tone_jammer(
        iq: np.ndarray,
        fs_iq: int,
        jammer_freq_hz: float,
        jammer_power_db: float
) -> np.ndarray:
    '''
    Add a single complex tone jammer to the IQ signal.

    jammer_freq_hz sets the jammer frequency offset from center.
    jammer_power_db sets jammer power relative to the signal power.
    '''

    n = np.arange(len(iq))

    signal_power = np.mean(np.abs(iq) ** 2)
    jammer_power = signal_power * 10 ** (jammer_power_db / 10)
    jammer_amp = np.sqrt(jammer_power)

    jammer = jammer_amp * np.exp(1j * 2 * np.pi * jammer_freq_hz * n / fs_iq)

    return (iq + jammer).astype(np.complex64)

def add_iq_dropout(
        iq: np.ndarray,
        fs_iq: int,
        start_time_s: float,
        duration_s: float
) -> np.ndarray: 
    '''
    Zero out a section of IQ samples to simulate a signal loss or dropout

    start_time_s sets when the dropout begins.
    duration_s sets how long the dropout lasts.
    '''
    impaired = iq.copy()

    start_idx = int(start_time_s * fs_iq)
    end_idx = int((start_time_s + duration_s) * fs_iq)

    start_idx = max(0, start_idx)
    end_idx = min(len(iq), end_idx)

    impaired[start_idx:end_idx] = 0

    return impaired.astype(np.complex64)

def clip_iq(iq: np.ndarray, clip_level: float = 1.0) -> np.ndarray:
    '''
    Limit the I and Q sample amplitude to simulate receiver or ADC clipping.

    clip_level sets the maximum position and negative value allowed for each channel.
    '''
    real = np.clip(np.real(iq), -clip_level, clip_level)
    imag = np.clip(np.imag(iq), -clip_level, clip_level)

    return (real + 1j * imag).astype(np.complex64)

def add_dc_offset(iq: np.ndarray, dc_i: float = 0.0, dc_q: float = 0.0) -> np.ndarray:
    '''
    Add DC offset to IQ samples.

    dc_i shifts the real/I channel.
    dc_q shifts the imaginary/Q channel.
    '''
    offset = dc_i + 1j * dc_q
    return (iq + offset).astype(np.complex64)

def add_iq_imbalance(iq: np.ndarray, gain_imbalance_db: float = 0.0, phase_imbalance_deg: float = 0.0) -> np.ndarray:
    '''
    Add IQ gain and phase imbalance.

    gain_imbalance_db changes the Q-channel gain relative to I.
    phase_imbanlence_deg mixes I into G to simulate quadrature phase error.
    '''

    i = np.real(iq)
    q = np.imag(iq)

    gain_linear = 10 ** (gain_imbalance_db / 20)
    phase_rad = np.deg2rad(phase_imbalance_deg)

    q_imbalanced = gain_linear * (q * np.cos(phase_rad) + i * np.sin(phase_rad))

    return (i + 1j * q_imbalanced).astype(np.complex64)


