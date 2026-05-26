# FM Signal Simulator

A Python-based FM signal simulator that converts `.wav` audio into complex IQ samples with configurable FM modulation and signal impairments.

This project is designed as a learning and research tool for digital signal processing, software-defined radio concepts, RF simulation, and future machine-learning-based signal recovery experiments.

## Current Version

**v0.2**

Version 0.2 expands the simulator with cleaner output handling, optional saved plots, optional IQ file export, saved run configuration, and additional SDR-style signal impairments.

## Signal Chain

```text
WAV audio
    ↓
Normalized / resampled audio
    ↓
FM IQ modulation
    ↓
Signal impairments
    ↓
FM demodulation
    ↓
Optional recovered WAV audio export
    ↓
Optional IQ file export
    ↓
Optional diagnostic plots
    ↓
Optional config JSON export
```

## Features

- Narrowband FM and wideband FM modulation
- Configurable IQ sample rate
- Configurable FM deviation
- Additive white Gaussian noise
- Frequency offset
- Tone jammer
- IQ dropout
- DC offset impairment
- IQ gain and phase imbalance impairment
- FM demodulation from IQ samples
- Optional recovered audio WAV export
- Optional IQ data saving
- Optional diagnostic plot saving
- Optional interactive plot display
- Optional run configuration export to JSON
- Organized output directory support
- Recovered audio path routing through `--output-dir`
- Cleaner terminal run summary

## Project Structure

```text
fm-signal-simulator/
  fmsim/
    audio.py
    cli.py
    demod.py
    fm.py
    impairments.py
    io.py
    plots.py
  examples/
    sample_audio.wav
  outputs/
  README.md
```

## Installation

Install the required Python packages:

```bash
pip install numpy scipy matplotlib
```

Or, if using a virtual environment on Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install numpy scipy matplotlib
```

## Basic Usage

Run the simulator from the project root folder:

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm
```

This runs a wideband FM simulation using the sample audio file.

By default, files are only saved when you use save options such as `--save-iq`, `--save-plots`, or `--save-config`.

## Example Commands

### Wideband FM

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm
```

### Narrowband FM

```bash
py -m fmsim.cli examples/sample_audio.wav --mode nbfm
```

### Add Noise

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20
```

### Add Frequency Offset

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --freq-offset 1000
```

### Add Tone Jammer

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --tone-jammer-hz 25000 --tone-jammer-power-db -10
```

### Add IQ Dropout

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --dropout-start 2 --dropout-duration 0.25
```

### Add DC Offset

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --dc-i 0.1 --dc-q 0.05
```

### Add IQ Imbalance

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --iq-gain-imbalance-db 3 --iq-phase-imbalance-deg 10
```

### Save IQ Data

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --save-iq --output-dir outputs/save_iq_test
```

This creates:

```text
outputs/save_iq_test/fm_iq_output.npz
```

### Save Diagnostic Plots

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --save-plots --output-dir outputs/plot_test
```

This creates:

```text
outputs/plot_test/iq_time.png
outputs/plot_test/psd.png
outputs/plot_test/spectrogram.png
```

### Show Plots

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --show-plots
```

### Save Configuration

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --save-config --output-dir outputs/config_test
```

This creates:

```text
outputs/config_test/config.json
```

### Save Recovered Audio

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --demod-output --output-dir outputs/demod_test
```

This creates:

```text
outputs/demod_test/recovered.wav
```

Save Recovered audio with a custom filename:

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --demod-output noisy_recovered.wav --output-dir outputs/demod_test
```

This creates:

```text
outputs/demod_test/noisy_recovered.wav
```

### Full Examples

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --freq-offset 1000 --tone-jammer-hz 25000 --tone-jammer-power-db -15 --dropout-start 2 --dropout-duration 0.25 --dc-i 0.05 --dc-q 0.02 --iq-gain-imbalance-db 2 --iq-phase-imbalance-deg 5 --save-iq --save-plots --save-config --output-dir outputs/full_test
```

Expected output:

```text
outputs/full_test/
  fm_iq_output.npz
  config.json
  iq_time.png
  psd.png
  spectrogram.png
```

## Command-Line Options

| Option | Description |
|---|---|
| `input_wav` | Input WAV audio file |
| `--mode` | FM mode: `wbfm` or `nbfm` |
| `--fs-iq` | IQ sample rate |
| `--deviation` | Custom FM deviation in Hz |
| `--snr-db` | Signal-to-noise ratio in dB |
| `--freq-offset` | Frequency offset in Hz |
| `--tone-jammer-hz` | Tone jammer frequency in Hz |
| `--tone-jammer-power-db` | Tone jammer power in dB |
| `--dropout-start` | Dropout start time in seconds |
| `--dropout-duration` | Dropout duration in seconds |
| `--dc-i` | DC offset added to I channel |
| `--dc-q` | DC offset added to Q channel |
| `--iq-gain-imbalance-db` | Q-channel gain imbalance in dB |
| `--iq-phase-imbalance-deg` | IQ phase imbalance in degrees |
| `--demod-output` | Save demodulated recovered audio as a `.wav` file |
| `--output-dir` | Directory for saved output files |
| `--save-iq` | Save IQ data as `.npz` |
| `--save-plots` | Save diagnostic plots |
| `--show-plots` | Display diagnostic plots |
| `--save-config` | Save run configuration as JSON |


## Example Plots

To generate example plots for this README, run:

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --freq-offset 1000 --dc-i 0.05 --dc-q 0.02 --iq-gain-imbalance-db 2 --iq-phase-imbalance-deg 5 --save-plots --save-config --output-dir outputs/readme_demo
```

After running that command, the following files should be created:

```text
outputs/readme_demo/iq_time.png
outputs/readme_demo/psd.png
outputs/readme_demo/spectrogram.png
outputs/readme_demo/config.json
```

## Version History

### v0.3

- Fixed metadata handling bug in `io.py`
- Added `--demod-output`
- Added FM demodulation from IQ samples
- Added recovered audio WAV export
- Added recovered audio output path routing
- Improved terminal run summary

### v0.2

- Added `--output-dir`
- Added `--save-plots`
- Added `--show-plots`
- Added `--save-iq`
- Added `--save-config`
- Added DC offset impairment
- Added IQ gain and phase imbalance impairment
- Improved output organization

### v0.1

- First working FM signal simulation chain
- WAV audio loading
- Audio normalization and resampling
- FM IQ modulation
- Basic signal impairments
- IQ file saving
- Diagnostic plots

## Project Goals

This project is intended to build practical experience with:

- Digital signal processing
- FM modulation
- SDR-style IQ data
- RF signal impairments
- Python-based simulation
- Signal visualization
- Future machine-learning-based signal recovery experiments