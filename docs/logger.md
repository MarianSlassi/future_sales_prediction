# 🧾 Custom Logger: `get_logger`

## 📌 Purpose

The `get_logger` function returns a ready-to-use logger instance with a specified name. It logs messages both to a file and to the console. If no file is specified, a unique file name is generated based on the logger name and current timestamp.

## 🛠️ Usage

```python
from utils.logger import get_logger

logger = get_logger("train_pipeline")
logger.info("Training started")
```
## ⚙️ Parameters

* `name (str)`: Name of the logger. Appears in the log output.
* `log_file (str, optional)`: Custom log file name (no path). If not provided, a file is created with a timestamp in the logs directory.
  
## 📁 Log Directory

The log file is saved in the directory defined in your config:

```python
LOG_DIR = config.get('logs_dir')
```

If the folder doesn’t exist, it is created automatically with all necessary parent folders.

If no log_file Path added, file will be created with logger name:

```
logs/train_pipeline_20250705_140311.log
```

## ✅ Output Sample

```
2025-07-05 14:06:12 | INFO | data_cleaning | Dropped 104 rows with missing prices
2025-07-05 14:06:14 | INFO | train_model | XGBoost training finished. RMSE: 1.084
```
Console output has the same structure as in logs files



## 🧠 Features

* Automatically avoids duplicate handlers if the logger is reused.
* Logs are formatted as:

  ```
  YYYY-MM-DD HH:MM:SS | LEVEL | LOGGER NAME | MESSAGE
  ```
* Works in modular projects and avoids duplicated output across modules.

## 🧪 Typical Usage Examples

Used for logging:

* Model training progress
* Data preprocessing diagnostics
* Evaluation metrics
* Runtime exceptions and debugging


---