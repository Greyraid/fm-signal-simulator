import argparse
from pathlib import Path
import json

from fmsim.audio import load_audio, save_audio_wav
from fmsim.demod import fm_demod, normalize_audio
from fmsim.fm import fm_modulate
from fmsim.io import save_iq_npz
from fmsim.impairments import (
    add_awgn,
    add_frequency_offset,
    add_tone_jammer,
    add_iq_dropout,
    add_dc_offset,
    add_iq_imbalance
)
from fmsim.plots import (
    plot_iq_time, 
    plot_psd, 
    plot_spectrogram,
    plot_psd_comparison,
    plot_recovered_audio
)

import matplotlib.pyplot as plt


def main() -> None:

    # Build command-line interface
    parser = argparse.ArgumentParser(description="FM Signal Simulator")
    
    parser.add_argument("input_wav", help="Input WAV audio file")
    parser.add_argument("--mode", choices=["nbfm", "wbfm"], default="wbfm")
    parser.add_argument("--fs-iq", type=int, default=240_000)
    parser.add_argument("--deviation", type=float, default=None)

    parser.add_argument("--snr-db", type=float, default=None)
    parser.add_argument("--freq-offset", type=float, default=None)
    parser.add_argument("--tone-jammer-hz", type=float, default=None)
    parser.add_argument("--tone-jammer-power-db", type=float, default=-10.0)
    parser.add_argument("--dropout-start", type=float, default=None)
    parser.add_argument("--dropout-duration", type=float, default=0.0)
    parser.add_argument("--dc-i", type=float, default=0.0, help="DC offset to I channel")
    parser.add_argument("--dc-q", type=float, default=0.0, help="DC offset added to Q channel")
    parser.add_argument("--iq-gain-imbalance-db", type=float, default=0.0, help="Q-channel gain imbalance in dB relative to I")
    parser.add_argument("--iq-phase-imbalance-deg", type=float, default=0.0, help="IQ phase imbalance in degrees")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for repeatable noise/jammer generation")
    parser.add_argument("--demod-output", nargs="?", const="recovered.wav", default=None, help="Save demodulated audio to a WAV file. Defaults to recovered.wav inside output-dir")
    parser.add_argument("--save-iq", action="store_true", help="Save simulated IQ data to the output directory")
    parser.add_argument("--save-config", action="store_true", help="Save run configuration metadata to the output directory")
    parser.add_argument("--save-plots", action="store_true", help="Save plots to the output directory")
    parser.add_argument("--show-plots", action="store_true", help="Display diagnostic plots in windows")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Directory where output files will be saved")

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

    # Clean copy of samples with no impairments
    iq_clean = iq.copy()

    if args.snr_db is not None:
        iq = add_awgn(iq, snr_db=args.snr_db, seed=args.seed)

    if args.freq_offset is not None and args.freq_offset != 0:
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

    if args.dc_i != 0.0 or args.dc_q != 0.0:
        iq = add_dc_offset(iq, dc_i=args.dc_i, dc_q=args.dc_q)

    if args.iq_gain_imbalance_db != 0.0 or args.iq_phase_imbalance_deg != 0.0:
        iq = add_iq_imbalance(iq, 
            gain_imbalance_db=args.iq_gain_imbalance_db,
            phase_imbalance_deg=args.iq_phase_imbalance_deg
        )

    demod_audio = None

    if args.demod_output is not None or args.save_plots or args.show_plots:
        demod_audio = fm_demod(iq)
        demod_audio = normalize_audio(demod_audio)

    if args.demod_output is not None:
        demod_output_path = Path(args.demod_output)

        # Save inside output-dir unless the user provided a folder/path
        if demod_output_path.parent == Path("."):
            demod_output_path = args.output_dir / demod_output_path

        demod_output_path.parent.mkdir(parents=True, exist_ok=True)

        save_audio_wav(demod_output_path, demod_audio, fs)

    metadata = {
        "mode" : args.mode,
        "fs_iq" : fs,
        "deviation_hz" : deviation_hz,
        "snr_db" : args.snr_db,
        "seed" : args.seed,
        "freq_offset_hz" : args.freq_offset,
        "tone_jammer_hz" : args.tone_jammer_hz,
        "tone_jammer_power_db" : args.tone_jammer_power_db,
        "dropout_start_s" : args.dropout_start,
        "dropout_duration_s" : args.dropout_duration,
        "dc_i" : args.dc_i,
        "dc_q" : args.dc_q,
        "iq_gain_imbalance_db" : args.iq_gain_imbalance_db,
        "iq_phase_imbalance_deg" : args.iq_phase_imbalance_deg
    }

    if args.save_iq or args.save_plots or args.save_config or args.demod_output is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.save_config:
        config_path = args.output_dir / "config.json"

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

    if args.save_iq:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output_iq_path = args.output_dir / "fm_iq_output.npz"
        save_iq_npz(output_iq_path, iq, fs, metadata)

    # Print run summary
    # ==================================
    print()
    print("FM Signal Simulator Run Complete")
    print("----------------------------------")
    print(f"Input WAV:      {args.input_wav}")
    print(f"Mode:           {args.mode}")
    print(f"Sample Rate:    {fs} Hz")
    print(f"Samples:        {len(iq)}")
    print(f"Duration:       {len(iq) / fs:.2f} seconds")
    print(f"Deviation:      {deviation_hz} Hz")
    print(f"Seed:           {args.seed if args.seed is not None else 'None'}")

    # Print impairment details
    # ==================================
    print()
    print("Impairments")
    print("-----------")

    if args.snr_db is not None:
        print(f"AWGN SNR:           {args.snr_db} dB")
    else:
        print("AWGN SNR:            None")

    if args.freq_offset is not None and args.freq_offset != 0:
        print(f"Frequency Offset:   {args.freq_offset} Hz")
    else:
        print("Frequency Offset:    None")

    if args.tone_jammer_hz is not None:
        print(f"Tone Jammer:        {args.tone_jammer_hz} Hz at {args.tone_jammer_power_db} dB")
    else:
        print("Tone Jammer:         None")

    if args.dropout_start is not None and args.dropout_duration > 0:
        print(f"Dropout:            starts at {args.dropout_start}s for {args.dropout_duration}s")
    else:
        print("Dropout:             None")

    if args.dc_i != 0.0 or args.dc_q != 0.0:
        print(f"DC Offset:          I={args.dc_i}, Q={args.dc_q}")
    else:
        print("DC Offset:           None")

    if args.iq_gain_imbalance_db != 0.0 or args.iq_phase_imbalance_deg != 0.0:
        print(f"IQ Imbalance:       gain={args.iq_gain_imbalance_db} dB, phase={args.iq_phase_imbalance_deg} deg")
    else:
        print("IQ Imbalance:        None")
 
    if args.save_plots or args.show_plots:
        iq_time_path = args.output_dir / "iq_time.png"
        psd_path = args.output_dir / "psd.png"
        spectrogram_path = args.output_dir / "spectrogram.png"
        psd_comparison_path = args.output_dir / "psd_comparison.png"
        recovered_audio_path = args.output_dir / "recovered_audio.png"

        save_path_iq_time = iq_time_path if args.save_plots else None
        save_path_psd = psd_path if args.save_plots else None
        save_path_spectrogram = spectrogram_path if args.save_plots else None
        save_path_psd_comparison = psd_comparison_path if args.save_plots else None
        save_path_recovered_audio = recovered_audio_path if args.save_plots else None

        plot_iq_time(iq, fs, save_path=save_path_iq_time)
        plot_psd(iq, fs, save_path=save_path_psd)
        plot_spectrogram(iq, fs, save_path=save_path_spectrogram)
        plot_psd_comparison(iq_clean=iq_clean, iq_impaired=iq, fs_iq=fs, save_path=save_path_psd_comparison)
        plot_recovered_audio(audio=demod_audio, fs_audio=fs, save_path=save_path_recovered_audio)

        if args.show_plots:
            plt.show()
        else:
            plt.close("all")

    # Print output details
    #==========================
    print()
    print("Outputs")
    print("--------")

    if args.save_iq:
        print(f"IQ File:            {output_iq_path}")

    if args.save_config:
        print(f"Config File:        {config_path}")

    if args.demod_output is not None:
        print(f"Recovered Audio:    {demod_output_path}")

    if args.save_plots:
        print(f"Plots Folder:       {args.output_dir}")

    if not args.save_iq and not args.save_config and args.demod_output is None and not args.save_plots:
        print("No files saved.")

if __name__ == "__main__":
    main()