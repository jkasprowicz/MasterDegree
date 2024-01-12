# utils.py
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
import cv2

def perform_inference(image_path):
    # Your Detectron2 inference logic here
    # ...

    # Dummy result for illustration
    inference_results = {
        'count': 42,
        'bounding_boxes': [(x1, y1, x2, y2), ...],
        # Add other relevant information
    }

    return inference_results
