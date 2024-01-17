from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor

def load_detectron2_model(model_path, config_path):
    cfg = get_cfg()
    cfg.set_new_allowed(True)  
    cfg.merge_from_file(config_path)  # Use your custom config file directly
    cfg.MODEL.DEVICE = 'cpu' 
    cfg.MODEL.WEIGHTS = model_path
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # Adjust threshold as needed
    predictor = DefaultPredictor(cfg)
    return predictor
