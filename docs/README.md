🔭 Project structure:

    project/
    │
    ├── img/              ← for images
    │
    ├── reqirements.txt
    │
    ├── README.MD
    │
    ├── data/
    │   ├── raw/            ← dicts + submission_data + sales_train.csv (⚠️check below for expected order)
    │   ├── interim/        ← techincal folder, redundant but remained in case of need (⚠️ check below for data explanation)
    │   ├── cleaned/        ← cleaned.parquet
    │   ├── features/       ← final_df
    │   ├── processed/      ← train/val/test
    │   ├── predictions/    ← output.csv
    │   └── logs/
    │
    ├── models/
    │   └── model.pkl
    │
    ├── notebooks/
    │   └── all_notebooks.ipynb
    │
    ├── src/
    |   ├── config.py
    |   |
    │   ├── data/
    │   │   ├── etl.py
    │   │   └── split.py
    │   ├── features/
    │   │   └── build_features.py
    │   ├── validation/
    │   │   ├── schema_cleaned.py     ← for data after cleaning
    │   │   ├── schema_features.py    ← for data after features engineering
    │   │   └── validate.py           ← to chose which schema to use
    │   ├── models/
    │   │   ├── train_model.py
    │   │   └── predict_model.py
    │   └── utils/
    │       ├── helpers.py
    │       └── logger.py


    🐢How to save raw data:
        raw/
        ├── dicts/
        │   ├── item_categories.csv
        │   ├── items.csv
        │   └── shops.csv
        ├── submission_data/
        │   ├── sample_submission.csv
        │   └── test.csv
        └── sales_train.csv


⚒️ **Base workflow (run files in the following order):**
1. `project/data/raw`      ⚠️ before starting save competition data in this directory
2. `project/src/data/clean.py`          (schema runs automatically)
3. `project/src/features/build_features.py`     (schema runs automatically)
4. `project/src/data/split.py`
5. `project/src/models/train_model.py`       (optionally)
6. `project/src/models/predict_model.py`
⚠️With current version we don't support running modules separatelly (as files), all that happens inside of run_all.py.
You need to run it as module. To do that you need to set for interpretator ROOT of the project as a starting directory.
Should be done with:
1. `cd \project`
2. `python -m src.scripts.run_all`
### How everything works?
The architecture of the project is built on Dependency Injection (DI). Whenever you initiate any script—for example, to clean raw data—you should pass both the config object and the logger object into the constructor of the pipeline class.

When running any transformation script using the `.run()` method, you must also pass a validation schema object as an argument and schema itslef. And last but not least, when defining a validation schema instance, the logger must also be passed in as an argument. You can check how this is done in project(package) main README in root, when the whole project run as package at remote environemnt. Or you can go to the project src.scripts.train.py and check right there how it's done.

If any transformation step fails schema validation, the entire script execution will be halted. To avoid this, you can set the `strict=False` parameter in the schema. Additionally, all schemas support input DataFrame modification, since every call to `.validate()` returns a new DataFrame. The logic for assigning these modified DataFrames is implemented in the `.output()` methods of transformation scripts such as `etl.py` and `build_features.py`.

Our system also supports running `build_features.py` and `etl.py` scripts without producing any output DataFrame — this can be done using the `dry_run=False` flag.
Example: you can call the BuildFeatures object like this:
`BuildFeatures.run(fe_validator, dry_run=False)`.




### Additional:

📂 Directories/paths managment by config in root:
We choose to run all scripts from root by default, so every module including config might be run from root of the project. And it still might be imported as following:

        from  src.fsp_ms.config import Config
        config = Config()

😇 Utils usage:

    🖇️Logger:
    from src.fsp_ms.utils.logger import get_logger
    logger = get_logger("etl", config.get('log_file_name')) # Technically you can skip second argument, then it will be writen in file with current date. All log files managed through Config

    logger.info("Starting etl Process")
    logger.warning("Something strange happened")
    logger.error("Something went wrong")









### 📁 Data: Interim

🪵 **Interim** — contains data exported to support transformations in notebooks.

- `data_checkpoint_full_df.parquet`
  ⤷ At the feature engineering notebook, some transformations are time-consuming. This file stores an intermediate result to speed up debugging — useful when rerunning cells from the beginning.

- `full_df_final.csv`
  ⤷ A snapshot of the final observations after transformations in the feature engineering notebooks. Used primarily to develop validation pipelines.

- `sales_for_eda.parquet`
  ⤷ Created at the end of the DQC notebook. Unlike the cleaned version, it includes values from dicts for visualization and data consistency checks.
  ⤷ Later, the same transformation logic was moved into the EDA notebook, but a commented-out line in DQC remains for reference:
  `sales.to_parquet(config.get('sales_for_eda'), engine='pyarrow')`</br>
  ⤷ You can uncomment line above in DQC, as well as import line in EDA `sales = pd.read_parquet(config.get('sales_for_eda'))` and trasform data with notebook. In this case comment out "Merging Dicts" block in EDA.
