from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
    QColorDialog,
)


class PlotAppearanceDialog(QDialog):
    """Dialog for changing plot appearance settings."""

    COLOR_OPTIONS = {
        "White": "white",
        "Light Gray": "#f0f0f0",
        "Soft Blue": "#d9eaf7",
        "Soft Green": "#e8f5e9",
        "Soft Yellow": "#fff3cd",
        "Soft Red": "#f8d7da",
        "Dark Gray": "#1e1e1e",
        "Charcoal": "#151a1f",
        "Midnight Blue": "#0b1020",
        "Google Dark": "#202124",
        "Black": "black",
    }

    def __init__(self, current_background: str, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Plot Appearance")
        self.setMinimumWidth(360)

        self.selected_color = current_background

        self.background_box = QComboBox()

        for name, color_value in self.COLOR_OPTIONS.items():
            self.background_box.addItem(name, color_value)

        index = self.find_color_index(current_background)
        if index >= 0:
            self.background_box.setCurrentIndex(index)

        self.background_box.currentIndexChanged.connect(self.update_selected_color)

        self.custom_color_button = QPushButton("Custom Color...")
        self.custom_color_button.clicked.connect(self.choose_custom_color)

        form = QFormLayout()
        form.addRow("Background Color:", self.background_box)
        form.addRow("", self.custom_color_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def find_color_index(self, color: str) -> int:
        """Find a dropdown index by stored color value."""

        for index in range(self.background_box.count()):
            if self.background_box.itemData(index) == color:
                return index

        return -1

    def update_selected_color(self) -> None:
        """Update selected color from preset box."""

        self.selected_color = self.background_box.currentData()

    def choose_custom_color(self) -> None:
        """Open a color picker for custom plot background colors."""

        initial_color = QColor(self.selected_color)

        if not initial_color.isValid():
            initial_color = QColor("white")

        color = QColorDialog.getColor(
            initial_color,
            self,
            "Choose Plot Background Color",
        )

        if color.isValid():
            hex_color = color.name()
            self.selected_color = hex_color

            label = f"Custom ({hex_color})"

            existing_index = self.find_color_index(hex_color)
            if existing_index == -1:
                self.background_box.addItem(label, hex_color)
                existing_index = self.background_box.count() - 1

            self.background_box.setCurrentIndex(existing_index)

    def selected_background(self) -> str:
        """Return the selected plot background color."""

        return self.selected_color