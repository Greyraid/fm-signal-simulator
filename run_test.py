import numpy as np
import os
import matplotlib.pyplot as plt

from fmsim import (
    load_audio,
    fm_modulate,
    save_iq_npz,
    add_awgn,
    add_frequency_offset,
    add_tone_jammer,
    add_iq_dropout
)

from fmsim.plots import plot_iq_time, plot_psd, plot_spectrogram #importing ploting functions

os.makedirs("outputs", exist_ok=True)

audio, fs = load_audio("examples/sample_audio.wav", target_fs=240_000)

iq_clean = fm_modulate(
    audio=audio,
    fs_iq=fs,
    deviation_hz=75_000)

iq_impaired = add_awgn(iq_clean, snr_db=20, seed=0)
iq_impaired = add_frequency_offset(iq_impaired, fs_iq=fs, offset_hz=1_000)
iq_impaired = add_tone_jammer(
    iq_impaired,
    fs_iq=fs,
    jammer_freq_hz=25_000,
    jammer_power_db=-10
)
iq_impaired = add_iq_dropout(
    iq_impaired,
    fs_iq=fs,
    start_time_s=2.0,
    duration_s=0.25
)

save_iq_npz(
    "outputs/fm_iq_impaired.npz",
    iq=iq_impaired,
    fs_iq=fs,
    metadata={
        "mode" : "wbfm",
        "deviation_hz" : 75_000,
        "snr_hz" : 20,
        "frequency_offset_hz" : 1_000,
        "tone_jammer_hz" : 25_000,
        "tone_jammer_power_db" : -10,
        "dropout_start_s" : 2.0,
        "dropout_duration_s" : 0.25
                    }
)

print("FM IQ file created")
print(f"Audio samples: {len(audio)}")
print(f"IQ samples: {len(iq_impaired)}")
print(f"IQ sample rate: {fs} Hz")

plot_iq_time(iq_impaired, fs, save_path="outputs/iq_time.png")
plot_psd(iq_impaired, fs, save_path="outputs/psd.png")
plot_spectrogram(iq_impaired, fs, save_path="outputs/spectrogram.png")

plt.show()
