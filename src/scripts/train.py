from src.fsp_ms.config import Config
from src.fsp_ms.utils.logger import get_logger
from src.fsp_ms.data.etl import ETL_pipeline
from src.fsp_ms.validation.schema_cleaned import SchemaSales
from src.fsp_ms.features.build_features import BuildFeatures
from src.fsp_ms.validation.scheme_features import SchemaFeatures
from src.fsp_ms.validation.validator import Validator
from src.fsp_ms.data.split import Split
from src.fsp_ms.models.XGB_model import XGB_model

# To run this file use following command from ROOT in console:  ``python -m src.scripts.train`` 
if __name__ == '__main__':
    # Common config for all objects
    config = Config()

    # ETL
    ## Init: etl object and it's logger
    logger_etl = get_logger(config=config, name = "etl", log_file = config.get('log_file_etl'))
    etl = ETL_pipeline(config, logger_etl)
    ## Init: Validator and it's logger
    logger_etl_schema = get_logger(config=config, name ="validation_schema_cleaned"\
                                   , log_file=config.get('validation_schema_cleaned'))
    etl_validator = Validator(logger_etl_schema)
    ### Init: Schema for Validator
    etl_schema = SchemaSales()
    ## Run: etl transformation with transferring validator and validation schema
    etl.run(validator_object = etl_validator, validation_schema = etl_schema, dry_run= False)

    # FE
    logger_fe = get_logger(config=config, name = "build_features", \
                        log_file = config.get('log_file_build_features'))
    build_features = BuildFeatures(config, logger_fe)
    ## Init: Validator and it's logger
    features_validation_logger = get_logger(config=config, name = "validation_schema_features", \
                        log_file = config.get('validation_schema_features'))
    fe_validator = Validator(features_validation_logger)
    ### Init: Schema for Validator
    features_schema = SchemaFeatures()

    build_features.run(validator_object = fe_validator, validation_schema = features_schema, dry_run = False )

    # Split
    
    logger_split = get_logger(config=config, name = "split", \
                            log_file = config.get('log_file_split'))
    split = Split(config, logger_split)
    split.run()

    # Model 

    logger_model = get_logger(config=config, name = "model", log_file= config.get('log_file_model'))

    model = XGB_model(config, logger_model)
    model.train(save = True)
