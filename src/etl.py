import pandas as pd
import numpy as np
import os
import logging
import datetime

from config import (
    PATH_SALES, PATH_ITEMS, PATH_ITEM_CATEGORIES,\
          PATH_SHOPS, PATH_TEST, PATH_OUTPUT_PARQUET, OUTPUT_DIR
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)

def extract():
    sales           = pd.read_csv(PATH_SALES)
    items           = pd.read_csv(PATH_ITEMS)
    item_categories = pd.read_csv(PATH_ITEM_CATEGORIES)
    shops           = pd.read_csv(PATH_SHOPS)
    test            = pd.read_csv(PATH_TEST)
    logging.info('Data loaded successfully')
    return sales, items, item_categories, shops, test

def date_convertation(sales):
    sales['date'] = pd.to_datetime(sales['date'], format='%d.%m.%Y')
    logging.info("Converted 'date' to datetime")
    return sales

def duplicates_filtration(sales: pd.DataFrame):
    subset_dup = list(sales.columns)
    dup_count = sales.duplicated(subset = subset_dup).sum()
    sales = sales.drop_duplicates(subset = subset_dup).copy()
    logging.info(f"Dropped {dup_count} duplicated rows, cols are : {subset_dup}")
    return sales

def outliers_filtration(df, column: str):
    logging.info(f'\n\n Starting Outliers Filtration for {column} : \n')

    # Column feature filtration :
    q99 = df[column].quantile(0.99)
    q01 = df[column].quantile(0.01)
    count_above = df[df[column] > q99].shape[0]
    count_below = df[df[column] < q01].shape[0]
    logging.info(f'{column}: 99th percentile = {q99:.2f}, amount of outliers above = {count_above}')
    logging.info(f'{column}: 1st percentile = {q01:.2f}, amount of outliers below = {count_below}')

    # Column negatives
    df_negative_zero = df[df[column] <= 0].shape[0]
    logging.info(f'Amount of observations with zero value of {column} column or below: {df_negative_zero}')
    df = df[df[column] > 0].copy()
    logging.info('Observations equal to zero or below have been removed')

    # Column hight values - clipping and marking
    was_column_outlier = f'was_{column}_outlier'
    df[was_column_outlier] = (df[column] > q99).astype('int8')
    df[column] = df[column].clip(0, q99)
    logging.info(f"{column} outliers have been marked as '{was_column_outlier}' binary feature")
    logging.info(f'Observations higher than 99th {column} percentile have been clipped to upper bound: {q99}\n')
    return df

def normalize_shop_ids(df):
    logging.info('Starting to check duplicated shops')
    replacements = {10: 11, 1: 58, 0: 57, 40: 39}
    df['shop_id'] = df['shop_id'].replace(replacements)
    logging.info('Duplicated shops have been replaced')
    logging.info(f'Amount of duplicates after dicts similar shops replacement : {df.duplicated().sum()}')
    logging.info('Grouping duplicated shops and sum item_cnt_value...')
    df = df.groupby(['date', 'date_block_num', 'shop_id', 'item_id', 'item_price'], as_index=False).agg({'item_cnt_day': 'sum'})
    logging.info(f'Amount of duplicates after grouping : {df.duplicated().sum()}')
    return df

def transform(sales, items, item_categories, shops, test):

    # Basic preprocessing
    initial_len = sales.shape[0]
    logging.info(f'Initial sales shape: {sales.shape}')
    sales = date_convertation(sales)
    sales = duplicates_filtration(sales)
    sales = normalize_shop_ids(sales)
    sales = outliers_filtration(sales, 'item_price')
    sales = outliers_filtration(sales, 'item_cnt_day')

    # Merge dictionaries
    sales = sales.merge(items, on='item_id', how='left')
    sales = sales.merge(item_categories, on='item_category_id', how='left')
    sales = sales.merge(shops, on='shop_id', how='left')
    logging.info('Merged sales with items, item_categories and shops')

    # Reseting indexes and evalueate overall preprocessing
    sales = sales.reset_index(drop=True)
    final_len = sales.shape[0]
    logging.info(f'Final sales shape: {sales.shape}')
    logging.info(f'Initial table decreased by {initial_len - final_len} raws')
    return sales

def load(sales):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    sales.to_parquet(PATH_OUTPUT_PARQUET, index=False)
    logging.info(f'Saved cleaned sales to {PATH_OUTPUT_PARQUET}')


def run_etl():
    logging.info('\n\n\n=== ETL process started ===')
    sales, items, item_categories, shops, test = extract()
    sales = transform(sales, items, item_categories, shops, test)
    load(sales)
    logging.info("\n=== ETL process finished ===\n\n\n\n")

if __name__ == "__main__":
    run_etl()
