import json
from pathlib import Path

import numpy as np

def save_iq_npz(
        path: str,
        iq: np.ndarray,
        fs_iq: int,
        metadata: dict | None = None,
    ) -> None:

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if metadata is None:
        metadata = {}

    np.savez(
        path, 
        iq=iq.astype(np.complex64),
        fs_iq=fs_iq,
        metadata=json.dumps(metadata)
    )

def load_iq_npz(path: str) -> tuple[np.ndarray, int, dict]:
    
    data = np.load(path, allow_pickle=True)

    iq = data["iq"]
    fs_iq = int(data["fs_iq"])

    metadata = {}
    if "metadata" in data:
        metadata = json.loads(str(data["metadata"]))

    return iq, fs_iq, metadata