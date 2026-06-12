from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QSizePolicy,
    QToolButton,
    QMessageBox
)

from fmsim.simulation import SimulationConfig
from fmsim.gui.widgets import (
    NoWheelComboBox,
    NoWheelDoubleSpinBox,
    NoWheelSpinBox,
)


class SettingsPanel(QWidget):
    """Right-side settings panel for the FM Signal Simulator."""
    input_requested = Signal()
    output_requested = Signal()
    run_requested = Signal()
    open_output_requested = Signal()
    
    def __init__(self) -> None:
        super().__init__()

        self.create_widgets()
        self.create_layout()

    def create_widgets(self) -> None:
        '''
        Create all GUI widgets.
        '''

        # Input and Output Widgets
        # ====================================
        self.input_label = QLabel("Input WAV: None selected")
        self.output_label = QLabel("Output Folder: outputs")

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
        self.input_button.clicked.connect(self.input_requested.emit)

        self.output_button = QPushButton("Select Output Folder")
        self.output_button.clicked.connect(self.output_requested.emit)

        self.save_iq_check = QCheckBox("Save IQ Data")
        self.save_iq_check.setChecked(False)

        self.save_plots_check = QCheckBox("Save Plots")
        self.save_plots_check.setChecked(False)

        self.save_audio_check = QCheckBox("Save Recovered Audio")
        self.save_audio_check.setChecked(False)

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
        self.run_button.clicked.connect(self.run_requested.emit)

        self.open_output_button = QPushButton("Open Output Folder")
        self.open_output_button.clicked.connect(self.open_output_requested.emit)

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
    
    def create_layout(self) -> None:
        """Create the full settings panel layout."""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(self.create_input_output_section())
        layout.addWidget(self.create_fm_settings_section())
        layout.addWidget(self.create_impairments_section())
        layout.addWidget(self.create_run_section())
        layout.addStretch()

    def create_help_button(self, title: str, message: str) -> QToolButton:
        """Create a small help button for an impairment setting."""

        button = QToolButton()
        button.setText("ⓘ")
        button.setToolTip(title)
        button.setAutoRaise(True)
        button.setFixedSize(22, 22)
        button.setStyleSheet(
            """
            QToolButton {
                color: #2f80ed;
                font-weight: bold;
                border: none;
                background: transparent;
            }

            QToolButton:hover {
                color: #56a3ff;
            }
            """
        )

        button.clicked.connect(
            lambda: QMessageBox.information(self, title, message)
        )

        return button
    
    def create_checkbox_with_help(self, checkbox: QCheckBox, title: str, message: str) -> QWidget:
        """Create a checkbox row with a small help button."""

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        checkbox.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Preferred,
        )

        layout.addWidget(checkbox)
        layout.addWidget(self.create_help_button(title, message))
        layout.addStretch(1)

        return widget

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
        awgn_help = self.create_checkbox_with_help(
            self.use_snr_check,
            "AWGN",
            (
                "Additive White Gaussian Noise adds random noise to the IQ signal.\n\n"
                "Lower SNR values create a noisier signal.\n"
                "Higher SNR values create a cleaner signal."
            ),
        )
        awgn_form.addRow(awgn_help, self.snr_box)
        outer.addLayout(awgn_form)

        # Frequency Offset
        freq_form = self.make_impairment_form()
        freq_help = self.create_checkbox_with_help(
            self.use_freq_offset_check,
            "Frequency Offset",
            (
                "Frequency offset shifts the signal in frequency.\n\n"
                "This simulates tuner error, oscillator mismatch, or Doppler-like offset."
            ),
        )
        freq_form.addRow(freq_help, self.freq_offset_box)
        outer.addLayout(freq_form)

        # Tone Jammer
        jammer_form = self.make_impairment_form()
        jammer_help = self.create_checkbox_with_help(
            self.use_tone_jammer_check,
            "Tone Jammer",
            (
                "Tone jammer adds a single interfering tone to the IQ signal.\n\n"
                "The frequency controls where the jammer appears.\n"
                "The power controls how strong the jammer is."
            ),
        )
        jammer_form.addRow(jammer_help, self.tone_jammer_box)
        jammer_form.addRow("Jammer Power:", self.tone_jammer_power_box)
        outer.addLayout(jammer_form)

        # IQ Dropout
        dropout_form = self.make_impairment_form()
        dropout_help = self.create_checkbox_with_help(
            self.use_dropout_check,
            "IQ Dropout",
            (
                "IQ dropout removes part of the IQ signal for a selected time range.\n\n"
                "This simulates signal loss, blanking, or a short receiver/data dropout."
            ),
        )
        dropout_form.addRow(dropout_help)
        dropout_form.addRow("Start Time:", self.dropout_start_box)
        dropout_form.addRow("Duration:", self.dropout_duration_box)
        outer.addLayout(dropout_form)

        # DC Offset
        dc_form = self.make_impairment_form()
        dc_help = self.create_checkbox_with_help(
            self.use_dc_offset_check,
            "DC Offset",
            (
                "DC offset adds a constant value to the I and/or Q channel.\n\n"
                "This simulates receiver bias or imperfect IQ hardware calibration."
            ),
        )
        dc_form.addRow(dc_help)
        dc_form.addRow("I Offset:", self.dc_i_box)
        dc_form.addRow("Q Offset:", self.dc_q_box)
        outer.addLayout(dc_form)

        # IQ Imbalance
        iq_form = self.make_impairment_form()
        iq_help = self.create_checkbox_with_help(
            self.use_iq_imbalance_check,
            "IQ Imbalance",
            (
                "IQ imbalance simulates mismatch between the I and Q signal paths.\n\n"
                "Gain error changes the relative amplitude.\n"
                "Phase error changes the angle between I and Q."
            ),
        )
        iq_form.addRow(iq_help)
        iq_form.addRow("Gain Error:", self.iq_gain_imbalance_box)
        iq_form.addRow("Phase Error:", self.iq_phase_imbalance_box)
        outer.addLayout(iq_form)

        # Random Seed
        seed_form = self.make_impairment_form()
        seed_help = self.create_checkbox_with_help(
            self.use_seed_check,
            "Random Seed",
            (
                "A random seed makes noise generation repeatable.\n\n"
                "Using the same seed and same settings should produce the same AWGN result."
            ),
        )
        seed_form.addRow(seed_help, self.seed_box)
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

    def set_input_wav(self, input_wav: Path) -> None:
        """Update the displayed input WAV path."""

        self.input_label.setText(f"Input WAV: {input_wav}")

    def set_output_dir(self, output_dir: Path) -> None:
        """Update the displayed output folder path."""

        self.output_label.setText(f"Output Folder: {output_dir}")

    def set_status_text(self, message: str) -> None:
        """Update the run details box."""

        self.status_box.setText(message)

    def set_running_state(self, is_running: bool) -> None:
        """Enable or disable run controls while simulation is running."""

        self.run_button.setEnabled(not is_running)
        self.open_output_button.setEnabled(not is_running)

    def get_config(self, input_wav: Path, output_dir: Path) -> SimulationConfig:
        """Build a SimulationConfig from the current settings panel values."""

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

        return SimulationConfig(
            input_wav=input_wav,
            output_dir=output_dir,
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
            save_config=True,
        )