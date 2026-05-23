import numpy as np

def add_awgn(iq: np.ndarray, snr_db: float, seed: int | None = None) -> np.ndarray:
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
    n = np.arange(len(iq))
    rotator = np.exp(1j * 2 * np.pi * offset_hz * n / fs_iq)

    return (iq * rotator).astype(np.complex64)

def add_tone_jammer(
        iq: np.ndarray,
        fs_iq: int,
        jammer_freq_hz: float,
        jammer_power_db: float
) -> np.ndarray:
    n = np.ndarray(len(iq))

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

    impaired = iq.copy()

    start_idx = int(start_time_s * fs_iq)
    end_idx = int((start_time_s + duration_s) * fs_iq)

    start_idx = max(0, start_idx)
    end_idx = min(len(iq), end_idx)

    impaired[start_idx:end_idx] = 0

    return impaired.astype(np.complex64)

def clip_iq(iq: np.ndarray, clip_level: float = 1.0) -> np.ndarray:
    real = np.clip(np.real(iq), -clip_level, clip_level)
    imag = np.clip(np.imag(iq), -clip_level, clip_level)

    return (real + 1j * imag).astype(np.complex64)


