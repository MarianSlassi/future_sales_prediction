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
    │   ├── interim/        ← techincal folder, probably redundant
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


⚒️ Base workflow:
    0. save competition data to project/data/raw
    1. project/src/data/        clean.py  (schema runs aotumatically)
    2. project/src/features/    build_features.py (schema runs aotumatically)
    3. project/src/data/        split.py
    4. project/src/models/      train_model.py (optionally)
    5. project/src/models/      predict_model.py


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
        ROOT = Path(__file__).resolve().parent[2]
        sys.path.append(str(ROOT))
        from config import Config
        config = Config()

😇 Utils usage:

    🖇️Logger: 
    from src.utils.logger import get_logger
    logger = get_logger("etl")

    logger.info("Starting etl Process")
    logger.warning("Something strange happened")
    logger.error("Something went wrong")











