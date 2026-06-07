# FM Signal Simulator

A Python-based FM signal simulator that converts `.wav` audio into complex IQ samples with configurable FM modulation and signal impairments.

This project is designed as a learning and research tool for digital signal processing, software-defined radio concepts, RF simulation, and future machine-learning-based signal recovery experiments.

## Current Version

**v0.7**

Version 0.7 focuses on integrated GUI plot viewing and improved signal analysis tools.

The GUI now displays simulation results directly inside the main application window using a tabbed plot workspace. Integrated plots include IQ time-domain, IQ constellation, clean vs impaired PSD comparison, spectrogram, and recovered audio waveform views.

This release also adds scrollable time-window controls for the IQ time-domain and recovered audio plots, allowing the user to inspect different parts of the signal without plotting the entire waveform at once. A plot appearance menu was also added so the user can change the plot background color from the Tools menu.

The GUI has also been refactored into smaller files for better readability and maintainability.

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

* Narrowband FM and wideband FM modulation
* Configurable IQ sample rate and FM deviation
* Shared simulation backend for both CLI and GUI use
* Signal impairments including AWGN, frequency offset, tone jammer, IQ dropout, DC offset, and IQ gain/phase imbalance
* Repeatable AWGN noise generation with `--seed`
* FM demodulation with optional recovered WAV audio export
* Optional IQ data, diagnostic plot, and configuration JSON saving
* Organized output directory support
* PySide6 desktop GUI using a `QMainWindow` engineering-tool layout
* Top menu bar, toolbar shortcuts, dockable Simulation Settings panel, and status bar
* Background-threaded simulation execution to keep the GUI responsive
* Integrated tabbed plot workspace in the GUI
* GUI plot tabs for IQ Time, IQ Constellation, PSD Comparison, Spectrogram, and Recovered Audio
* Scrollable time-window controls for IQ Time and Recovered Audio plots
* Adjustable plot window lengths from 10 ms to 1 s
* Plot appearance dialog for changing plot background color
* Disabled value controls when their impairment checkbox is unchecked
* Open output folder option from the File menu, toolbar, and Simulation Control panel

## Project Structure

```text
fm-signal-simulator/
  gui.py
  fmsim/
    __init__.py
    audio.py
    cli.py
    demod.py
    fm.py
    impairments.py
    io.py
    plots.py
    simulation.py
    gui/
      __init__.py
      appearance_dialog.py
      main_window.py
      plot_panel.py
      settings_panel.py
      widgets.py
      worker.py
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
py gui.py
```

The GUI provides a desktop engineering-tool style layout with:

* A top menu bar for File, View, Tools, and Help actions
* A toolbar for quick access to common commands
* A right-side Simulation Settings panel
* A central tabbed plot workspace for integrated signal visualization
* A bottom status bar for run status and progress indication

The GUI allows the user to:

* Select an input `.wav` audio file
* Select an output folder
* Open the selected output folder directly from the GUI
* Choose WBFM or NBFM modulation
* Configure AWGN, frequency offset, tone jammer, IQ dropout, DC offset, and IQ imbalance
* Select a repeatable random seed
* Save recovered audio, IQ samples, diagnostic plots, and simulation configuration data
* View integrated plots directly inside the GUI
* Adjust the visible time window for IQ time-domain and recovered audio plots
* Change the plot background color from the Tools menu
* View basic help and impairment information from the Help menu

Integrated GUI plot tabs include:
* IQ Time
* IQ Constellation
* PSD Comparison
* Spectrogram
* Recovered Audio

The IQ Time and Recovered Audio plots include a time slider and window length selector so different parts of the signal can be inspected without plotting the entire waveform at once.

Inactive impairment value controls are disabled until their checkbox is selected. Simulation runs are executed in a background thread so the interface remains responsive while the simulation is running.

## Command-Line Usage

Run the simulator from the project root folder:

```bash
py -m fmsim.cli examples/sample_audio.wav --mode wbfm
```

This runs a wideband FM simulation using the sample audio file.

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
outputs/plot_test/iq_constellation.png
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
  iq_constellation.png
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
outputs/readme_demo/iq_constellation.png
outputs/readme_demo/psd.png
outputs/readme_demo/psd_comparison.png
outputs/readme_demo/spectrogram.png
outputs/readme_demo/recovered_audio.png
outputs/readme_demo/recovered.wav
outputs/readme_demo/config.json
```

## Version History

### v0.7
- Added integrated GUI plot viewing inside the main application window
- Added tabbed plot workspace
- Added IQ Time plot tab
- Added IQ Constellation plot tab
- Added clean vs impaired PSD Comparison plot tab
- Added Spectrogram plot tab
- Added Recovered Audio plot tab
- Added scrollable time-window controls for IQ Time and Recovered Audio plots
- Added selectable plot window lengths: 10 ms, 50 ms, 100 ms, 250 ms, 500 ms, and 1 s
- Added Tools menu Plot Appearance dialog
- Added configurable plot background colors
- Added IQ constellation plot saving as `iq_constellation.png`
- Refactored GUI code into smaller modules:
  - `main_window.py`
  - `settings_panel.py`
  - `plot_panel.py`
  - `appearance_dialog.py`
  - `widgets.py`
  - `worker.py`
- Updated GUI to use shared simulation results directly for embedded plotting

### v0.6
- Rebuilt the GUI around a `QMainWindow` application layout
- Added top menu bar with File, View, Tools, and Help menus
- Added toolbar shortcuts for opening WAV files, selecting output folders, opening the output folder, and running simulations
- Added dockable right-side Simulation Settings panel
- Added central Signal Display Workspace placeholder for future v0.7 plot viewing
- Added bottom status bar with running and completed status messages
- Added indeterminate progress bar while simulations are running
- Moved simulation execution into a background thread to prevent the GUI from freezing
- Added Open Output Folder option to the File menu, toolbar, and Simulation Control panel
- Added Help menu popups for usage instructions, impairment descriptions, and program information
- Disabled impairment value controls when their corresponding checkbox is unchecked
- Disabled mouse-wheel value changes for spin boxes and combo boxes
- Improved spacing between impairment groups
- Updated Matplotlib plotting backend for GUI-safe plot saving

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