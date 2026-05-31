# FM Signal Simulator

A Python-based FM signal simulator that converts `.wav` audio into complex IQ samples with configurable FM modulation and signal impairments.

This project is designed as a learning and research tool for digital signal processing, software-defined radio concepts, RF simulation, and future machine-learning-based signal recovery experiments.

## Current Version

**v0.5**

Version 0.5 introduces the first desktop graphical user interface for the FM Signal Simulator. The simulation pipeline has been refactored into a shared backend in `simulation.py`, allowing both the command-line interface and the new PySide6 GUI to run the same FM simulation process.

The GUI provides controls for FM mode selection, signal impairments, random seed selection, output file generation, and output folder selection. This release is an important step toward the long-term goal of packaging the simulator as a standalone Windows application.

## Signal Chain

```text
WAV audio
    ↓
GUI or command-line configuration
    ↓
Shared simulation backend
    ↓
Normalized / resampled audio
    ↓
FM IQ modulation
    ↓
Clean IQ copy saved for comparison
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
- Repeatable AWGN noise generation with `--seed`
- Clean vs impaired IQ PSD comparison plot
- Recovered audio snippet plot
- PySide6 desktop graphical user interface
- Shared simulation backend used by both the CLI and GUI
- Input WAV file selection through the GUI
- Output folder selection through the GUI
- Scrollable GUI control layout

## Project Structure

```text
fm-signal-simulator/
  fmsim/
    audio.py
    cli.py
    demod.py
    fm.py
    gui.py
    impairments.py
    io.py
    plots.py
    simulation.py
  examples/
    sample_audio.wav
  outputs/
  README.md
```

## Installation

Install the required Python packages:

```bash
py -m pip install numpy scipy matplotlib PySide6
```

Or, if using a virtual environment on Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
py -m pip install numpy scipy matplotlib PySide6
```

## GUI Usage

Launch the desktop graphical user interface from the project root folder:

```bash
py -m fmsim.gui
```

The GUI allows the user to:

- Select an input `.wav` audio file
- Select an output folder
- Choose WBFM or NBFM modulation
- Configure AWGN, frequency offset, tone jammer, IQ dropout, DC offset, and IQ imbalance
- Select a repeatable random seed
- Save recovered audio, IQ samples, diagnostic plots  and simulation configuration data

The GUI currently saves results to the selected output folder. Future versions are planned to add improved plot viewing and standalone Windows executable packaging.

## Command-Line Usage

Run the simulator from the project root folder:

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm```

This runs a wideband FM simulation using the sameple audio file.

By default, files are only saved when using options such as `--save-iq`, `--save-plots`, `--save-config`, or `--demod-output`.

## Example CLI Commands

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

### Seed

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --seed 123
```

Using the same seed with the same settings produces the same AWGN noise sequence.

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
outputs/plot_test/psd_comparison.png
outputs/plot_test/spectrogram.png
outputs/plot_test/recovered_audio.png
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
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --seed 123 --freq-offset 1000 --tone-jammer-hz 25000 --tone-jammer-power-db -15 --dropout-start 2 --dropout-duration 0.25 --dc-i 0.05 --dc-q 0.02 --iq-gain-imbalance-db 2 --iq-phase-imbalance-deg 5 --save-iq --save-plots --save-config --demod-output --output-dir outputs/full_test
```

Expected output:

```text
outputs/full_test/
  fm_iq_output.npz
  config.json
  iq_time.png
  psd.png
  psd_comparison.png
  spectrogram.png
  recovered_audio.png
  recovered.wav
```

## Command-Line Options

| Option | Description |
|---|---|
| `input_wav` | Input WAV audio file |
| `--mode` | FM mode: `wbfm` or `nbfm` |
| `--fs-iq` | IQ sample rate |
| `--deviation` | Custom FM deviation in Hz |
| `--snr-db` | Signal-to-noise ratio in dB |
| `--seed` | Random seed for repeatable AWGN noise generation |
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
py -m fmsim.cli examples/sample_audio.wav --mode wbfm --snr-db 20 --seed 123 --freq-offset 1000 --tone-jammer-hz 25000 --tone-jammer-power-db -10 --dc-i 0.05 --dc-q 0.02 --iq-gain-imbalance-db 2 --iq-phase-imbalance-deg 5 --save-plots --save-config --demod-output --output-dir outputs/readme_demo
```

After running that command, the following files should be created:

```text
outputs/readme_demo/iq_time.png
outputs/readme_demo/psd.png
outputs/readme_demo/psd_comparison.png
outputs/readme_demo/spectrogram.png
outputs/readme_demo/recovered_audio.png
outputs/readme_demo/recovered.wav
outputs/readme_demo/config.json
```

## Version History

### v0.5
- Refactored the simulation pipeline into `simulation.py`
- Maintained CLI functionality through the shared simulation backend
- Added a PySide6 desktop GUI
- Added input WAV file selection
- Added output folder selection
- Added GUI controls for:
  - WBFM / NBFM mode
  - AWGN
  - Frequency offset
  - Tone jammer frequency and power
  - IQ dropout
  - DC offset
  - IQ gain and phase imbalance
  - Random seed
- Added GUI output options for:
  - Saved IQ data
  - Diagnostic plots
  - Recovered audio
  - Configuration metadata
- Added a scrollable GUI layout

### v0.4
- Added `--seed` for repeatable AWGN noise generation
- Added clean IQ preservation before impairments
- Added clean vs impaired IQ PSD comparison plot
- Added recovered audio snippet plot
- Fixed tone jammer power dB terminal output
- Fixed minor spelling and terminal output issues

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