🔭 Project structure:

    project/
    │
    ├── config.py
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


🏗️ Architecture imporvements:
    -add local interpretator - uv, poetry

📂 Directories/paths managment by config in root:

    Notebooks:
        from pathlib import Path
        import sys
        ROOT = Path().resolve().parent
        sys.path.append(str(ROOT))
        from config import Config
        config = Config()

    Scripts:
        from pathlib import Path
        import sys
        ROOT = Path(__file__).resolve().parents[2]
        sys.path.append(str(ROOT))
        from config import Config
        config = Config()

😇 Utils usage:

    🖇️Logger: 
    from src.utils.logger import get_logger
    logger = get_logger("etl", config.get('log_file_name')) # You can skip second argument. All log files managed through Config

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










