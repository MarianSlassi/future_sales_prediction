

---


# 🧠 Feature Engineering Pipeline: Retail Sales Forecasting

## 📜 Overview

This script builds an advanced, memory-efficient, and leakege-free feature engineering pipeline for the [Russian Retail Sales dataset](https://www.kaggle.com/competitions/competitive-data-science-predict-future-sales/). It extracts raw data, performs multiple transformations, handles outliers, builds useful statistical aggregations, encodes categorical features, and finally outputs a `full_df.parquet` file ready for ML models.

All logging is handled with a custom logger. The pipeline is modular, object-oriented, and reproducible.

---

## 📦 Dependencies

Make sure these libraries are installed:

```bash
pip install pandas numpy pyarrow tqdm
````

For visualizations and extended analysis, these might be useful but **not required here**:

```bash
pip install matplotlib seaborn plotly
```

If you're running from a structured project, you’ll also need your `config.py` and `src/utils/logger.py` available and importable. Adjust your `PYTHONPATH` accordingly (done automatically in script with `sys.path.append(...)`).

---

## 🗂️ Project Structure Assumption

```
project/
│
├── data/
│   ├── raw/                  <- raw CSV/Parquet files
│   └── interim/              <- outputs like full_df.parquet
│
├── src/
│   └── utils/
│       └── logger.py         <- provides get_logger()
│
├── config.py                 <- provides Config class to fetch paths
├── scripts/
│   └── build_features.py     <- you are here
```

---

## 🧩 Class Structure

### `BuildFeatures`

Main feature engineering class.

#### Constructor

```python
BuildFeatures(config: Config)
```

Initializes config.

---

### 📥 Data Extraction

```python
extract()
```

Loads cleaned sales data, item dicts, shop dicts, item categories, and test set.

---

### 🧱 Feature Engineering Pipeline

#### Schema Generation

```python
blank_schema(sales)
```

Creates a full schema of (month, shop\_id, item\_id) combinations.

#### Aggregation

```python
sales_aggregation(sales)
```

Aggregates sales to monthly target level, flags outliers.

#### Merging

```python
merge_df_aggregated(df, aggregated)
concat_test(full_df, test)
merge_full_df_dicts(full_df, items, items_categories, shops)
merge_sales_dicts(sales, items, items_categories, shops)
```

Combines all information into a single DataFrame for training.

---

### 📊 Feature Creation

```python
month_aggregations(full_df, sales)
```

Adds aggregated target statistics grouped by various entities.

```python
first_month(full_df)
```

Flags items appearing for the first time.

```python
expanding_window(full_df)
```

Creates leakege-free expanding window features.

```python
year_month(full_df)
```

Adds month and year features.

```python
was_in_test(full_df, test)
```

Flags test items and shops.

```python
lags(full_df)
```

Creates lagged features with configurable shift range.

```python
deltas(full_df)
```

Computes deltas and linear extrapolations from lagged features.

```python
downcast_dtypes(full_df)
```

Reduces memory usage by downcasting datatypes.

---

### 🔍 Leakege Control

```python
check_leakege(full_df)
```

Drops features that leak test set information or are constant in the test month (month 34).

---

### 💾 Output

```python
output(full_df)
```

Saves final `full_df` to Parquet with path from config.

---

### 🧵 Main Pipeline

```python
run()
```

Full pipeline: extraction → schema → feature engineering → leakege check → export.

---

## 🚀 Run Script

To execute:

```bash
python build_features.py
```

---

## 📘 Logging

All actions are logged to the file defined in:

```python
config.get('log_file_build_features')
```

You can customize the logger using `get_logger(name, log_file)` in `src/utils/logger.py`.

---

## 🧠 Notes

* Lags and deltas are added for both targets and outlier flags.
* Memory usage is monitored throughout with `size_memory_info`.
* Modularized into reusable functions and full pipeline methods (`full_schema`, `transform`, etc.)
* `test` month is hardcoded as `34` based on Kaggle challenge structure.

---

## ✨ Tip for Users

If you're iterating/debugging inside a notebook, extract methods like `.extract()`, `.full_schema()` and `.transform()` to run them independently, step-by-step.

---

## 🧼 TODO

* Integrate DVC for reproducible pipeline steps
* Optional: Replace raw loops with vectorized pandas (where feasible)



```

RAW:
Methods:
- extract()
- full_schema()
- month_aggregations()
- first_month()
- expanding_window()
- year_month()
- was_in_test()
- downcast_dtype()
- lags()
- deltas()
- output()




Functions: 
- size_memmory_info()


Syntax:
Every method represents a heading from notebook. Every sub heading devvided by two \n. Every cell devided by one \n

Architecture:
Better to store variables locally across methods and keep instnce variables of object as much clean as possible, since we have big enough dataframe for memmory malloc or overflow. Some operations provided with function syntax of the file to import in case of need (probable will remove them to helper.py)





----------
Here's a full documentation for your script in `.md` format — suitable for your repo, cleanly structured and markdown-beautiful.