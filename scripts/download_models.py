"""
Download pre-trained models for ADA compliance assessment
"""

import requests
from pathlib import Path
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_file(url: str, destination: Path):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as f, tqdm(
        desc=destination.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))


def main():
    """Download all required models"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # YOLOv8 model (using base model as example)
    # In production, this would be your fine-tuned model
    model_url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8x.pt"
    model_path = models_dir / "yolov8x-ada.pt"
    
    if not model_path.exists():
        logger.info("Downloading YOLOv8 model...")
        try:
            # For demo, we'll just download the base YOLOv8 model
            from ultralytics import YOLO
            model = YOLO('yolov8x.pt')
            model.save(str(model_path))
            logger.info(f"Model saved to {model_path}")
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            logger.info("Please manually download the model or train your own")
    else:
        logger.info(f"Model already exists: {model_path}")
    
    logger.info("Model setup complete!")


if __name__ == "__main__":
    main()
