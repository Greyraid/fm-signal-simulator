import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QSlider,
    QComboBox
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy import signal

class PlotCanvas(FigureCanvas):
    """Reusable Matplotlib canvas for one plot tab"""

    def __init__(self) -> None:
        self.figure = Figure(figsize=(8, 5))
        self.axes = self.figure.add_subplot(111)

        super().__init__(self.figure)

    def clear(self) -> None:
        self.figure.clear()
        self.axes = self.figure.add_subplot(111)

class PlotPanel(QWidget):
    """Central tabbed plot display for simulation results."""

    def __init__(self) -> None:
        super().__init__()

        self.latest_result = None
        self.plot_background_color = "white"

        self.window_start_s = 0.0
        self.window_length_s = 0.05

        self.tabs = QTabWidget()

        self.iq_time_canvas = PlotCanvas()
        self.constellation_canvas = PlotCanvas()
        self.psd_canvas = PlotCanvas()
        self.spectrogram_canvas = PlotCanvas()
        self.audio_canvas = PlotCanvas()

        self.tabs.addTab(self.iq_time_canvas, "IQ Time")
        self.tabs.addTab(self.constellation_canvas, "IQ Constellation")
        self.tabs.addTab(self.psd_canvas, "PSD Comparison")
        self.tabs.addTab(self.spectrogram_canvas, "Spectrogram")
        self.tabs.addTab(self.audio_canvas, "Recovered Audio")

        self.set_plot_tabs_enabled(False)
        self.tabs.setTabEnabled(0, True)
        self.tabs.setCurrentIndex(0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

        self.time_controls = self.create_time_controls()
        layout.addWidget(self.time_controls)

        self.show_empty_message()

    def show_empty_message(self) -> None:
        """Show placeholder text before the first simulation run."""

        self.apply_canvas_background(self.iq_time_canvas)

        self.iq_time_canvas.axes.text(
            0.5,
            0.5,
            "Run a simulation to display plots.",
            ha="center",
            va="center",
            transform=self.iq_time_canvas.axes.transAxes
        )
        self.iq_time_canvas.axes.set_axis_off()
        self.iq_time_canvas.draw()

    def update_plots(self, result) -> None:
        """Update all plot tabs after a simulation run."""

        self.latest_result = result

        self.set_plot_tabs_enabled(True)
        self.configure_time_controls(result)

        self.plot_iq_time(result)
        self.plot_iq_constellation(result)
        self.plot_psd_comparison(result)
        self.plot_spectrogram(result)
        self.plot_recovered_audio(result)

    def set_plot_tabs_enabled(self, enabled: bool) -> None:
        """Enable or disable plot tabs."""
        for index in range(self.tabs.count()):
            self.tabs.setTabEnabled(index, enabled)

    def set_plot_background_color(self, color: str) -> None:
        """Set the background color for all plot canvases."""
        
        self.plot_background_color = color

        for canvas in self.get_all_canvases():
            canvas.figure.patch.set_facecolor(color)
            canvas.axes.set_facecolor(color)
            canvas.draw()
        
        if self.latest_result is not None:
            self.update_plots(self.latest_result)

    def get_all_canvases(self) -> list:
        """Return all plot canvases."""

        return [
            self.iq_time_canvas,
            self.constellation_canvas,
            self.psd_canvas,
            self.spectrogram_canvas,
            self.audio_canvas
        ]

    def apply_canvas_background(self, canvas) -> None:
        """Apply the selected background color to a canvas."""

        canvas.figure.patch.set_facecolor(self.plot_background_color)
        canvas.axes.set_facecolor(self.plot_background_color)

    def create_time_controls(self) -> QWidget:
        """Create time-window controls for scrollable plots."""

        controls = QWidget()
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(4, 4, 4, 4)

        self.time_label = QLabel("Time Window: run a simulation first")

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(0)
        self.time_slider.setValue(0)
        self.time_slider.setEnabled(False)
        self.time_slider.valueChanged.connect(self.handle_time_control_changed)

        self.window_length_box = QComboBox()
        self.window_length_box.addItem("10 ms", 0.010)
        self.window_length_box.addItem("50 ms", 0.050)
        self.window_length_box.addItem("100 ms", 0.100)
        self.window_length_box.addItem("250 ms", 0.250)
        self.window_length_box.addItem("500 ms", 0.500)
        self.window_length_box.addItem("1 s", 1.000)
        self.window_length_box.setCurrentIndex(1)
        self.window_length_box.setEnabled(False)
        self.window_length_box.currentIndexChanged.connect(self.handle_time_control_changed)

        layout.addWidget(QLabel("Start:"))
        layout.addWidget(self.time_slider, stretch=1)
        layout.addWidget(QLabel("Window:"))
        layout.addWidget(self.window_length_box)
        layout.addWidget(self.time_label)

        return controls
    
    def configure_time_controls(self, result) -> None:
        """Configure time slider limits after a simulation run."""

        duration_s = result.duration_s

        self.time_slider.blockSignals(True)
        self.window_length_box.blockSignals(True)

        self.window_start_s = self.window_length_box.currentData()

        max_start_s = max(0.0, duration_s - self.window_length_s)
        max_slider_value = int(max_start_s * 1000)

        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(max_slider_value)
        self.time_slider.setValue(0)
        self.time_slider.setEnabled(max_slider_value > 0)

        self.window_length_box.setEnabled(True)

        self.window_start_s = 0.0
        self.update_time_label(duration_s)

        self.time_slider.blockSignals(False)
        self.window_length_box.blockSignals(False)

    def handle_time_control_changed(self) -> None:
        """Redraw time-window plots when slider or window length changes."""

        if self.latest_result is None:
            return
        
        self.window_length_s = self.window_length_box.currentData()

        max_start_s = max(0.0, self.latest_result.duration_s - self.window_length_s)
        max_slider_value = int(max_start_s * 1000)

        current_value = min(self.time_slider.value(), max_slider_value)

        self.time_slider.blockSignals(True)
        self.time_slider.setMaximum(max_slider_value)
        self.time_slider.setValue(current_value)
        self.time_slider.blockSignals(False)

        self.window_start_s = current_value / 1000.0

        self.update_time_label(self.latest_result.duration_s)

        self.plot_iq_time(self.latest_result)
        self.plot_recovered_audio(self.latest_result)

    def update_time_label(self, duration_s: float) -> None:
        """Update the displayed time-window label."""

        end_time_s = min(duration_s, self.window_start_s + self.window_length_s)

        self.time_label.setText(
            f"{self.window_start_s:.3f}s to {end_time_s:.3f}s"
        )

    def plot_iq_time(self, result) -> None:
        """Plot impaired IQ samples in the time domain."""

        self.iq_time_canvas.clear()
        self.apply_canvas_background(self.iq_time_canvas)

        iq = result.iq_impaired
        fs = result.fs_iq

        start_idx = int(self.window_start_s * fs)
        end_idx = start_idx + int(self.window_length_s * fs)

        start_idx = max(0, start_idx)
        end_idx = min(len(iq), end_idx)

        iq_window = iq[start_idx:end_idx]
        t = np.arange(start_idx, end_idx) / fs

        self.iq_time_canvas.axes.plot(t, np.real(iq_window), label="I")
        self.iq_time_canvas.axes.plot(t, np.imag(iq_window), label="Q")

        self.iq_time_canvas.axes.set_title(
            f"IQ Time Domain ({self.window_start_s:.3f}s window start)"
        )       
        self.iq_time_canvas.axes.set_xlabel("Time (s)")
        self.iq_time_canvas.axes.set_ylabel("Amplitude")
        self.iq_time_canvas.axes.grid(True)
        self.iq_time_canvas.axes.legend()

        self.iq_time_canvas.figure.tight_layout()
        self.iq_time_canvas.draw()

    def plot_iq_constellation(self, result) -> None:
        """Plot impaired IQ samples as a constellation diagram."""

        self.constellation_canvas.clear()
        self.apply_canvas_background(self.constellation_canvas)

        iq = result.iq_impaired

        max_points = min(len(iq), 20_000)

        if max_points <= 0:
            self.constellation_canvas.axes.text(
                0.5,
                0.5,
                "No IQ samples available.",
                ha="center",
                va="center",
                transform=self.constellation_canvas.axes.transAxes
            )
            self.constellation_canvas.axes.set_axis_off()
            self.constellation_canvas.draw()
            return

        step = max(1, len(iq) // max_points)
        iq_plot = iq[::step][:max_points]

        self.constellation_canvas.axes.scatter(
            np.real(iq_plot),
            np.imag(iq_plot),
            s=1,
            alpha=0.35
        )

        self.constellation_canvas.axes.axhline(0, linewidth=0.8)
        self.constellation_canvas.axes.axvline(0, linewidth=0.8)

        self.constellation_canvas.axes.set_title("IQ Constellation")
        self.constellation_canvas.axes.set_xlabel("In-phase (I)")
        self.constellation_canvas.axes.set_ylabel("Quadrature (Q)")
        self.constellation_canvas.axes.grid(True)
        self.constellation_canvas.axes.set_aspect("equal", adjustable="box")

        self.constellation_canvas.figure.tight_layout()
        self.constellation_canvas.draw()

    def plot_psd_comparison(self, result) -> None:
        """Plot clean vs impaired PSD."""

        self.psd_canvas.clear()
        self.apply_canvas_background(self.psd_canvas)


        fs = result.fs_iq

        f_clean, pxx_clean = signal.welch(
            result.iq_clean,
            fs=fs,
            nperseg=2048,
            return_onesided=False,
        )

        f_imp, pxx_imp = signal.welch(
            result.iq_impaired,
            fs=fs,
            nperseg=2048,
            return_onesided=False,
        )

        f_clean = np.fft.fftshift(f_clean)
        pxx_clean = np.fft.fftshift(pxx_clean)

        f_imp = np.fft.fftshift(f_imp)
        pxx_imp = np.fft.fftshift(pxx_imp)

        self.psd_canvas.axes.plot(
            f_clean,
            10 * np.log10(pxx_clean + 1e-12),
            label="Clean",
        )
        self.psd_canvas.axes.plot(
            f_imp,
            10 * np.log10(pxx_imp + 1e-12),
            label="Impaired",
        )

        self.psd_canvas.axes.set_title("Clean vs Impaired PSD")
        self.psd_canvas.axes.set_xlabel("Frequency (Hz)")
        self.psd_canvas.axes.set_ylabel("PSD (dB/Hz)")
        self.psd_canvas.axes.grid(True)
        self.psd_canvas.axes.legend()

        self.psd_canvas.figure.tight_layout()
        self.psd_canvas.draw()

    def plot_spectrogram(self, result) -> None:
        """Plot impaired IQ spectrogram."""

        self.spectrogram_canvas.clear()
        self.apply_canvas_background(self.spectrogram_canvas)

        fs = result.fs_iq
        iq = result.iq_impaired

        self.spectrogram_canvas.axes.specgram(
            iq,
            NFFT=1024,
            Fs=fs,
            noverlap=512,
        )

        self.spectrogram_canvas.axes.set_title("Impaired IQ Spectrogram")
        self.spectrogram_canvas.axes.set_xlabel("Time (s)")
        self.spectrogram_canvas.axes.set_ylabel("Frequency (Hz)")

        self.spectrogram_canvas.figure.tight_layout()
        self.spectrogram_canvas.draw()

    def plot_recovered_audio(self, result) -> None:
        """Plot recovered audio snippet if available."""

        self.audio_canvas.clear()
        self.apply_canvas_background(self.audio_canvas)

        if result.recovered_audio is None or result.fs_audio is None:
            self.audio_canvas.axes.text(
                0.5,
                0.5,
                "Recovered audio data not available.",
                ha="center",
                va="center",
                transform=self.audio_canvas.axes.transAxes,
            )
            self.audio_canvas.axes.set_axis_off()
            self.audio_canvas.draw()
            return

        audio = result.recovered_audio
        fs_audio = result.fs_audio

        start_idx = int(self.window_start_s * fs_audio)
        end_idx = start_idx + int(self.window_length_s * fs_audio)

        start_idx = max(0, start_idx)
        end_idx = min(len(audio), end_idx)

        audio_window = audio[start_idx:end_idx]
        t = np.arange(start_idx, end_idx) / fs_audio

        self.audio_canvas.axes.plot(t, audio_window)

        self.audio_canvas.axes.set_title(f"Recovered Audio ({self.window_start_s:.3f}s window start)")
        self.audio_canvas.axes.set_xlabel("Time (s)")
        self.audio_canvas.axes.set_ylabel("Amplitude")
        self.audio_canvas.axes.grid(True)

        self.audio_canvas.figure.tight_layout()
        self.audio_canvas.draw()