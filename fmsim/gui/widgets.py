from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QSpinBox

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