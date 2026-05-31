from pathlib import Path
import sys

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QComboBox,
    QDoubleSpinBox,
    QCheckBox,
    QTextEdit,
    QSpinBox,
    QScrollArea
)

from fmsim.simulation import SimulationConfig, run_simulation

class FMSimGui(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.input_wav: Path | None = None
        self.output_dir: Path = Path("outputs")

        self.setWindowTitle("FM Signal Simulator")
        self.resize(650, 650)

        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # Input and Output Buttons
        # ====================================
        self.input_label = QLabel("Input WAV: None selected")
        self.output_label = QLabel(f"Output Folder: {self.output_dir}")

        input_button = QPushButton("Select Input WAV")
        input_button.clicked.connect(self.select_input_wav)

        output_button = QPushButton("Select Output Folder")
        output_button.clicked.connect(self.select_output_folder)

        layout.addWidget(self.input_label)
        layout.addWidget(input_button)

        layout.addWidget(self.output_label)
        layout.addWidget(output_button)

        # Mode Selection
        # =======================================
        self.mode_box = QComboBox()
        self.mode_box.addItems(["wbfm", "nbfm"])

        layout.addWidget(QLabel("FM Mode"))
        layout.addWidget(self.mode_box)

        # SNR Selection
        # ========================================
        self.snr_box = QDoubleSpinBox()
        self.snr_box.setRange(-50.0, 100.0)
        self.snr_box.setValue(20.0)
        self.snr_box.setSuffix(" dB")

        self.use_snr_check = QCheckBox("Add AWGN")
        self.use_snr_check.setChecked(True)

        layout.addWidget(self.use_snr_check)
        layout.addWidget(self.snr_box)

        # Frequency Offset Selection
        # ========================================
        self.freq_offset_box = QDoubleSpinBox()
        self.freq_offset_box.setRange(-100_000.0, 100_000.0)
        self.freq_offset_box.setValue(0.0)
        self.freq_offset_box.setSuffix(" Hz")

        self.use_freq_offset_check = QCheckBox("Add Frequency Offset")

        layout.addWidget(self.use_freq_offset_check)
        layout.addWidget(self.freq_offset_box)

        # Jammer Selection
        # ===========================================
        self.tone_jammer_box = QDoubleSpinBox()
        self.tone_jammer_box.setRange(0.0, 100_000.0)
        self.tone_jammer_box.setValue(25_000.0)
        self.tone_jammer_box.setSuffix(" Hz")

        self.use_tone_jammer_check = QCheckBox("Add Tone Jammer")
        
        layout.addWidget(self.use_tone_jammer_check)
        layout.addWidget(self.tone_jammer_box)

        self.tone_jammer_power_box = QDoubleSpinBox()
        self.tone_jammer_power_box.setRange(-100.0, 20.0)
        self.tone_jammer_power_box.setValue(-10.0)
        self.tone_jammer_power_box.setSuffix(" dB")

        layout.addWidget(QLabel("Tone Jammer Power"))
        layout.addWidget(self.tone_jammer_power_box)

        # Dropout Selection
        # =============================================
        self.use_dropout_check = QCheckBox("Add IQ Dropout")

        self.dropout_start_box = QDoubleSpinBox()
        self.dropout_start_box.setRange(0.0, 999.0) #change this to change with the length of the audio
        self.dropout_start_box.setValue(2.0)
        self.dropout_start_box.setSuffix(" s")

        self.dropout_duration_box = QDoubleSpinBox()
        self.dropout_duration_box.setRange(0.0, 999.0)
        self.dropout_duration_box.setValue(0.25)
        self.dropout_duration_box.setSuffix(" s")

        layout.addWidget(self.use_dropout_check)
        layout.addWidget(QLabel("Dropout Start"))
        layout.addWidget(self.dropout_start_box)
        layout.addWidget(QLabel("Dropout Duration"))
        layout.addWidget(self.dropout_duration_box)

        # DC Offset Selection
        # =============================================
        self.use_dc_offset_check = QCheckBox("Add DC Offset")

        self.dc_i_box = QDoubleSpinBox()
        self.dc_i_box.setRange(-10.0, 10.0)
        self.dc_i_box.setValue(0.0)

        self.dc_q_box = QDoubleSpinBox()
        self.dc_q_box.setRange(-10.0, 10.0)
        self.dc_q_box.setValue(0.0)

        layout.addWidget(self.use_dc_offset_check)
        layout.addWidget(QLabel("DC Offset I"))
        layout.addWidget(self.dc_i_box)
        layout.addWidget(QLabel("DC Offset Q"))
        layout.addWidget(self.dc_q_box)

        # IQ Imbalance Selection
        # =============================================
        self.use_iq_imbalance_check = QCheckBox("Add IQ Imbalance")

        self.iq_gain_imbalance_box = QDoubleSpinBox()
        self.iq_gain_imbalance_box.setRange(-20.0, 20.0)
        self.iq_gain_imbalance_box.setValue(0.0)
        self.iq_gain_imbalance_box.setSuffix(" dB")

        self.iq_phase_imbalance_box = QDoubleSpinBox()
        self.iq_phase_imbalance_box.setRange(-45.0, 45.0)
        self.iq_phase_imbalance_box.setValue(0.0)
        self.iq_phase_imbalance_box.setSuffix(" deg")

        layout.addWidget(self.use_iq_imbalance_check)
        layout.addWidget(QLabel("IQ Gain Imbalance"))
        layout.addWidget(self.iq_gain_imbalance_box)
        layout.addWidget(QLabel("IQ Phase Imbalance"))
        layout.addWidget(self.iq_phase_imbalance_box)

        # Seed Selection
        # =============================================
        self.use_seed_check = QCheckBox("Use Random Seed")
        self.seed_box = QSpinBox()
        self.seed_box.setRange(0, 999)
        self.seed_box.setValue(123)

        layout.addWidget(self.use_seed_check)
        layout.addWidget(QLabel("Seed"))
        layout.addWidget(self.seed_box)

        # Save IQ Selection
        # =============================================
        self.save_iq_check = QCheckBox("Save IQ Data")
        self.save_iq_check.setChecked(False)
        layout.addWidget(self.save_iq_check)

        # Save Plots Selection
        # =============================================
        self.save_plots_check = QCheckBox("Save Plots")
        self.save_plots_check.setChecked(True)

        self.save_audio_check = QCheckBox("Save Recovered Audio")
        self.save_audio_check.setChecked(True)

        layout.addWidget(self.save_plots_check)
        layout.addWidget(self.save_audio_check)

        # Run Simulation Button
        # =========================================
        run_button = QPushButton("Run Simulation")
        run_button.clicked.connect(self.run_simulation_from_gui)

        layout.addWidget(run_button)

        # Status Box
        # ==========================================
        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setMinimumHeight(150)
        layout.addWidget(self.status_box)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
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

    def run_simulation_from_gui(self) -> None:
        if self.input_wav is None:
            self.status_box.setText("Please select an input WAV file first.")
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

        try:
            result = run_simulation(config)
        except Exception as exc:
            self.status_box.setText(f"Simulation failed:\n{exc}")
            return
        
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

        self.status_box.setText(message)
    
def main() -> None:
    app = QApplication(sys.argv)
    window = FMSimGui()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()