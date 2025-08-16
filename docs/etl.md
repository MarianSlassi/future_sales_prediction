# 🧱 ETL_pipeline: Sales Data Preprocessing Module

`ETL_pipeline` is a modular Python class that implements an end-to-end Extract, Transform, Load (ETL) process for historical sales data. It includes built-in logging, outlier handling, date formatting, deduplication, and shop ID normalization. The final dataset is saved in a clean, ready-to-use format such as Parquet.

---

## ✅ Initialization

```python
ETL_pipeline(config, logger)
````

**Arguments:**

* `config`: Config object with already defined proper paths

* `logger`: A configured logging object for tracking pipeline progress and issues.

---

## 🔧 Transformation Methods

### `outliers_filtration(df: pd.DataFrame, column: str) -> pd.DataFrame`

Removes zero and negative values, clips values above the 99th percentile, and creates a binary indicator for clipped rows.

* Logs the number of outliers above and below thresholds.
* Adds a column named `was_{column}_outlier` to mark clipped entries.

### `normalize_shop_ids(df: pd.DataFrame) -> pd.DataFrame`

Replaces known duplicate `shop_id`s using a predefined mapping, then aggregates the data by summing `item_cnt_day` for identical (date, shop, item, price) combinations.

* Ensures no duplicate shop entities remain.

### `date_conversion(sales: pd.DataFrame) -> pd.DataFrame`

Converts the `date` column from `DD.MM.YYYY` format to `datetime`.

### `duplicates_filtration(sales: pd.DataFrame) -> pd.DataFrame`

Removes full row duplicates based on all columns.

* Logs how many duplicates were found and removed.

---

## 🔄 Core Workflow

### `transform(sales: pd.DataFrame) -> pd.DataFrame`

Applies the complete transformation pipeline in the following order:

1. Convert date column to datetime
2. Remove full duplicates
3. Normalize duplicate shop IDs
4. Filter outliers from `item_price`
5. Filter outliers from `item_cnt_day`

Logs the change in dataset size before and after transformation.

### `extract() -> pd.DataFrame`

Reads the raw CSV file from the path specified in `config["sales"]`.

### `load(sales: pd.DataFrame)`

Saves the cleaned DataFrame to a Parquet file at the path `config["cleaned_parquet"]`. Creates the output directory if it doesn’t exist.

---

## 🚀 Run Pipeline

### `run(validator_object=None, validation_schema=None, dry_run=True)`

Orchestrates the full ETL flow:

1. Extract raw data
2. Transform it
3. Optionally validate the cleaned data
4. Save the output (unless `dry_run=True`)

**Arguments:**

* `validator_object`: An object with a `.validate(schema, df, scheme_name)` method
* `validation_schema`: Validation rules (e.g., from Pandera or custom logic)
* `dry_run`: If `True`, skips saving the output

---

## Example Usage

```python
pipeline = ETL_pipeline(config=my_config, logger=my_logger)
pipeline.run(dry_run=False)
```
