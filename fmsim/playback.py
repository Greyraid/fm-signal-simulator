from pathlib import Path
import math
import tempfile

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class AudioPlayer(QObject):
    status_changed = Signal(str)
    position_changed = Signal(int)
    duration_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)

        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)

        self.current_file: Path | None = None
        self.playback_file: Path | None = None

        self.player.positionChanged.connect(self.position_changed.emit)
        self.player.durationChanged.connect(self.duration_changed.emit)

    def load(self, file_path: str | Path) -> bool:
        file_path = Path(file_path)

        if not file_path.exists():
            self.status_changed.emit(f"File not found: {file_path}")
            return False

        try:
            self.playback_file = self.create_playback_wav(file_path)
        except Exception as exc:
            self.status_changed.emit(f"Could not prepare audio for playback: {exc}")
            return False

        self.current_file = file_path
        self.player.setSource(QUrl.fromLocalFile(str(self.playback_file)))
        self.status_changed.emit(f"Loaded: {file_path.name}")
        return True

    def play(self) -> None:
        if self.playback_file is None:
            self.status_changed.emit("No audio file loaded.")
            return

        self.player.play()
        self.status_changed.emit(f"Playing: {self.current_file.name}")

    def stop(self) -> None:
        self.player.pause()
        self.status_changed.emit("Stopped.")

    def reset(self) -> None:
        self.player.stop()
        self.player.setPosition(0)
        self.status_changed.emit("Reset to beginning.")

    def seek(self, position_ms: int) -> None:
        self.player.setPosition(position_ms)

    def set_volume(self, volume: float) -> None:
        volume = max(0.0, min(1.0, volume))
        self.audio_output.setVolume(volume)

    def create_playback_wav(self, file_path: Path) -> Path:
        input_sample_rate, audio = wavfile.read(file_path)

        audio = self.convert_to_float(audio)

        target_sample_rate = 44100

        if input_sample_rate != target_sample_rate:
            gcd = math.gcd(input_sample_rate, target_sample_rate)
            up = target_sample_rate // gcd
            down = input_sample_rate // gcd
            audio = resample_poly(audio, up, down, axis=0)

        audio_int16 = self.convert_to_int16(audio)

        temp_dir = Path(tempfile.gettempdir()) / "fmsim_playback"
        temp_dir.mkdir(parents=True, exist_ok=True)

        output_path = temp_dir / f"{file_path.stem}_playback.wav"
        wavfile.write(output_path, target_sample_rate, audio_int16)

        return output_path

    def convert_to_float(self, audio: np.ndarray) -> np.ndarray:
        if audio.dtype == np.int16:
            return audio.astype(np.float32) / 32768.0

        if audio.dtype == np.int32:
            return audio.astype(np.float32) / 2147483648.0

        if audio.dtype == np.uint8:
            return (audio.astype(np.float32) - 128.0) / 128.0

        return audio.astype(np.float32)

    def convert_to_int16(self, audio: np.ndarray) -> np.ndarray:
        max_value = np.max(np.abs(audio))

        if max_value > 0:
            audio = audio / max_value

        audio = np.clip(audio, -1.0, 1.0)

        return (audio * 32767).astype(np.int16)