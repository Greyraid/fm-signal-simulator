from dataclasses import dataclass, field
from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np

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
    plot_iq_constellation,
    plot_psd,
    plot_spectrogram,
    plot_psd_comparison,
    plot_recovered_audio
)

@dataclass
class SimulationConfig:
    input_wav: Path
    output_dir: Path

    mode: str = "wbfm"
    fs_iq: int = 240_000
    deviation: float | None = None    
    
    snr_db: float | None = None
    freq_offset: float | None = None
    tone_jammer_hz: float | None = None
    tone_jammer_power_db: float = -10.0
    dropout_start: float | None = None
    dropout_duration: float = 0.0
    
    dc_i: float = 0.0
    dc_q: float = 0.0
    iq_gain_imbalance_db: float = 0.0
    iq_phase_imbalance_deg: float = 0.0

    seed: int | None = None
    
    demod_output: Path | None = None
    save_iq: bool = False
    save_config: bool = False
    save_plots: bool = False
    show_plots: bool = False

@dataclass
class SimulationResult:
    output_dir: Path
    input_wav: Path
    mode: str
    fs_iq: int
    samples: int
    duration_s: float
    deviation_hz: float
    metadata: dict

    iq_clean: np.ndarray
    iq_impaired: np.ndarray
    recovered_audio: np.ndarray | None = None
    fs_audio: int | None = None

    iq_path: Path | None = None
    config_path: Path | None = None
    demod_audio_path: Path | None = None
    plot_paths: list[Path] = field(default_factory=list)

def run_simulation(config: SimulationConfig) -> SimulationResult:
    """
    Main simulation pipeline used by both the CLI and GUI
    """
    if config.deviation is None:
        deviation_hz = 75_000 if config.mode == "wbfm" else 5_000
    else:
        deviation_hz = config.deviation

    audio, fs = load_audio(config.input_wav, target_fs=config.fs_iq)

    iq = fm_modulate(
        audio=audio,
        fs_iq=fs,
        deviation_hz=deviation_hz
    )

    iq_clean = iq.copy()

    if config.snr_db is not None:
        iq = add_awgn(iq, snr_db=config.snr_db, seed=config.seed)

    if config.freq_offset is not None and config.freq_offset != 0:
        iq = add_frequency_offset(iq, fs_iq=fs, offset_hz=config.freq_offset)

    if config.tone_jammer_hz is not None:
        iq = add_tone_jammer(
            iq,
            fs_iq=fs,
            jammer_freq_hz=config.tone_jammer_hz,
            jammer_power_db=config.tone_jammer_power_db
        )
    
    if config.dropout_start is not None and config.dropout_duration > 0:
        iq = add_iq_dropout(
            iq,
            fs_iq=fs,
            start_time_s=config.dropout_start,
            duration_s=config.dropout_duration
        )

    if config.dc_i != 0.0 or config.dc_q != 0.0:
        iq = add_dc_offset(iq, dc_i=config.dc_i, dc_q=config.dc_q)

    if config.iq_gain_imbalance_db != 0.0 or config.iq_phase_imbalance_deg != 0.0:
        iq = add_iq_imbalance(
            iq,
            gain_imbalance_db=config.iq_gain_imbalance_db,
            phase_imbalance_deg=config.iq_phase_imbalance_deg
        )

    metadata = {
        "mode": config.mode,
        "fs_iq": fs,
        "deviation_hz" : deviation_hz,
        "snr_db": config.snr_db,
        "seed": config.seed,
        "freq_offset_hz": config.freq_offset,
        "tone_jammer_hz": config.tone_jammer_hz,
        "tone_jammer_power_db": config.tone_jammer_power_db,
        "dropout_start_s": config.dropout_start,
        "dropout_duration_s": config.dropout_duration,
        "dc_i": config.dc_i,
        "dc_q": config.dc_q,
        "iq_gain_imbalance_db": config.iq_gain_imbalance_db,
        "iq_phase_imbalance_deg": config.iq_phase_imbalance_deg
    }

    should_make_output_dir = (
        config.save_iq
        or config.save_config
        or config.save_plots
        or config.demod_output is not None
    )

    if should_make_output_dir:
        config.output_dir.mkdir(parents=True, exist_ok=True)

    demod_audio = fm_demod(iq)
    demod_audio = normalize_audio(demod_audio)
    
    demod_output_path = None

    if config.demod_output is not None:
        demod_output_path = Path(config.demod_output)

        if demod_output_path.parent == Path("."):
            demod_output_path = config.output_dir / demod_output_path
        
        demod_output_path.parent.mkdir(parents=True, exist_ok=True)
        save_audio_wav(demod_output_path, demod_audio, fs)

    config_path = None

    if config.save_config:
        config_path = config.output_dir / "config.json"

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

    iq_path = None

    if config.save_iq:
        iq_path = config.output_dir / "fm_iq_output.npz"
        save_iq_npz(iq_path, iq, fs, metadata)

    plot_paths: list[Path] = []

    if config.save_plots or config.show_plots:
        iq_time_path = config.output_dir / "iq_time.png"
        iq_constellation_path = config.output_dir / "iq_constellation.png"
        psd_path = config.output_dir / "psd.png"
        spectrogram_path = config.output_dir / "spectrogram.png"
        psd_comparison_path = config.output_dir / "psd_comparison.png"
        recovered_audio_path = config.output_dir / "recovered_audio.png"

        plot_iq_time(
            iq,
            fs,
            save_path=iq_time_path if config.save_plots else None
        )

        plot_iq_constellation(
            iq,
            save_path=iq_constellation_path if config.save_plots else None
        )

        plot_psd(
            iq, fs, save_path=psd_path if config.save_plots else None
        )

        plot_spectrogram(
            iq,
            fs,
            save_path=spectrogram_path if config.save_plots else None
        )

        plot_psd_comparison(
            iq_clean=iq_clean,
            iq_impaired=iq,
            fs_iq=fs,
            save_path=psd_comparison_path if config.save_plots else None
        )

        plot_recovered_audio(
            audio=demod_audio,
            fs_audio=fs,
            save_path=recovered_audio_path if config.save_plots else None
        )

        if config.save_plots:
            plot_paths.extend(
                [
                    iq_time_path,
                    iq_constellation_path,
                    psd_path,
                    spectrogram_path,
                    psd_comparison_path,
                    recovered_audio_path
                ]
            )
        
        if config.show_plots:
            plt.show()
        else:
            plt.close("all")
        
    return SimulationResult(
        output_dir=config.output_dir,
        input_wav=config.input_wav,
        mode=config.mode,
        fs_iq=fs,
        samples=len(iq),
        duration_s=len(iq) / fs,
        deviation_hz=deviation_hz,
        metadata=metadata,
        iq_clean=iq_clean,
        iq_impaired=iq,
        recovered_audio=demod_audio,
        fs_audio=fs,
        iq_path=iq_path,
        config_path=config_path,
        demod_audio_path=demod_output_path,
        plot_paths=plot_paths
    )