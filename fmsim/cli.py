import argparse

from fmsim.audio import load_audio
from fmsim.fm import fm_modulate
from fmsim.io import save_iq_npz
from fmsim.impairments import (
    add_awgn,
    add_frequency_offset,
    add_tone_jammer,
    add_iq_dropout
)
from fmsim.plots import plot_iq_time, plot_psd, plot_spectrogram

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser(description="FM Signal Simulator")
    
    parser.add_argument("input_wav", help="Input WAV audio file")
    parser.add_argument("--out", default="outputs/fm_iq_output.npz", help="Output IQ NPZ file")
    parser.add_argument("--mode", choices=["nbfm", "wbfm"], default="wbfm")
    parser.add_argument("--fs-iq", type=int, default=240_000)
    parser.add_argument("--deviation", type=float, default=None)

    parser.add_argument("--snr-db", type=float, default=None)
    parser.add_argument("--freq-offset", type=float, default=None)
    parser.add_argument("--tone-jammer-hz", type=float, default=None)
    parser.add_argument("--tone-jammer-power-db", type=float, default=-10.0)
    parser.add_argument("--dropout-start", type=float, default=None)
    parser.add_argument("--dropout-duration", type=float, default=0.0)
    parser.add_argument("--plots", action="store_true", help="Generate diagnostic plots")

    args = parser.parse_args()

    if args.deviation is None:
        deviation_hz = 75_000 if args.mode == "wbfm" else 5_000
    else:
        deviation_hz = args.deviation
    
    audio, fs = load_audio(args.input_wav, target_fs=args.fs_iq)

    iq = fm_modulate(
        audio=audio,
        fs_iq=fs,
        deviation_hz=deviation_hz
    )

    if args.snr_db is not None:
        iq = add_awgn(iq, snr_db=args.snr_db)

    if args.freq_offset != 0:
        iq = add_frequency_offset(iq, fs_iq=fs, offset_hz=args.freq_offset)

    if args.tone_jammer_hz is not None:
        iq = add_tone_jammer(
            iq,
            fs_iq=fs,
            jammer_freq_hz=args.tone_jammer_hz,
            jammer_power_db=args.tone_jammer_power_db
        )

    if args.dropout_start is not None and args.dropout_duration > 0:
        iq = add_iq_dropout(
            iq,
            fs_iq=fs,
            start_time_s=args.dropout_start,
            duration_s=args.dropout_duration
        )

    metadata = {
        "mode" : args.mode,
        "fs_iq" : fs,
        "deviation_hz" : deviation_hz,
        "snr_db" : args.snr_db,
        "freq_offset_hz" : args.freq_offset,
        "tone_jammer_hz" : args.tone_jammer_hz,
        "tone_jammer_power_db" : args.tone_jammer_power_db,
        "dropout_start_s" : args.dropout_start,
        "dropout_duration_s" : args.dropout_duration
    }

    save_iq_npz(args.out, iq, fs, metadata)

    print(f"Saved IQ File: {args.out}")
    print(f"Samples: {len(iq)}")
    print(f"sample rate: {fs} Hz")
    print(f"Mode: {args.mode}")
    print(f"Deviation {deviation_hz} Hz")

    if args.plots:
        plot_iq_time(iq, fs, save_path="outputs/cli_iq_time.png")
        plot_psd(iq, fs, save_path="outputs/cli_psd.png")
        plot_spectrogram(iq, fs, save_path="outputs/cli_spectrogram.png")
        plt.show()

if __name__ == "__main__":
    main()