# backend-ml/ml_model.py
# YOLO model singleton.
# Import this module and access `ml_model.model` (not `from ml_model import model`)
# so that mutations made by load_model() are visible everywhere.

from pathlib import Path
from ultralytics import YOLO

model: YOLO | None = None


def load_model() -> None:
    """Load YOLO model from disk. Called once at FastAPI startup."""
    global model
    model_path = Path("models/best.pt")
    if not model_path.exists():
        print("!!!!!WARNING: models/best.pt not found!!!!!")
        print("   Place your trained model at backend-ml/models/best.pt to enable detection.")
        model = None
        return
    model = YOLO(str(model_path))
    print("- - - - - YOLO model loaded - - - - ")
