import numpy as np
import pandas as pd

from pathlib import Path

from src.config import Config
from src.utils.logger import get_logger
from src.data.etl import ETL_pipeline
from src.validation.schema_cleaned import SchemaSales
from src.features.build_features import BuildFeatures
from src.validation.scheme_features import SchemaFeatures
from src.data.split import Split
from src.models.XGB_model import XGB_model

# To run this file use following command from ROOT in console:  ``python -m src.scripts.predict`` 
if __name__ == '__main__':
    config = Config()

    # ETL
    logger_etl = get_logger("etl", log_file = config.get('log_file_etl'))
    etl = ETL_pipeline(config, logger_etl)
    logger_etl_schema = get_logger(name="validation_schema_cleaned"\
                                   , log_file=config.get('validation_schema_cleaned'))
    etl_validator = SchemaSales(logger_etl_schema)

    etl.run_etl(validator_object = etl_validator, dry_run= False)

    # FE
    logger_fe = get_logger(name = "build_features", \
                        log_file = config.get('log_file_build_features'))
    build_features = BuildFeatures(config, logger_fe)

    features_validation_logger = get_logger(name = "validation_schema_features", \
                        log_file = config.get('validation_schema_features'))
    fe_validator = SchemaFeatures(features_validation_logger)

    build_features.run(validator_object = fe_validator, dry_run = False )

    # Split
    
    logger_split = get_logger(name = "split", \
                            log_file = config.get('log_file_split'))
    split = Split(config, logger_split)
    split.run()

    # Model 

    logger_model = get_logger(name = "model", log_file= config.get('log_file_model'))

    model = XGB_model(config, logger_model)
    model.train(save = True)

    
    # Class: model.prediction() / model.inference() / model.train() 
