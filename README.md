This is a simple librarary to transofrm data, train model, and make predictions.
----
If you are using collab or kaggle notebook, please import this package as:
---
!pip install \
  --index-url https://test.pypi.org/simple/ \\\
  --extra-index-url https://pypi.org/simple \\\
  fsp-ms
</br></br>*Or you can use it locally .venv:*
</br>uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple fsp-ms


# Google Collab
Before starting you will need to add raw data in the appropriate path in default order. You can initialise `data/` directory in any place just with config and trying to run a project - it will fail first run, but will create the `data/` . So then you add all predict future sales files there. You can redefine default paths with config
</br></br>
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
And run the following code
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


### Dev info:
To upload package new version go to root and write to console:
 - `Remove-Item -Recurse -Force .\dist\`
 - `py -m build`
 - `py -m twine upload --repository testpypi dist/* --verbose`


### When commit changes, don't forget to:
 - Activate .venv to pass pre-commit checks
 - Use command `pre-commit run --all-files`

### How to use bump2version:
 - If you want patch package just use `bumbp2version patch`, or
 - `bump2version minor`, or
 - `bump2version major`
Don't need to be explained the format is "major.minor.patch" version



### Collab free version might crash because of limit for 12GB RAM
We tried to light weighted our pipline for this, couldn't say it helped a lot, but at least from this you can find out how to work further in case of need. All apened due to expanding window algorithm cost of RAM with copying several massive `full_df` data frames to RAM simultaniously in the single loop. Even garbage collector didn't help. Since all needed to be handled at once (simultaniously)
PS: probably we can make every loop to be called through function siparatelly.
Here is the solution:

```python
!pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  fsp-ms
```
```python
import gc
import pandas as pd
import fsp_ms
```
```python
from fsp_ms import Config, get_logger, Validator, ETL_pipeline, SchemaSales, BuildFeatures, SchemaFeatures , Split , XGB_model
from pathlib import Path
colab_base_dir = Path("/content/data")

# Common config for all objects
config = Config(base_dir=colab_base_dir)
```
```python
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

del logger_etl, etl, logger_etl_schema, etl_validator, etl_schema
gc.collect()

```
```python
# FE
logger_fe = get_logger(config=config,name = "build_features", \
                    log_file = config.get('log_file_build_features'))
build_features = BuildFeatures(config, logger_fe)
## Init: Validator and it's logger
features_validation_logger = get_logger(config=config,name = "validation_schema_features", \
                    log_file = config.get('validation_schema_features'))
fe_validator = Validator(features_validation_logger)
### Init: Schema for Validator
features_schema = SchemaFeatures()



dry_run = False
```
```python
# .run() method decomposed:
build_features.logger.info('\n=== FEATURE ENGINEERING process started ===\n')

#sales, items, items_categories, shops, test = build_features.extract()
full_df = build_features.full_schema(*build_features.extract())

full_df = build_features.first_month(full_df)
full_df = build_features.expanding_window(full_df)
full_df = build_features.year_month(full_df)
full_df.to_parquet(config.get('interim_parquet'))

```
```python
full_df = pd.read_parquet(config.get('interim_parquet'))
full_df = build_features.lags(full_df)
full_df = build_features.deltas(full_df)

full_df = build_features.check_leakage(full_df)# can be moved inside build_features.output() or build_features.transform()

if fe_validator and features_schema:
    full_df = fe_validator.validate(schema = features_schema, df = full_df, scheme_name='feaures_engineering')
else:
    build_features.logger.warning('!!! No validation schema passed to build_features pipeline\
                        The pipeline performed transformations without validation.')

if not dry_run:
    build_features.output(full_df)
build_features.logger.info("\n=== FEATURE ENGINEERING process finished ===\n\n\n\n\n")
```

```python
del build_features
gc.collect()
```
```python
# Split

logger_split = get_logger(config=config,name = "split", \
                        log_file = config.get('log_file_split'))
split = Split(config, logger_split)
split.run()

# Model

logger_model = get_logger(config=config,name = "model", log_file= config.get('log_file_model'))

model = XGB_model(config, logger_model)
model.train(save = True)
```
