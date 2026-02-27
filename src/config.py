from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    ROOT: Path = Path(__file__).resolve().parent.parent
    MODEL_DIR: Path = ROOT / "models" / "xlm_roberta_fear"
    BG_IMAGE: Path = ROOT / "assets" / "ui_bg.png"

    MAX_LENGTH: int = 192
    THRESHOLD: float = 0.55