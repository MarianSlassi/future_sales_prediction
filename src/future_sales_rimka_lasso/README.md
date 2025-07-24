This is a simple librarary to transofrm data, train model, and make predictions.
If you using collab or kaggle notebook, please import this package as 
---
!pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  fse-rimka-lasso
</br></br>*Or you can use with activated .venv:*
</br>uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple fse-rimka-lasso


# Google Collab
To run project in google collab save raw data to /content/data as following:
```
    🐢How to save raw data: 
    content/
        └──data/
            └──01_raw/
                ├── dicts/
                │   ├── item_categories.csv
                │   ├── items.csv
                │   └── shops.csv
                ├── submission_data/
                │   ├── sample_submission.csv
                │   └── test.csv
                └── sales_train.csv
```
And run folling code
```
import gc

from fse_rimka_lasso import Config, get_logger, Validator, ETL_pipeline, SchemaSales, BuildFeatures, SchemaFeatures , Split , XGB_model
from pathlib import Path
colab_base_dir = Path("/content/data")

# Common config for all objects
config = Config(base_dir=colab_base_dir)

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

del logger_etl, etl, logger_etl_schema, etl_validator, etl_schema
gc.collect()
```
### New cell
```
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

del build_features
gc.collect()

# Split

logger_split = get_logger(config=config, name = "split", \
                        log_file = config.get('log_file_split'))
split = Split(config, logger_split)
split.run()

# Model 

logger_model = get_logger(config=config, name = "model", log_file= config.get('log_file_model'))

model = XGB_model(config, logger_model)
model.train(save = True)

```