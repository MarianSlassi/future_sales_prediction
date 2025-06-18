import os

BASE_DIR              = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
DICT_DIR              = os.path.join(BASE_DIR, 'dicts')
SUBMISSION_DIR        = os.path.join(BASE_DIR, 'submission_data')
OUTPUT_DIR            = os.path.join(BASE_DIR, 'output')

PATH_SALES            = os.path.join(BASE_DIR, 'sales_train.csv')
PATH_ITEMS            = os.path.join(DICT_DIR, 'items.csv')
PATH_ITEM_CATEGORIES  = os.path.join(DICT_DIR, 'item_categories.csv')
PATH_SHOPS            = os.path.join(DICT_DIR, 'shops.csv')
PATH_TEST             = os.path.join(SUBMISSION_DIR, 'test.csv')
PATH_OUTPUT_PARQUET   = os.path.join(OUTPUT_DIR, 'sales_cleaned.parquet')