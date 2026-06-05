from pathlib import Path
import sys
import os

from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QFileDialog,
    QComboBox,
    QDoubleSpinBox,
    QCheckBox,
    QTextEdit,
    QSpinBox,
    QScrollArea,
    QDockWidget,
    QToolBar,
    QFrame,
    QSizePolicy,
    QMessageBox,
    QProgressBar,
)

from fmsim.simulation import SimulationConfig, run_simulation

# Disable mouse wheel spin
# ===========================================================
class NoWheelDoubleSpinBox(QDoubleSpinBox):
    """Double spin box that ignores mouse wheel changes."""
    def wheelEvent(self, event) -> None:
        event.ignore()

class NoWheelSpinBox(QSpinBox):
    """Spin box that ignores mouse wheel changes."""
    def wheelEvent(self, event) -> None:
        event.ignore()

class NoWheelComboBox(QComboBox):
    """Combo box that ignores mouse wheel changes."""
    def wheelEvent(self, event) -> None:
        event.ignore()

class SimulationWorker(QObject):
    """Run the FM simulation in a background thread."""

    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, config: SimulationConfig) -> None:
        super().__init__()
        self.config = config

    @Slot()
    def run(self) -> None:
        try:
            result = run_simulation(self.config)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))

# ======================================================
class FMSimGui(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.input_wav: Path | None = None
        self.output_dir: Path = Path("outputs")

        self.setWindowTitle("FM Signal Simulator")
        self.resize(1200, 600)

        # Build application interface
        # =====================================
        self.create_widgets()
        self.create_actions()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_workspace()
        self.create_settings_dock()

        self.statusBar().addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
        self.statusBar().showMessage("Ready")

    def create_widgets(self) -> None:
        '''
        Create all GUI widgets arranging them into sections
        '''

        # Input and Output Widgets
        # ====================================
        self.input_label = QLabel("Input WAV: None selected")
        self.output_label = QLabel(f"Output Folder: {self.output_dir}")

        self.input_label.setWordWrap(True)
        self.output_label.setWordWrap(True)
        self.input_label.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred
        )

        self.output_label.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Preferred
        )

        self.input_button = QPushButton("Select Input WAV")
        self.input_button.clicked.connect(self.select_input_wav)

        self.output_button = QPushButton("Select Output Folder")
        self.output_button.clicked.connect(self.select_output_folder)

        self.save_iq_check = QCheckBox("Save IQ Data")
        self.save_iq_check.setChecked(False)

        self.save_plots_check = QCheckBox("Save Plots")
        self.save_plots_check.setChecked(True)

        self.save_audio_check = QCheckBox("Save Recovered Audio")
        self.save_audio_check.setChecked(True)

        # FM Settings Widgets
        # =======================================
        self.mode_box = NoWheelComboBox()
        self.mode_box.addItems(["wbfm", "nbfm"])

        # AWGN Widgets
        # =======================================
        self.use_snr_check = QCheckBox("Add AWGN")

        self.snr_box = NoWheelDoubleSpinBox()
        self.snr_box.setRange(-50.0, 100.0)
        self.snr_box.setValue(20.0)
        self.snr_box.setSuffix(" dB")

        # Frequency Offset Widgets
        # =======================================
        self.use_freq_offset_check = QCheckBox("Add Frequency Offset")

        self.freq_offset_box = NoWheelDoubleSpinBox()
        self.freq_offset_box.setRange(-100_000.0, 100_000.0)
        self.freq_offset_box.setValue(0.0)
        self.freq_offset_box.setSuffix(" Hz")
        
        # Tone Jammer Widgets
        # =======================================
        self.use_tone_jammer_check = QCheckBox("Add Tone Jammer")

        self.tone_jammer_box = NoWheelDoubleSpinBox()
        self.tone_jammer_box.setRange(0.0, 100_000.0)
        self.tone_jammer_box.setValue(25_000.0)
        self.tone_jammer_box.setSuffix(" Hz")

        self.tone_jammer_power_box = NoWheelDoubleSpinBox()
        self.tone_jammer_power_box.setRange(-100.0, 20.0)
        self.tone_jammer_power_box.setValue(-10.0)
        self.tone_jammer_power_box.setSuffix(" dB")

        # Dropout Widgets
        # =======================================
        self.use_dropout_check = QCheckBox("Add IQ Dropout")

        self.dropout_start_box = NoWheelDoubleSpinBox()
        self.dropout_start_box.setRange(0.0, 999.0) #change this to change with the length of the audio
        self.dropout_start_box.setValue(2.0)
        self.dropout_start_box.setSuffix(" s")

        self.dropout_duration_box = NoWheelDoubleSpinBox()
        self.dropout_duration_box.setRange(0.0, 999.0)
        self.dropout_duration_box.setValue(0.25)
        self.dropout_duration_box.setSuffix(" s")

        # DC Offset Widgets
        # =======================================
        self.use_dc_offset_check = QCheckBox("Add DC Offset")

        self.dc_i_box = NoWheelDoubleSpinBox()
        self.dc_i_box.setRange(-10.0, 10.0)
        self.dc_i_box.setValue(0.0)

        self.dc_q_box = NoWheelDoubleSpinBox()
        self.dc_q_box.setRange(-10.0, 10.0)
        self.dc_q_box.setValue(0.0)

        # IQ Imbalance Widgets
        # =======================================
        self.use_iq_imbalance_check = QCheckBox("Add IQ Imbalance")

        self.iq_gain_imbalance_box = NoWheelDoubleSpinBox()
        self.iq_gain_imbalance_box.setRange(-20.0, 20.0)
        self.iq_gain_imbalance_box.setValue(0.0)
        self.iq_gain_imbalance_box.setSuffix(" dB")

        self.iq_phase_imbalance_box = NoWheelDoubleSpinBox()
        self.iq_phase_imbalance_box.setRange(-45.0, 45.0)
        self.iq_phase_imbalance_box.setValue(0.0)
        self.iq_phase_imbalance_box.setSuffix(" deg")

        # Seed Widget
        # =======================================
        self.use_seed_check = QCheckBox("Use Random Seed")
        self.seed_box = NoWheelSpinBox()
        self.seed_box.setRange(0, 999)
        self.seed_box.setValue(123)

        # Run / Status Widgets
        # =======================================
        self.run_button = QPushButton("Run Simulation")
        self.run_button.clicked.connect(self.run_simulation_from_gui)

        self.open_output_button = QPushButton("Open Output Folder")
        self.open_output_button.clicked.connect(self.open_output_folder)

        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setMinimumHeight(150)

        # Enable / disable controls based on checkboxes
        # =======================================
        self.use_snr_check.toggled.connect(self.update_impairment_controls)
        self.use_freq_offset_check.toggled.connect(self.update_impairment_controls)
        self.use_tone_jammer_check.toggled.connect(self.update_impairment_controls)
        self.use_dropout_check.toggled.connect(self.update_impairment_controls)
        self.use_dc_offset_check.toggled.connect(self.update_impairment_controls)
        self.use_iq_imbalance_check.toggled.connect(self.update_impairment_controls)
        self.use_seed_check.toggled.connect(self.update_impairment_controls)

        self.update_impairment_controls()

        # Status bar progress indicator
        # =========================================
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(160)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0) # Indeterminate/busy indication
        self.progress_bar.setVisible(False)

    def update_impairment_controls(self) -> None:
        """Enable controls only when their impairment checkbox is checked"""
        self.snr_box.setEnabled(self.use_snr_check.isChecked())

        self.freq_offset_box.setEnabled(self.use_freq_offset_check.isChecked())

        tone_jammer_enabled = self.use_tone_jammer_check.isChecked()
        self.tone_jammer_box.setEnabled(tone_jammer_enabled)
        self.tone_jammer_power_box.setEnabled(tone_jammer_enabled)

        dropout_enabled = self.use_dropout_check.isChecked()
        self.dropout_start_box.setEnabled(dropout_enabled)
        self.dropout_duration_box.setEnabled(dropout_enabled)

        dc_offset_enabled = self.use_dc_offset_check.isChecked()
        self.dc_i_box.setEnabled(dc_offset_enabled)
        self.dc_q_box.setEnabled(dc_offset_enabled)

        iq_imbalance_enabled = self.use_iq_imbalance_check.isChecked()
        self.iq_gain_imbalance_box.setEnabled(iq_imbalance_enabled)
        self.iq_phase_imbalance_box.setEnabled(iq_imbalance_enabled)

        self.seed_box.setEnabled(self.use_seed_check.isChecked())

    def create_actions(self) -> None:
        '''
        Create actions used by the menu bar and toolbar.
        '''
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

        # Help actions
        # ===============================================
        self.how_to_use_action = QAction("How to Use", self)
        self.how_to_use_action.triggered.connect(self.show_how_to_use)

        self.impairment_info_action = QAction("Impairment Information", self)
        self.impairment_info_action.triggered.connect(self.show_impairment_info)

        self.about_action = QAction("About FM Signal Simulator", self)
        self.about_action.triggered.connect(self.show_about)

    def create_menu_bar(self) -> None:
        '''
        Create the top application menu bar.
        '''
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

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.how_to_use_action)
        help_menu.addAction(self.impairment_info_action)
        help_menu.addSeparator()
        help_menu.addAction(self.about_action)

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
                "Plot viewing inside the main workspace will be added in v0.7."
            ),
        )

    def show_impairment_info(self) -> None:
        """Show descriptions of available impairments"""

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
        """Show program information"""
        
        QMessageBox.information(
            self,
            "About FM Signal Simulator",
            (
                "FM Signal Simulator\n\n"
                "A Python-based FM signal simulation tool for generating, impairing, "
                "analyzing, and recovering FM-modulated signals from WAV audio files.\n\n"
                "Current focus: v0.6 GUI layout and usability polish.\n"
                "Next focus: v0.7 integrated plot display."
            ),
        )

    def create_toolbar(self) -> None:
        '''
        Create the main toolbar below the menu bar.
        '''
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)

        toolbar.addAction(self.open_wav_action)
        toolbar.addAction(self.output_folder_action)
        toolbar.addAction(self.open_output_action)
        toolbar.addSeparator()
        toolbar.addAction(self.run_action)

        self.addToolBar(toolbar)

    def create_workspace(self) -> None:
        '''
        Create the central chart workspace.
        '''
        workspace = QFrame()
        workspace.setObjectName("workspace")

        workspace.setStyleSheet(
            """
            QFrame#workspace {
                background-color: #151a1f;
                border: 1px solid #2d353d;
            }

            QLabel#workspaceTitle {
                color: #e6e6e6;
                font-size: 20px;
                font-weight: bold;
            }

            QLabel#workspaceMessage {
                color: #9aa4ad;
                font-size: 12px;
            }
            """
        )

        layout = QVBoxLayout(workspace)

        title = QLabel("Signal Display Workspace")

        title.setObjectName("workspaceTitle")

        message = QLabel(
            "No plots currently displayed.\n\n"
            "Run a simulation to generate output files.\n\n"
            "Integrated chart viewing will be added in v0.7"
        )
        message.setObjectName("workspaceMessage")

        layout.addStretch()
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.setCentralWidget(workspace)

    def create_settings_dock(self) -> None:
        """Create the dockable simulation settings panel."""

        self.settings_dock = QDockWidget("Simulation Settings", self)

        self.settings_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(self.create_input_output_section())
        layout.addWidget(self.create_fm_settings_section())
        layout.addWidget(self.create_impairments_section())
        layout.addWidget(self.create_run_section())
        layout.addStretch()

        scroll_area.setWidget(scroll_content)
        self.settings_dock.setWidget(scroll_area)

        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.settings_dock
        )

        self.resizeDocks(
            [self.settings_dock],
            [355],
            Qt.Orientation.Horizontal
        )

        self.view_menu.addAction(self.settings_dock.toggleViewAction())

    def create_input_output_section(self) -> QGroupBox:
        '''
        Create the input file, output folder, and save options section.
        '''
        
        group = QGroupBox("Input / Output")
        layout = QVBoxLayout()

        layout.addWidget(self.input_label)
        layout.addWidget(self.input_button)

        layout.addSpacing(6)

        layout.addWidget(self.output_label)
        layout.addWidget(self.output_button)

        layout.addSpacing(8)

        layout.addWidget(QLabel("Save Options"))
        layout.addWidget(self.save_iq_check)
        layout.addWidget(self.save_plots_check)
        layout.addWidget(self.save_audio_check)

        group.setLayout(layout)
        return group

    def create_fm_settings_section(self) -> QGroupBox:
        """Create FM signal settings controls."""

        group = QGroupBox("FM Settings")
        layout = QFormLayout()

        layout.addRow("FM Mode:", self.mode_box)

        group.setLayout(layout)
        return group

    def make_impairment_form(self) -> QFormLayout:
        """Create a form layout used for one impairment group."""
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        form.setContentsMargins(0, 0, 0, 0)
        return form

    def create_impairments_section(self) -> QGroupBox:
        """Create signal impairment controls with more spacing between groups."""

        group = QGroupBox("Signal Impairments")
        outer = QVBoxLayout()
        outer.setSpacing(16)

        # AWGN
        awgn_form = self.make_impairment_form()
        awgn_form.addRow(self.use_snr_check, self.snr_box)
        outer.addLayout(awgn_form)

        # Frequency Offset
        freq_form = self.make_impairment_form()
        freq_form.addRow(self.use_freq_offset_check, self.freq_offset_box)
        outer.addLayout(freq_form)

        # Tone Jammer
        jammer_form = self.make_impairment_form()
        jammer_form.addRow(self.use_tone_jammer_check, self.tone_jammer_box)
        jammer_form.addRow("Jammer Power:", self.tone_jammer_power_box)
        outer.addLayout(jammer_form)

        # IQ Dropout
        dropout_form = self.make_impairment_form()
        dropout_form.addRow(self.use_dropout_check)
        dropout_form.addRow("Start Time:", self.dropout_start_box)
        dropout_form.addRow("Duration:", self.dropout_duration_box)
        outer.addLayout(dropout_form)

        # DC Offset
        dc_form = self.make_impairment_form()
        dc_form.addRow(self.use_dc_offset_check)
        dc_form.addRow("I Offset:", self.dc_i_box)
        dc_form.addRow("Q Offset:", self.dc_q_box)
        outer.addLayout(dc_form)

        # IQ Imbalance
        iq_form = self.make_impairment_form()
        iq_form.addRow(self.use_iq_imbalance_check)
        iq_form.addRow("Gain Error:", self.iq_gain_imbalance_box)
        iq_form.addRow("Phase Error:", self.iq_phase_imbalance_box)
        outer.addLayout(iq_form)

        # Random Seed
        seed_form = self.make_impairment_form()
        seed_form.addRow(self.use_seed_check, self.seed_box)
        outer.addLayout(seed_form)

        group.setLayout(outer)
        return group
    
    def create_run_section(self) -> QGroupBox:
        """Create run control and detailed status display"""

        group = QGroupBox("Simulation Control")
        layout = QVBoxLayout()

        self.run_button.setMinimumHeight(34)

        layout.addWidget(self.run_button)
        layout.addWidget(self.open_output_button)
        layout.addWidget(QLabel("Run Details"))
        layout.addWidget(self.status_box)

        group.setLayout(layout)
        return group

    def select_input_wav(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input WAV",
            "",
            "WAV Files (*.wav)"
        )

        if file_name:
            self.input_wav = Path(file_name)
            self.input_label.setText(f"Input WAV: {self.input_wav}")

    def select_output_folder(self) -> None:
        folder_name = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            ""
        )

        if folder_name:
            self.output_dir = Path(folder_name)
            self.output_label.setText(f"Output Folder: {self.output_dir}")

    def open_output_folder(self) -> None:
        """Open the selected output folder in the system file explorer."""

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            os.startfile(self.output_dir)

            self.statusBar().showMessage(
                f"Opened output folder: {self.output_dir}"
            )

        except Exception as exc:
            self.status_box.setText(f"Could not open output folder:\n{exc}")
            self.statusBar().showMessage("Could not open output folder.")

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
        self.status_box.setText(message)
        self.statusBar().showMessage(f"Simulation complete | Output: {result.output_dir}")

        self.sim_thread.quit()
        self.sim_thread.wait()

    def handle_simulation_failed(self, error_message: str) -> None:
        """Handle simulation failure."""

        self.set_running_state(False)
        self.status_box.setText(f"Simulation failed:\n{error_message}")
        self.statusBar().showMessage("Simulation failed.")

        self.sim_thread.quit()
        self.sim_thread.wait()

    def set_running_state(self, is_running: bool) -> None:
        """Update GUI controls and status bar while simulation runs."""

        self.run_button.setEnabled(not is_running)
        self.run_action.setEnabled(not is_running)

        self.progress_bar.setVisible(is_running)

        if is_running:
            self.status_box.setText("Running simulation...\nPlease wait.")
            self.statusBar().showMessage("Running simulation...")
        else:
            self.progress_bar.hide()

    def run_simulation_from_gui(self) -> None:
        if self.input_wav is None:
            self.status_box.setText("Please select an input WAV file first.")
            self.statusBar().showMessage("No input WAV file selected.")
            return
        
        snr_db = self.snr_box.value() if self.use_snr_check.isChecked() else None

        freq_offset = (
            self.freq_offset_box.value()
            if self.use_freq_offset_check.isChecked()
            else None
        )

        tone_jammer_hz = (
            self.tone_jammer_box.value()
            if self.use_tone_jammer_check.isChecked()
            else None
        )

        tone_jammer_power_db = (
            self.tone_jammer_power_box.value()
            if self.use_tone_jammer_check.isChecked()
            else -10.0
        )

        dropout_start = (
            self.dropout_start_box.value()
            if self.use_dropout_check.isChecked()
            else None
        )

        dropout_duration = (
            self.dropout_duration_box.value()
            if self.use_dropout_check.isChecked()
            else 0.0
        )

        dc_i = self.dc_i_box.value() if self.use_dc_offset_check.isChecked() else 0.0

        dc_q = self.dc_q_box.value() if self.use_dc_offset_check.isChecked() else 0.0

        iq_gain_imbalance_db = (
            self.iq_gain_imbalance_box.value()
            if self.use_iq_imbalance_check.isChecked()
            else 0.0
        )

        iq_phase_imbalance_deg = (
            self.iq_phase_imbalance_box.value()
            if self.use_iq_imbalance_check.isChecked()
            else 0.0
        )

        seed = self.seed_box.value() if self.use_seed_check.isChecked() else None

        demod_output = Path("recovered.wav") if self.save_audio_check.isChecked() else None

        config = SimulationConfig(
            input_wav=self.input_wav,
            output_dir=self.output_dir,
            mode=self.mode_box.currentText(),
            snr_db=snr_db,
            freq_offset=freq_offset,
            tone_jammer_hz=tone_jammer_hz,
            tone_jammer_power_db=tone_jammer_power_db,
            dropout_start=dropout_start,
            dropout_duration=dropout_duration,
            dc_i=dc_i,
            dc_q=dc_q,
            iq_gain_imbalance_db=iq_gain_imbalance_db,
            iq_phase_imbalance_deg=iq_phase_imbalance_deg,
            seed=seed,
            demod_output=demod_output,
            save_iq=self.save_iq_check.isChecked(),
            save_plots=self.save_plots_check.isChecked(),
            save_config=True
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
        
def main() -> None:
    app = QApplication(sys.argv)
    window = FMSimGui()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()