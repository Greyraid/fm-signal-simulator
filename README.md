# FM Signal Simulator

A Python-based FM signal simulator that converts `.wav` audio into complex IQ samples with configurable FM modulation and signal impairments.

This project is designed as a learning and research tool for digital signal processing, software-defined radio concepts, RF simulation, and future machine-learning-based signal recovery experiments.

## Current Version

**v0.1**

This version implements the first working signal simulation chain:

```text
WAV audio → normalized/resampled audio → FM IQ modulation → impairments → saved IQ file → diagnostic plots