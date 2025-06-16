import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)

def load_data():
    base_path = '../data'
    sales = pd.read_csv(os.path.join(base_path, 'sales_train.csv'))
    items = pd.read_csv(os.path.join(base_path, 'dicts/items.csv'))
    item_categories = pd.read_csv(os.path.join(base_path, 'dicts/item_categories.csv'))
    shops = pd.read_csv(os.path.join(base_path, 'dicts/shops.csv'))
    test = pd.read_csv(os.path.join(base_path, 'submission_data/test.csv'))
    logging.info('Data loaded successfully')
    return sales, items, item_categories, shops, test

def normalize_shop_ids(df):
    replacements = {
        0: 57, 1: 58, 10: 11, 40: 39, 23: 25
    }
    df['shop_id'] = df['shop_id'].replace(replacements)
    return df

def categorize_item_categories(item_categories):
    item_categories['general_item_category_name'] = item_categories['item_category_name'].apply(lambda x: 'Игровые консоли' if x.split()[0] == 'Игровые' else x.split()[0] )
    return item_categories

def extract_city_feature(shops):
    shops['city'] = shops['shop_name'].apply(lambda x: 'Якутск' if x.split()[0] == '!Якутск' else x.split()[0] )
    return shops

def preprocess_sales(sales):

    # Basic preprocessing
    logging.info(f'Initial sales shape: {sales.shape}')

    sales['date'] = pd.to_datetime(sales['date'], format='%d.%m.%Y')
    logging.info("Converted 'date' to datetime")

    dup_count = sales.duplicated().sum()
    sales = sales.drop_duplicates()
    logging.info(f"Dropped {dup_count} duplicated rows")




    # item_price feature filtration :
    price_q99 = sales['item_price'].quantile(0.99)
    price_q01 = sales['item_price'].quantile(0.01)
    count_price_above = sales[sales['item_price'] > price_q99].shape[0]
    count_price_below = sales[sales['item_price'] < price_q01].shape[0]
    logging.info(f'item_price: 99th percentile = {price_q99:.2f}, outliers above = {count_price_above}')
    logging.info(f'item_price: 1st percentile = {price_q01:.2f}, outliers below = {count_price_below}')

    ## item_price negatives
    sales_negative_zero = sales[sales['item_price'] <= 0].shape[0]
    logging.info(f'Amount of observations with zero price or below:{sales_negative_zero}')
    sales = sales[sales['item_price'] > 0]
    logging.info('Observations equal to zero or below have been removed')

    ## item_price hight, clipping and marking
    sales['was_item_price_outlier'] = (sales['item_price'] > price_q99).astype('int8')
    sales['item_price'] = sales['item_price'].clip(0, price_q99)
    logging.info('item_price outliers have been marked as "was_item_price" binary feature')
    logging.info(f'Observations higher than 99th item_price percentile have been clipped to upper bound: {price_q99}')
    
    


    # item_cnt_day feature filtration :
    cnt_q99 = sales['item_cnt_day'].quantile(0.99)
    cnt_q01 = sales['item_cnt_day'].quantile(0.01)
    count_cnt_above = sales[sales['item_cnt_day'] > cnt_q99].shape[0]
    count_cnt_below = sales[sales['item_cnt_day'] < cnt_q01].shape[0]
    logging.info(f'item_cnt_day: 99th percentile = {cnt_q99:.2f}, outliers above = {count_cnt_above}')
    logging.info(f'item_cnt_day: 1st percentile = {cnt_q01:.2f}, outliers below = {count_cnt_below}')

    # item_cnt_day negatives
    sales = sales[sales['item_cnt_day'] >= 0]
    logging.info('Observations with item_cnt_day below zero have been removed')

    # item_cnt_day hight, clipping and marking
    sales['was_item_cnt_day_outlier'] = (sales['item_cnt_day'] > cnt_q99).astype('int8')
    sales['item_cnt_day'] = sales['item_cnt_day'].clip(0, cnt_q99)
    logging.info('item_cnt_day outliers have been marked as "was_item_cnt_day" binary feature')
    logging.info(f'Observations higher than 99th item_cnt_day percentile have been clipped to upper bound: {cnt_q99}')




    # reseting indexes and evalueate overall preprocessing
    sales = sales.reset_index(drop=True)
    logging.info(f'Final sales shape: {sales.shape}')
    return sales

def run_etl():
    logging.info('=== ETL process started ===')
    sales, items, item_categories, shops, test = load_data()

    sales = normalize_shop_ids(sales)
    test = normalize_shop_ids(test)

    item_categories = categorize_item_categories(item_categories)
    shops = extract_city_feature(shops)

    sales = preprocess_sales(sales)

    # Merge dictionaries
    sales = sales.merge(items, on='item_id', how='left')
    sales = sales.merge(item_categories, on='item_category_id', how='left')
    sales = sales.merge(shops, on='shop_id', how='left')
    logging.info('Merged sales with items, item_categories and shops')

    output_path = '../data/output'
    os.makedirs(output_path, exist_ok=True)
    sales.to_csv(os.path.join(output_path, "sales_cleaned.csv"), index=False)
    logging.info(f'Saved cleaned sales to output/sales_cleaned.csv')
    logging.info("=== ETL process finished ===")

if __name__ == "__main__":
    run_etl()
