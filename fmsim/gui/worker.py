from PySide6.QtCore import QObject, Signal, Slot

from fmsim.simulation import SimulationConfig, run_simulation

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