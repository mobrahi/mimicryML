# backend/config.py

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models" / "pretrained_models"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

# Style transfer settings
AVAILABLE_STYLES = {
    "vangogh": {
        "name": "Van Gogh - Starry Night",
        "description": "Swirling brushstrokes and vibrant colors"
    },
    "picasso": {
        "name": "Picasso - Cubism",
        "description": "Geometric shapes and abstract forms"
    },
    "monet": {
        "name": "Monet - Impressionism",
        "description": "Soft colors and light effects"
    },
    "kandinsky": {
        "name": "Kandinsky - Abstract",
        "description": "Bold colors and abstract patterns"
    }
}

# Processing settings
MAX_IMAGE_SIZE = 512  # Max dimension for processing
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Model settings
USE_GPU = False  # Set to True if you have GPU
NUM_ITERATIONS = 500  # For optimization-based style transfer
CONTENT_WEIGHT = 1.0
STYLE_WEIGHT = 1000.0