## 📁 `build_features.py` — Feature Engineering Pipeline

### 📌 Purpose

This script builds the final feature set `full_df` using cleaned sales data and associated lookup tables (`items`, `shops`, `item_categories`, and the `test` set). It constructs a machine learning-ready dataset with aggregations, lags, binary flags, delta features, and leakage handling. The final output is saved as a `.parquet` file.

---

### 🧩 Main Class: `BuildFeatures`

#### `__init__(config, logger)`

Initializes the pipeline with the configuration object and logger instance.

---

### 🔍 Step 1: Data Extraction

#### `extract()`

Loads raw datasets:

* `sales`: cleaned transactional data
* `items`, `shops`, `item_categories`: reference dictionaries
* `test`: the test dataset for November 2015 (missing target)

---

### 🏗 Step 2: Schema Construction

#### `blank_schema(sales)`

Generates a complete monthly item/shop/item\_id grid (`full_df`) for all observed combinations in `sales`.

#### `sales_aggregation(sales)`

Aggregates sales per month: average `item_price`, total `item_cnt_day`, and flags for price/count outliers.

#### `merge_df_aggregated(df, aggregated)`

Merges the blank schema with the aggregated monthly sales.

#### `concat_test(full_df, test)`

Appends the test set to `full_df` by assigning it `date_block_num = 34`.

---

### 🧠 Step 3: Feature Enrichment

#### `encode_dicts(...)`

Encodes categorical fields into numerical codes:

* `item_category_name` → `general_item_category_name`
* `shop_name` → `city`

Text columns are dropped.

#### `merge_full_df_dicts(...)`

Joins `items`, `shops`, and `item_categories` to `full_df`.

#### `merge_sales_dicts(...)`

Adds encoded reference data to `sales`, for use in groupby aggregations.

#### `month_aggregations(...)`

Computes aggregations (`sum`, `mean`) of the target across groups like:

* `item_id`, `shop_id`, `item_category_id`, `general_item_category_name`, `city`.

#### `was_in_test(...)`

Adds binary flags indicating whether each `shop_id` and `item_id` is present in the `test` set.

#### `first_month(...)`

Adds flags marking the first appearance of each item in the timeline.

#### `expanding_window(...)`

Creates leak-free expanding window features (mean and max of target) for:

* `item_id`, `shop_id`, `item_id + shop_id`

#### `year_month(...)`

Adds `year` and `month` as separate features from `date_block_num`.

---

### 📉 Step 4: Lags, Deltas & Cleanup

#### `lags(full_df, additional)`

Generates lag features for `target` and optional fields over 1, 2, 3, and 12 months.

#### `deltas(full_df, columns_to_delta)`

Computes simple deltas between lag features and naive forecasts based on them.

#### `check_leakege(full_df)`

Removes columns that are always zero in the final test month (`date_block_num == 34`).
This ensures no accidental leakage from training into test.

#### `downcast_dtypes(...)`

Downcasts `float64` to `float32` and `int64` to `int32` to reduce memory footprint.

---

### 💾 Step 5: Output

#### `output(full_df)`

Applies downcasting and saves `full_df` to a `.parquet` file. Logs memory usage and path.

---

### ▶ Main Pipeline Execution

#### `run(validator_object=None, dry_run=True)`

Runs the full pipeline:

* Builds the schema
* Applies transformations and enrichment
* Optionally validates with a `Pandera` schema
* Saves output if `dry_run=False`

---

### 🧪 Manual CLI Debug (Entry Point)

```python
if __name__ == '__main__':
    config = Config()
    logger = get_logger(...)
    build_features = BuildFeatures(config, logger)
    validator = SchemaFeatures(logger)
    build_features.run(validator_object=validator, dry_run=False)
```

---

### 🧼 Design Notes & Best Practices

* Every method includes detailed memory and shape logging.
* Leakage-aware design prevents contamination of test month.
* Feature validation is handled via Pandera — strict schemas catch unexpected changes.
* `tqdm` is used for visible tracking of slow processes like expanding windows.

