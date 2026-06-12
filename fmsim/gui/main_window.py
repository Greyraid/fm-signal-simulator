from pathlib import Path
import os
import sys
import tempfile

from PySide6.QtCore import Qt, QThread, QStandardPaths
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QScrollArea,
    QDockWidget,
    QToolBar,
    QMessageBox,
    QProgressBar,
    QTabWidget,
    QSplashScreen,
)

from scipy.io import wavfile

from fmsim.gui.settings_panel import SettingsPanel
from fmsim.gui.worker import SimulationWorker
from fmsim.gui.plot_panel import PlotPanel
from fmsim.gui.appearance_dialog import PlotAppearanceDialog
from fmsim.gui.audio_playback_panel import AudioPlaybackPanel
from fmsim.version import WINDOW_TITLE, APP_NAME, APP_DESCRIPTION, APP_VERSION
from fmsim.resources import resource_path

class FMSimGui(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.remove_stale_temp_files()
        

        self.setWindowIcon(
            QIcon(str(resource_path("fmsim/resources/icons/fmsim.ico")))
        )

        self.input_wav: Path | None = None
        self.input_duration_s: float | None = None
        self.output_dir = self.get_default_output_dir()
        
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            self.output_dir = Path.home() / "FM Signal Simulator" / "outputs"

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(1200, 600)

        self.create_progress_bar()
        self.create_actions()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_workspace()
        self.create_settings_dock()

        self.settings_panel.set_output_dir(self.output_dir)

        self.statusBar().addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
        self.statusBar().showMessage("Ready")

    def create_progress_bar(self) -> None:
        """Create the status bar progress indicator."""

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(160)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)

    def create_actions(self) -> None:
        """Create actions used by the menu bar and toolbar."""

        self.open_wav_action = QAction("Open WAV", self)
        self.open_wav_action.triggered.connect(self.select_input_wav)

        self.output_folder_action = QAction("Output Folder", self)
        self.output_folder_action.triggered.connect(self.select_output_folder)

        self.open_output_action = QAction("Open Output Folder", self)
        self.open_output_action.triggered.connect(self.open_output_folder)

        self.run_action = QAction("Run Simulation", self)
        self.run_action.triggered.connect(self.run_simulation_from_gui)

        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.close)

        self.how_to_use_action = QAction("How to Use", self)
        self.how_to_use_action.triggered.connect(self.show_how_to_use)

        self.impairment_info_action = QAction("Impairment Information", self)
        self.impairment_info_action.triggered.connect(self.show_impairment_info)

        self.about_action = QAction("About FM Signal Simulator", self)
        self.about_action.triggered.connect(self.show_about)

        self.plot_appearance_action = QAction("Plot Appearance...", self)
        self.plot_appearance_action.triggered.connect(self.show_plot_appearance_dialog)

    def create_menu_bar(self) -> None:
        """Create the top application menu bar."""

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.open_wav_action)
        file_menu.addAction(self.output_folder_action)
        file_menu.addAction(self.open_output_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        self.view_menu = menu_bar.addMenu("View")

        tools_menu = menu_bar.addMenu("Tools")
        tools_menu.addAction(self.run_action)
        tools_menu.addSeparator()
        tools_menu.addAction(self.plot_appearance_action)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.how_to_use_action)
        help_menu.addAction(self.impairment_info_action)
        help_menu.addSeparator()
        help_menu.addAction(self.about_action)

    def create_toolbar(self) -> None:
        """Create the main toolbar below the menu bar."""

        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)

        toolbar.addAction(self.open_wav_action)
        toolbar.addAction(self.output_folder_action)
        toolbar.addAction(self.open_output_action)
        toolbar.addSeparator()
        toolbar.addAction(self.run_action)

        self.addToolBar(toolbar)

    def create_workspace(self) -> None:
        """Create the central chart workspace."""

        self.workspace_tabs = QTabWidget()
        
        self.plot_panel = PlotPanel()
        self.audio_playback_panel = AudioPlaybackPanel()

        self.workspace_tabs.addTab(self.plot_panel, "Plots")
        self.workspace_tabs.addTab(self.audio_playback_panel, "Audio Playback")

        self.setCentralWidget(self.workspace_tabs)

    def create_settings_dock(self) -> None:
        """Create the dockable simulation settings panel."""

        self.settings_panel = SettingsPanel()

        self.settings_panel.input_requested.connect(self.select_input_wav)
        self.settings_panel.output_requested.connect(self.select_output_folder)
        self.settings_panel.run_requested.connect(self.run_simulation_from_gui)
        self.settings_panel.open_output_requested.connect(self.open_output_folder)

        self.settings_dock = QDockWidget("Simulation Settings", self)

        self.settings_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(self.settings_panel)

        self.settings_dock.setWidget(scroll_area)

        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.settings_dock,
        )

        self.resizeDocks(
            [self.settings_dock],
            [380],
            Qt.Orientation.Horizontal,
        )

        self.view_menu.addAction(self.settings_dock.toggleViewAction())

    def select_input_wav(self) -> None:
        """Select and load an input WAV file."""

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input WAV",
            "",
            "WAV Files (*.wav)",
        )

        if not file_name:
            return

        selected_path = Path(file_name)

        try:
            sample_rate, audio = wavfile.read(selected_path)

            if sample_rate <= 0 or audio.size == 0:
                raise ValueError("The WAV file contains no valid audio data.")

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Invalid WAV File",
                (
                    "The selected WAV file could not be loaded.\n\n"
                    f"{exc}"
                ),
            )
            return

        self.input_duration_s = len(audio) / sample_rate
        self.settings_panel.set_input_duration(self.input_duration_s)

        self.input_wav = selected_path
        self.settings_panel.set_input_wav(self.input_wav)
        self.audio_playback_panel.load_original_audio(self.input_wav)

        self.statusBar().showMessage(
            f"Loaded input WAV: {self.input_wav.name}"
        )

    def select_output_folder(self) -> None:
        """Select the simulation output directory."""

        folder_name = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            str(self.output_dir),
        )

        if folder_name:
            selected_dir = Path(folder_name)

            try:
                selected_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                QMessageBox.warning(
                    self,
                    "Invalid Output Folder",
                    f"The selected output folder could not be used:\n\n{exc}",
                )
                return

            self.output_dir = selected_dir
            self.settings_panel.set_output_dir(self.output_dir)
            self.statusBar().showMessage(
                f"Output folder selected: {self.output_dir}"
            )

    def validate_output_dir(self) -> bool:
        """Verify that the output directory can be created and written to."""

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)

            test_file = self.output_dir / ".fmsim_write_test"
            test_file.touch()
            test_file.unlink()

            return True

        except OSError as exc:
            QMessageBox.warning(
                self,
                "Output Folder Error",
                (
                    "The selected output folder is not writable.\n\n"
                    f"{self.output_dir}\n\n"
                    f"{exc}"
                ),
            )

            self.statusBar().showMessage("Output folder is not writable.")
            return False

    def open_output_folder(self) -> None:
        """Open the selected output folder in the system file explorer."""

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            os.startfile(str(self.output_dir))

            self.statusBar().showMessage(
                f"Opened output folder: {self.output_dir}"
            )

        except Exception as exc:
            self.settings_panel.set_status_text(
                f"Could not open output folder:\n{exc}"
            )
            self.statusBar().showMessage("Could not open output folder.")

    def validate_input_wav(self) -> bool:
        """Verify that the selected input WAV exists and can be read."""

        if self.input_wav is None:
            QMessageBox.warning(
                self,
                "No input WAV",
                "Please select an input WAV file first."
            )
            return False
        
        if not self.input_wav.exists():
            QMessageBox.warning(
                self,
                "Input File Missing",
                (
                    "The selected WAV file could not be found.\n\n"
                    f"{self.input_wav}"
                )
            )
            return False
        
        if self.input_wav.suffix.lower() != ".wav":
            QMessageBox.warning(
                self,
                "Unsupported Input File",
                "The selected input file must be a WAV file."
            )
            return False
        
        try:
            sample_rate, audio = wavfile.read(self.input_wav)
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Invalid WAV File",
                (
                    "The selected WAV file could not be read.\n\n"
                    f"{exc}"
                )
            )
            return False
        
        if sample_rate <= 0:
            QMessageBox.warning(
                self,
                "Invalid WAV File",
                "The WAV file has an invalid sample rate."
            )
            return False

        if audio.size == 0:
            QMessageBox.warning(
                self,
                "Empty WAV File",
                "The selected WAV file contains no audio samples."
            )
            return False
    
        self.input_duration_s = len(audio) / sample_rate
        self.settings_panel.set_input_duration(self.input_duration_s)

        return True

    def run_simulation_from_gui(self) -> None:
        """Build config from GUI settings and run the simulation."""

        if not self.validate_input_wav():
            self.settings_panel.set_status_text(
                "A valid input WAV file is required."
            )
            self.statusBar().showMessage("Invalid input WAV file.")
            return

        if not self.validate_output_dir():
            return

        self.audio_playback_panel.clear_recovered_audio()

        try:
            config = self.settings_panel.get_config(
                input_wav=self.input_wav,
                output_dir=self.output_dir,
                input_duration_s=self.input_duration_s,
            )
        except ValueError as exc:
            QMessageBox.warning(
                self,
                "Invalid Simulation Settings",
                str(exc),
            )
            self.settings_panel.set_status_text(
                f"Invalid simulation settings:\n{exc}"
            )
            self.statusBar().showMessage("Invalid simulation settings.")
            return

        self.set_running_state(True)

        self.sim_thread = QThread()
        self.sim_worker = SimulationWorker(config)

        self.sim_worker.moveToThread(self.sim_thread)

        self.sim_thread.started.connect(self.sim_worker.run)
        self.sim_worker.finished.connect(self.handle_simulation_finished)
        self.sim_worker.failed.connect(self.handle_simulation_failed)

        self.sim_worker.finished.connect(self.sim_worker.deleteLater)
        self.sim_worker.failed.connect(self.sim_worker.deleteLater)
        self.sim_thread.finished.connect(self.sim_thread.deleteLater)

        self.sim_thread.start()

    def handle_simulation_finished(self, result) -> None:
        """Handle successful simulation completion."""

        message = (
            "Simulation complete.\n\n"
            f"Input WAV: {result.input_wav}\n"
            f"Mode: {result.mode}\n"
            f"Sample Rate: {result.fs_iq} Hz\n"
            f"Duration: {result.duration_s:.2f} seconds\n"
            f"Output Folder: {result.output_dir}\n"
        )

        if result.demod_audio_path is not None:
            message += f"Recovered Audio: {result.demod_audio_path}\n"

        if result.recovered_audio is not None and result.fs_audio is not None:
            self.audio_playback_panel.load_recovered_audio_array(
                result.recovered_audio,
                result.fs_audio
            )

        if result.plot_paths:
            message += "\nPlots:\n"
            for path in result.plot_paths:
                message += f"{path}\n"

        self.set_running_state(False)
        self.settings_panel.set_status_text(message)
        self.plot_panel.update_plots(result)

        self.statusBar().showMessage(
            f"Simulation complete | Output: {result.output_dir}"
        )

        self.sim_thread.quit()
        self.sim_thread.wait()

    def handle_simulation_failed(self, error_message: str) -> None:
        """Handle simulation failure."""

        self.set_running_state(False)
        self.settings_panel.set_status_text(
            f"Simulation failed:\n{error_message}"
        )
        self.statusBar().showMessage("Simulation failed.")

        self.sim_thread.quit()
        self.sim_thread.wait()

    def set_running_state(self, is_running: bool) -> None:
        """Update GUI controls and status bar while simulation runs."""

        self.settings_panel.set_running_state(is_running)

        self.run_action.setEnabled(not is_running)
        self.open_wav_action.setEnabled(not is_running)
        self.output_folder_action.setEnabled(not is_running)
        self.open_output_action.setEnabled(not is_running)
        self.plot_appearance_action.setEnabled(not is_running)

        self.progress_bar.setVisible(is_running)

        if is_running:
            self.settings_panel.set_status_text("Running simulation...\nPlease wait.")
            self.statusBar().showMessage("Running simulation...")
        else:
            self.progress_bar.hide()

    def show_how_to_use(self) -> None:
        """Show basic usage instructions."""

        QMessageBox.information(
            self,
            "How to Use",
            (
                "FM Signal Simulator - Basic Use\n\n"
                "1. Select an input WAV file.\n"
                "2. Select an output folder.\n"
                "3. Choose the FM mode: WBFM or NBFM.\n"
                "4. Enable any impairments you want to apply.\n"
                "5. Adjust the impairment values.\n"
                "6. Choose whether to save IQ data, plots, and recovered audio.\n"
                "7. Click Run Simulation.\n\n"
                "The results will be saved in the selected output folder. "
            ),
        )

    def show_impairment_info(self) -> None:
        """Show descriptions of available impairments."""

        QMessageBox.information(
            self,
            "Impairment Information",
            (
                "Available Signal Impairments\n\n"
                "AWGN:\n"
                "Adds random noise to the IQ signal. Lower SNR values create a noisier signal.\n\n"
                "Frequency Offset:\n"
                "Shifts the signal frequency, simulating tuner error or oscillator mismatch.\n\n"
                "Tone Jammer:\n"
                "Adds a single interfering tone at a selected frequency and power level.\n\n"
                "IQ Dropout:\n"
                "Zeros out part of the IQ signal for a selected time duration.\n\n"
                "DC Offset:\n"
                "Adds a constant offset to the I and/or Q channel.\n\n"
                "IQ Imbalance:\n"
                "Simulates gain and phase mismatch between the I and Q channels.\n\n"
                "Random Seed:\n"
                "Makes random noise repeatable between runs when enabled."
            ),
        )

    def show_about(self) -> None:
        """Show program information."""

        QMessageBox.information(
            self,
            f"About {APP_NAME}",
            (
                f"{APP_NAME}\n"
                f"Version {APP_VERSION}\n\n"
                f"{APP_DESCRIPTION}\n\n"
                "Key features:\n"
                "• WBFM and NBFM modulation\n"
                "• Configurable RF signal impairments\n"
                "• Integrated IQ and audio plots\n"
                "• Original and recovered audio playback\n"
                "• IQ, plot, configuration, and recovered WAV export\n"
                "• Command-line and PySide6 GUI interfaces\n\n"
                "Created by Greyson Meetze\n"
                "Built with Python, NumPy, SciPy, Matplotlib, and PySide6."
            ),
        )

    def show_plot_appearance_dialog(self) -> None:
        """Show plot appearance settings dalog."""

        dialog = PlotAppearanceDialog(
            current_background=self.plot_panel.plot_background_color,
            parent=self
        )

        if dialog.exec():
            self.plot_panel.set_plot_background_color(
                dialog.selected_background()
            )

    def get_default_output_dir(self) -> Path:
        """Return a writable default output directory."""

        document_dir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )

        if document_dir:
            return Path(document_dir) /"FM Signal Simulator" / "outputs"
        
        return Path.home() /"FM Signal Simulator" / "outputs"

    def closeEvent(self, event) -> None:
        """Clean up temporary playback files before closing."""

        self.audio_playback_panel.cleanup_temp_audio()
        event.accept()

    def remove_stale_temp_files(self) -> None:
        """Remove recovered playback files left by previous sessions."""

        temp_dir = Path(tempfile.gettempdir()) / "fmsim_playback"

        if not temp_dir.exists():
            return

        for file_path in temp_dir.glob("recovered_playback_*.wav"):
            try:
                file_path.unlink()
            except OSError:
                pass  

def main() -> None:
    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Greyson Meetze")

    icon_path = resource_path("fmsim/resources/icons/fmsim.ico")
    icon = QIcon(str(icon_path))
    app.setWindowIcon(icon)

    splash_path = resource_path("fmsim/resources/images/splash.png")
    splash_pixmap = QPixmap(str(splash_path)).scaled(
    600,
    340,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation,
)

    splash = QSplashScreen(splash_pixmap)
    splash.show()

    app.processEvents()

    window = FMSimGui()
    window.setWindowIcon(icon)
    window.show()

    splash.finish(window)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()