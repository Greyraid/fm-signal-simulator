import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    """Return the correct resource path in development and packaged builds."""

    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path