---
### Pipeline dataflow visualisation:
```text
                        ┌────────────────────┐
                        │ Cleaned Sales CSV  │
                        └────────┬───────────┘
                                 ▼
                       ┌──────────────────────┐
                       │      sales (df)      │
                       └────────┬─────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
        ▼                                               ▼
┌────────────────────┐                         ┌────────────────────┐
│   blank_schema()    │                         │ sales_aggregation()│
│ → df (all dates,    │                         │ → aggregated (sum  │
│ shop_id, item_id)   │                         │   + mean per group)│
└────────┬────────────┘                         └────────┬───────────┘
         │                                               │
         └───────────────────────────────────────────────┘
                         ▼
        ┌────────────────────────────────────────┐
        │ merge_df_aggregated(df, aggregated)    │
        │ → full_df (joined schema + sales info) │
        └────────────────────────┬───────────────┘
                                 ▼
                     ┌────────────────────────┐
                     │ concat_test()          │
                     │ (+ assigns block 34)   │
                     └─────────┬──────────────┘
                               ▼
                    ┌────────────────────────────┐
                    │ full_df (now includes test)│
                    └─────────┬──────────────────┘
                              │
                              ▼
                    ┌────────────────────────────┐
                    │ Items CSV                  │
                    │ Shops CSV                  │
                    │ Item Categories CSV        │
                    └─────────┬────────────┬─────┘
                              ▼            ▼
                   ┌─────────────────────────────┐
                   │ encode_dicts()              │
                   │ → encoded items, shops, cats│
                   └───────┬──────────────┬──────┘
                           ▼              ▼
            ┌────────────────────┐  ┌───────────────────────┐
            │ merge_full_df_dicts│  │ merge_sales_dicts     │
            │ → full_df enriched │  │ → sales enriched       │
            └──────────┬─────────┘  └─────────┬──────────────┘
                       ▼                      ▼
           ┌───────────────────────┐ ┌────────────────────────────┐
           │ month_aggregations()  │ │ sales used as group source │
           │ → stats added to      │ └────────────────────────────┘
           │   full_df             │
           └──────────┬────────────┘
                      ▼
          ┌───────────────────────────────┐
          │ was_in_test(full_df, test)    │
          │ → flags item/shop presence    │
          └──────────┬────────────────────┘
                     ▼
          ┌───────────────────────────────┐
          │ first_month(full_df)          │
          │ → marks item's first sale     │
          └──────────┬────────────────────┘
                     ▼
          ┌───────────────────────────────┐
          │ expanding_window(full_df)     │
          │ → mean/max per previous month │
          └──────────┬────────────────────┘
                     ▼
          ┌───────────────────────────────┐
          │ year_month(full_df)           │
          │ → adds 'year' and 'month'     │
          └──────────┬────────────────────┘
                     ▼
          ┌───────────────────────────────┐
          │ lags(full_df)                 │
          │ → shifted features t-1, t-2.. │
          └──────────┬────────────────────┘
                     ▼
          ┌───────────────────────────────┐
          │ deltas(full_df)               │
          │ → diffs & naive predictions   │
          └──────────┬────────────────────┘
                     ▼
          ┌───────────────────────────────┐
          │ check_leakege(full_df)        │
          │ → removes invalid features    │
          └──────────┬────────────────────┘
                     ▼
         ┌────────────────────────────────┐
         │ Pandera Validation (optional)  │
         └──────────┬─────────────────────┘
                    ▼
         ┌────────────────────────────────┐
         │ downcast_dtypes(full_df)       │
         └──────────┬─────────────────────┘
                    ▼
         ┌────────────────────────────────┐
         │ output(full_df)                │
         │ → saves as full_df.parquet     │
         └────────────────────────────────┘

```


Possibilities:
1. Changing any of those parametrs inside of a script will cause a schemma error. Yet features schema rebuild script isn't included in the project.
2. For downcast dtypes when it used inside of tqdm loop, we avoid interrupting console output and might like to stop logging inside of tqdm, that's why for `.downcast_dtypes()` method we have argument as `logs: bool = False` by default it doesn't show in logs how much script decreased a memory of a given DataFrame. We also have `only_to_show_loses: bool = False` parametr in case if we want to see ONLY how much memory will be reduced but not reducing this, pay attention when enabling this flag, because downcasting itslelf won't work.
3. For `.check_leakege()`  you can send as argument `constant_features` for those features checking for all Nans in test set inside of full_df will be skipped. By default it includes features as `{'target','item_id_was_in_test', 'shop_id_was_in_test','not_full_historical_data'}`
4. For `.deltas()` you also can choose from which feature you want to create deltas for the last two monthes, and "predictions" for the next two. By default it includes following features: `['target', 'target_item_id_total', 'target_shop_id_total','target_item_category_id_total',\
                            'target_general_item_category_name_total', 'target_city_total']`
5. For `.lags()` you can also pass features names for which to create lags, by default script creates lags which has 'target' string inside of columns names. And you can add some, by default following are added: `['was_item_price_outlier', 'was_item_cnt_day_outlier', 'item_price']`

Syntax of script:
Every method represents a heading from notebook. Every sub heading devvided by two \n. Every cell devided by one \n

Architecture:
Better to store variables locally across methods and keep instance variables of object as much clean as possible, since we have big enough dataframe for memmory malloc or overflow.

RAW:
</br>Methods:
- extract()

- blank_schema()
- sales_aggregation()
- merge_df_aggregated()
- concat_test()
- encode_dicts()
- merge_full_df_dicts()
- merge_sales_dicts()
- month_aggregations()
- was_in_test()

- month_aggregations()
- first_month()
- expanding_window()
- year_month()
- was_in_test()
- downcast_dtype()
- lags()
- deltas()
- output()
- size_memmory_info()
