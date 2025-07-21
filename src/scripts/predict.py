import numpy as np
import pandas as pd
from pathlib import Path
from src.models.XGB_model import XGB_model
from src.config import Config
from src.utils.logger import get_logger 

if __name__ == '__main__':
    # python -m src.scripts.predict
    config = Config()
    logger_predict = get_logger("predict", log_file = config.get('log_file_model'))
    model = XGB_model(config, logger_predict)
    model.predict(load=True,save=True)