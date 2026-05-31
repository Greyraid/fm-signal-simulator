import argparse
from pathlib import Path

from fmsim.simulation import SimulationConfig, run_simulation

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

    config = SimulationConfig(
        input_wav=Path(args.input_wav),
        output_dir=args.output_dir,
        mode=args.mode,
        fs_iq=args.fs_iq,
        deviation=args.deviation,
        snr_db=args.snr_db,
        freq_offset=args.freq_offset,
        tone_jammer_hz=args.tone_jammer_hz,
        tone_jammer_power_db=args.tone_jammer_power_db,
        dropout_start=args.dropout_start,
        dropout_duration=args.dropout_duration,
        dc_i=args.dc_i,
        dc_q=args.dc_q,
        iq_gain_imbalance_db=args.iq_gain_imbalance_db,
        iq_phase_imbalance_deg=args.iq_phase_imbalance_deg,
        seed=args.seed,
        demod_output=Path(args.demod_output) if args.demod_output is not None else None,
        save_iq=args.save_iq,
        save_config=args.save_config,
        save_plots=args.save_plots,
        show_plots=args.show_plots
    )

    result = run_simulation(config)

    # Print run summary
    # ==================================
    print()
    print("FM Signal Simulator Run Complete")
    print("----------------------------------")
    print(f"Input WAV:      {result.input_wav}")
    print(f"Mode:           {result.mode}")
    print(f"Sample Rate:    {result.fs_iq} Hz")
    print(f"Samples:        {result.samples}")
    print(f"Duration:       {result.duration_s:.2f} seconds")
    print(f"Deviation:      {result.deviation_hz} Hz")
    print(f"Seed:           {config.seed if config.seed is not None else 'None'}")

    # Print impairment details
    # ==================================
    print()
    print("Impairments")
    print("-----------")

    if config.snr_db is not None:
        print(f"AWGN SNR:           {config.snr_db} dB")
    else:
        print("AWGN SNR:            None")

    if config.freq_offset is not None and config.freq_offset != 0:
        print(f"Frequency Offset:   {config.freq_offset} Hz")
    else:
        print("Frequency Offset:    None")

    if config.tone_jammer_hz is not None:
        print(f"Tone Jammer:        {config.tone_jammer_hz} Hz at {config.tone_jammer_power_db} dB")
    else:
        print("Tone Jammer:         None")

    if config.dropout_start is not None and config.dropout_duration > 0:
        print(f"Dropout:            starts at {config.dropout_start}s for {config.dropout_duration}s")
    else:
        print("Dropout:             None")

    if config.dc_i != 0.0 or config.dc_q != 0.0:
        print(f"DC Offset:          I={config.dc_i}, Q={config.dc_q}")
    else:
        print("DC Offset:           None")

    if config.iq_gain_imbalance_db != 0.0 or config.iq_phase_imbalance_deg != 0.0:
        print(f"IQ Imbalance:       gain={config.iq_gain_imbalance_db} dB, phase={config.iq_phase_imbalance_deg} deg")
    else:
        print("IQ Imbalance:        None")

    # Print output details
    #==========================
    print()
    print("Outputs")
    print("--------")

    if result.iq_path is not None:
        print(f"IQ File:            {result.iq_path}")

    if result.config_path is not None:
        print(f"Config File:        {result.config_path}")

    if result.demod_audio_path is not None:
        print(f"Recovered Audio:    {result.demod_audio_path}")

    if result.plot_paths:
        print(f"Plots Folder:       {result.output_dir}")

    if (
        result.iq_path is None
        and result.config_path is None
        and result.demod_audio_path is None
        and not result.plot_paths
    ):
        print("No files saved.")

if __name__ == "__main__":
    main()