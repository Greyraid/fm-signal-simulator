from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def plot_iq_time(iq: np.ndarray, fs_iq:int, seconds: float = 0.005, save_path: str | Path | None = None) -> None:
    
    num_samples = min(len(iq), int(seconds * fs_iq))
    t = np.arange(num_samples) / fs_iq

    plt.figure()
    plt.plot(t, np.real(iq[:num_samples]), label='I')
    plt.plot(t, np.imag(iq[:num_samples]), label='Q')
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.title("IQ Time Domain")
    plt.legend()
    plt.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")

    plt.close()

def plot_iq_constellation(iq: np.ndarray, save_path: Path | None = None) -> None:
    """Plot IQ constellation."""

    plt.figure()

    max_points = min(len(iq), 20_000)
    step = max(1, len(iq) // max_points)
    iq_plot = iq[::step][:max_points]

    plt.scatter(
        np.real(iq_plot),
        np.imag(iq_plot),
        s=1,
        alpha=0.35,
    )

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.title("IQ Constellation")
    plt.xlabel("In-phase (I)")
    plt.ylabel("Quadrature (Q)")
    plt.grid(True)
    plt.axis("equal")

    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    
    plt.close()

def plot_psd(iq: np.ndarray, fs_iq: int, save_path: str | Path | None = None) -> None:
    freqs,psd = signal.welch(
        iq,
        fs=fs_iq,
        nperseg=4096,
        return_onesided=False,
        scaling="density"
    )

    freqs = np.fft.fftshift(freqs)
    psd = np.fft.fftshift(psd)

    plt.figure()
    plt.plot(freqs / 1000, 10 * np.log10(psd + 1e-22))
    plt.xlabel("Frequency [kHz]")
    plt.ylabel("PSD [dB/Hz]")
    plt.title("FM IQ Power Spectral Density")
    plt.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches='tight')

    plt.close()

def plot_psd_comparison(iq_clean : np.ndarray, iq_impaired: np.ndarray, fs_iq: int, save_path: str | Path | None = None) -> None:
    """
    Plot clean and impaired IQ power spectral density on the same graph.
    """

    f_clean, psd_clean = signal.welch(
        iq_clean,
        fs=fs_iq,
        nperseg=2048,
        return_onesided=False
    )

    f_impaired, psd_impaired = signal.welch(
        iq_impaired,
        fs=fs_iq,
        nperseg=2048,
        return_onesided=False
    )

    f_clean = np.fft.fftshift(f_clean)
    psd_clean = np.fft.fftshift(psd_clean)

    f_impaired = np.fft.fftshift(f_impaired)
    psd_impaired = np.fft.fftshift(psd_impaired)

    plt.figure(figsize=(10, 5))

    plt.plot(f_clean / 1000, 10 * np.log10(psd_clean + 1e-12), label="Clean IQ")
    plt.plot(f_impaired / 1000, 10 * np.log10(psd_impaired + 1e-12), label="Impaired IQ")

    plt.title("PSD Comparison: Clean vs Impaired IQ")
    plt.xlabel("Frequency Offset (kHz)")
    plt.ylabel("Power Spectral Density (dB/Hz)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)

    plt.close()

def plot_spectrogram(iq: np.ndarray, fs_iq: int, save_path: str| Path | None = None) -> None:
    freqs, times, Sxx = signal.spectrogram(
        iq,
        fs=fs_iq,
        nperseg=1024,
        noverlap=768,
        return_onesided=False,
        scaling="density",
        mode="magnitude"
    )

    freqs = np.fft.fftshift(freqs)
    Sxx = np.fft.fftshift(Sxx, axes=0)

    plt.figure()
    plt.pcolormesh(times, freqs / 1000, 20 * np.log10(Sxx + 1e-12), shading='auto')
    plt.xlabel("Time [s]")
    plt.ylabel("Frequency [kHz]")
    plt.title("FM IQ Spectrogram")
    plt.colorbar(label="Magnitude [dB]")

    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches='tight')

    plt.close()

def plot_recovered_audio(
        audio: np.ndarray,
        fs_audio: int,
        start_time_s: float = 0.0,
        seconds: float = 0.25,
        save_path: str | Path | None = None
) -> None:
    """
    Plot a short section of recovered demodulated audio in the time domain.        
    """

    start_idx = int(start_time_s * fs_audio)
    end_idx = start_idx + int(seconds * fs_audio)

    start_idx = max(0, start_idx)
    end_idx = min(len(audio), end_idx)

    audio_segment = audio[start_idx:end_idx]
    t = np.arange(start_idx, end_idx) / fs_audio

    plt.figure(figsize=(10,4))
    plt.plot(t, audio_segment)
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.title(f"Recovered Audio Waveform ({seconds:.2f} s Window)")
    plt.grid(True)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")

    plt.close()
