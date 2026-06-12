from pathlib import Path
import tempfile
import numpy as np
from scipy.io  import wavfile

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QSlider,
)

from fmsim.playback import AudioPlayer

class AudioPlaybackPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_recovered_temp_path: Path | None = None

        self.original_player = AudioPlayer(self)
        self.recovered_player = AudioPlayer(self)

        self.original_slider_is_pressed = False
        self.recovered_slider_is_pressed = False

        self.recovered_audio_counter = 0

        self.create_layout()
        self.connect_signals()

    def create_layout(self) -> None:
        main_layout = QVBoxLayout(self)

        title_label = QLabel("Audio Playback")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.original_group = self.create_audio_section("Original Input Audio")
        self.recovered_group = self.create_audio_section("Recovered Output Audio")

        main_layout.addWidget(title_label)
        main_layout.addWidget(self.original_group["box"])
        main_layout.addWidget(self.recovered_group["box"])
        main_layout.addStretch()

    def create_audio_section(self, title: str) -> dict:
        group_box = QGroupBox(title)
        layout = QVBoxLayout(group_box)

        file_label = QLabel("No file loaded.")
        file_label.setWordWrap(True)

        time_label = QLabel("00:00 / 00:00")

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 0)

        volume_label = QLabel("Volume: 50%")

        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(50)
        volume_slider.setMaximumWidth(180)

        button_layout = QHBoxLayout()

        play_button = QPushButton("Play")
        stop_button = QPushButton("Stop")
        reset_button = QPushButton("Reset")

        play_button.setEnabled(False)
        stop_button.setEnabled(False)
        reset_button.setEnabled(False)

        button_layout.addWidget(play_button)
        button_layout.addWidget(stop_button)
        button_layout.addWidget(reset_button)
        button_layout.addStretch()

        volume_layout = QHBoxLayout()
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(volume_slider)
        volume_layout.addStretch()

        layout.addWidget(file_label)
        layout.addWidget(time_label)
        layout.addWidget(slider)
        layout.addLayout(button_layout)
        layout.addLayout(volume_layout)

        return {
            "box": group_box,
            "file_label": file_label,
            "time_label": time_label,
            "slider": slider,
            "play_button": play_button,
            "stop_button": stop_button,
            "reset_button": reset_button,
            "volume_label": volume_label,
            "volume_slider": volume_slider,
        }

    def connect_signals(self) -> None:
        self.original_group["play_button"].clicked.connect(self.original_player.play)
        self.original_group["stop_button"].clicked.connect(self.original_player.stop)
        self.original_group["reset_button"].clicked.connect(self.original_player.reset)

        self.recovered_group["play_button"].clicked.connect(self.recovered_player.play)
        self.recovered_group["stop_button"].clicked.connect(self.recovered_player.stop)
        self.recovered_group["reset_button"].clicked.connect(self.recovered_player.reset)

        self.original_player.position_changed.connect(self.update_original_position)
        self.original_player.duration_changed.connect(self.update_original_duration)

        self.recovered_player.position_changed.connect(self.update_recovered_position)
        self.recovered_player.duration_changed.connect(self.update_recovered_duration)

        self.original_group["slider"].sliderPressed.connect(
            lambda: self.set_original_slider_pressed(True)
        )
        self.original_group["slider"].sliderReleased.connect(
            self.seek_original_audio
        )

        self.recovered_group["slider"].sliderPressed.connect(
            lambda: self.set_recovered_slider_pressed(True)
        )
        self.recovered_group["slider"].sliderReleased.connect(
            self.seek_recovered_audio
        )

        self.original_group["volume_slider"].valueChanged.connect(
            self.set_original_volume
        )

        self.recovered_group["volume_slider"].valueChanged.connect(
            self.set_recovered_volume
        )

        self.original_player.status_changed.connect(self.update_status)
        self.recovered_player.status_changed.connect(self.update_status)

    def load_original_audio(self, file_path: Path) -> None:
        loaded = self.original_player.load(file_path)

        self.set_section_enabled(self.original_group, loaded)
                
        if loaded:
            self.original_group["file_label"].setText(f"File: {file_path}")

    def load_recovered_audio(self, file_path: Path) -> None:
        """Load recovered audio into the playback controls."""

        self.recovered_player.stop()
        self.recovered_group["slider"].setValue(0)
        self.recovered_group["slider"].setRange(0, 0)
        self.recovered_group["time_label"].setText("00:00 / 00:00")

        loaded = self.recovered_player.load(file_path)

        self.set_section_enabled(self.recovered_group, loaded)

        if loaded:
            self.recovered_group["file_label"].setText(
                f"File: {file_path}"
            )
        else:
            self.recovered_group["file_label"].setText(
                "Recovered audio could not be loaded."
            )

    def load_recovered_audio_array(self, audio: np.ndarray, fs_audio: int) -> None:
        """Write recovered audio to a temporary WAV file and replace the old one."""

        temp_dir = Path(tempfile.gettempdir()) / "fmsim_playback"
        temp_dir.mkdir(parents=True, exist_ok=True)

        self.recovered_audio_counter += 1
        temp_path = temp_dir / (
            f"recovered_playback_{self.recovered_audio_counter}.wav"
        )

        audio = np.asarray(audio)

        if audio.size == 0:
            self.clear_recovered_audio()
            return

        max_value = np.max(np.abs(audio))

        if max_value > 0:
            audio = audio / max_value

        audio_int16 = np.clip(audio, -1.0, 1.0)
        audio_int16 = (audio_int16 * 32767).astype(np.int16)

        wavfile.write(str(temp_path), int(fs_audio), audio_int16)

        previous_path = self.current_recovered_temp_path

        self.recovered_player.unload()
        self.load_recovered_audio(temp_path)
        self.current_recovered_temp_path = temp_path

        if previous_path is not None and previous_path.exists():
            try:
                previous_path.unlink()
            except OSError:
                pass

    def update_original_duration(self, duration_ms: int) -> None:
        self.original_group["slider"].setRange(0, duration_ms)
        self.update_time_label(
            self.original_group["time_label"],
            self.original_group["slider"].value(),
            duration_ms,
        )

    def update_recovered_duration(self, duration_ms: int) -> None:
        self.recovered_group["slider"].setRange(0, duration_ms)
        self.update_time_label(
            self.recovered_group["time_label"],
            self.recovered_group["slider"].value(),
            duration_ms,
        )

    def update_original_position(self, position_ms: int) -> None:
        if not self.original_slider_is_pressed:
            self.original_group["slider"].setValue(position_ms)

        self.update_time_label(
            self.original_group["time_label"],
            position_ms,
            self.original_group["slider"].maximum(),
        )

    def update_recovered_position(self, position_ms: int) -> None:
        if not self.recovered_slider_is_pressed:
            self.recovered_group["slider"].setValue(position_ms)

        self.update_time_label(
            self.recovered_group["time_label"],
            position_ms,
            self.recovered_group["slider"].maximum(),
        )

    def set_original_slider_pressed(self, pressed: bool) -> None:
        self.original_slider_is_pressed = pressed

    def set_recovered_slider_pressed(self, pressed: bool) -> None:
        self.recovered_slider_is_pressed = pressed

    def seek_original_audio(self) -> None:
        position_ms = self.original_group["slider"].value()
        self.original_player.seek(position_ms)
        self.original_slider_is_pressed = False

    def seek_recovered_audio(self) -> None:
        position_ms = self.recovered_group["slider"].value()
        self.recovered_player.seek(position_ms)
        self.recovered_slider_is_pressed = False

    def update_status(self, message: str) -> None:
        self.window().statusBar().showMessage(message)

    def update_time_label(
        self,
        label: QLabel,
        position_ms: int,
        duration_ms: int,
    ) -> None:
        label.setText(
            f"{self.format_time(position_ms)} / {self.format_time(duration_ms)}"
        )

    def format_time(self, time_ms: int) -> str:
        total_seconds = max(0, time_ms // 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        return f"{minutes:02d}:{seconds:02d}"
    
    def set_original_volume(self, value: int) -> None:
        """Update original audio playback volume."""

        self.original_player.set_volume(value / 100.0)
        self.original_group["volume_label"].setText(f"Volume: {value}%")

    def set_recovered_volume(self, value: int) -> None:
        """Update recovered audio playback volume."""

        self.recovered_player.set_volume(value / 100.0)
        self.recovered_group["volume_label"].setText(f"Volume: {value}%")

    def set_section_enabled(self, section: dict, enabled: bool) -> None:
        """Enable or disable playback controls for one audio section."""

        section["play_button"].setEnabled(enabled)
        section["stop_button"].setEnabled(enabled)
        section["reset_button"].setEnabled(enabled)
        section["slider"].setEnabled(enabled)

    def clear_recovered_audio(self) -> None:
        """Clear recovered playback until a new simulation finishes."""

        self.recovered_player.stop()
        self.recovered_player.reset()

        self.recovered_group["file_label"].setText("No file loaded.")
        self.recovered_group["slider"].setRange(0, 0)
        self.recovered_group["slider"].setValue(0)
        self.recovered_group["time_label"].setText("00:00 / 00:00")

        self.recovered_slider_is_pressed = False

        self.set_section_enabled(self.recovered_group, False)

    def cleanup_temp_audio(self) -> None:
        """Delete temporary recovered playback files."""

        self.recovered_player.unload()

        if (
            self.current_recovered_temp_path is not None
            and self.current_recovered_temp_path.exists()
        ):
            try:
                self.current_recovered_temp_path.unlink()
            except OSError:
                pass

        self.current_recovered_temp_path = None