from src.fsp_ms.models.XGB_model import XGB_model
from src.fsp_ms.config import Config
from src.fsp_ms.utils.logger import get_logger 

if __name__ == '__main__':
    # python -m src.scripts.predict
    config = Config()
    logger_predict = get_logger("predict", log_file = config.get('log_file_model'))
    model = XGB_model(config, logger_predict)
    model.predict(load=True,save=True)