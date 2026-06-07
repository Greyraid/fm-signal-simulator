from pathlib import Path
import os
import sys

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QScrollArea,
    QDockWidget,
    QToolBar,
    QMessageBox,
    QProgressBar,
)

from fmsim.gui.settings_panel import SettingsPanel
from fmsim.gui.worker import SimulationWorker
from fmsim.gui.plot_panel import PlotPanel
from fmsim.gui.appearance_dialog import PlotAppearanceDialog

class FMSimGui(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.input_wav: Path | None = None
        self.output_dir: Path = Path("outputs")

        self.setWindowTitle("FM Signal Simulator")
        self.resize(1200, 600)

        self.create_progress_bar()
        self.create_actions()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_workspace()
        self.create_settings_dock()

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

        self.plot_panel = PlotPanel()
        self.setCentralWidget(self.plot_panel)

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
            [355],
            Qt.Orientation.Horizontal,
        )

        self.view_menu.addAction(self.settings_dock.toggleViewAction())

    def select_input_wav(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input WAV",
            "",
            "WAV Files (*.wav)",
        )

        if file_name:
            self.input_wav = Path(file_name)
            self.settings_panel.set_input_wav(self.input_wav)

    def select_output_folder(self) -> None:
        folder_name = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            "",
        )

        if folder_name:
            self.output_dir = Path(folder_name)
            self.settings_panel.set_output_dir(self.output_dir)

    def open_output_folder(self) -> None:
        """Open the selected output folder in the system file explorer."""

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            os.startfile(self.output_dir)

            self.statusBar().showMessage(
                f"Opened output folder: {self.output_dir}"
            )

        except Exception as exc:
            self.settings_panel.set_status_text(
                f"Could not open output folder:\n{exc}"
            )
            self.statusBar().showMessage("Could not open output folder.")

    def run_simulation_from_gui(self) -> None:
        """Build config from GUI settings and run the simulation."""

        if self.input_wav is None:
            self.settings_panel.set_status_text(
                "Please select an input WAV file first."
            )
            self.statusBar().showMessage("No input WAV file selected.")
            return

        config = self.settings_panel.get_config(
            input_wav=self.input_wav,
            output_dir=self.output_dir,
        )

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
            "About FM Signal Simulator",
            (
                "FM Signal Simulator\n\n"
                "A Python-based FM signal simulation tool for generating, impairing, "
                "analyzing, and recovering FM-modulated signals from WAV audio files.\n\n"
                "Current focus: v0.7 integrated plot display."
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

def main() -> None:
    app = QApplication(sys.argv)
    window = FMSimGui()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()