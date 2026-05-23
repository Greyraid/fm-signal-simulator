import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def plot_iq_time(iq: np.ndarray, fs_iq:int, seconds: float = 0.005, save_path: str | None = None) -> None:
    num_samples = int(seconds * fs_iq)
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

def plot_psd(iq: np.ndarray, fs_iq: int, save_path: str | None = None) -> None:
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

def plot_spectrogram(iq: np.ndarray, fs_iq: int, save_path: str | None = None) -> None:
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


