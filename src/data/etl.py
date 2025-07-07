import pandas as pd
import numpy as np
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from config import Config

from src.utils.logger import get_logger


# Setup logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('src/etl_pipeline.log'),
#         logging.StreamHandler()
#     ]
# )



def outliers_filtration(df, column: str):
    logger.info(f'\n\n Starting Outliers Filtration for {column} : \n')

    # Column feature filtration :
    q99 = df[column].quantile(0.99)
    q01 = df[column].quantile(0.01)
    count_above = df[df[column] > q99].shape[0]
    count_below = df[df[column] < q01].shape[0]
    logger.info(f'{column}: 99th percentile = {q99:.2f}, amount of outliers above = {count_above}')
    logger.info(f'{column}: 1st percentile = {q01:.2f}, amount of outliers below = {count_below}')

    # Column negatives
    df_negative_zero = df[df[column] <= 0].shape[0]
    logger.info(f'Amount of observations with zero value of {column} column or below: {df_negative_zero}')
    df = df[df[column] > 0].copy()
    logger.info('Observations equal to zero or below have been removed')

    # Column hight values - clipping and marking
    was_column_outlier = f'was_{column}_outlier'
    df[was_column_outlier] = (df[column] > q99).astype('int8')
    df[column] = df[column].clip(0, q99)
    logger.info(f"{column} outliers have been marked as '{was_column_outlier}' binary feature")
    logger.info(f'Observations higher than 99th {column} percentile have been clipped to upper bound: {q99}\n')
    return df

def normalize_shop_ids(df):
    logger.info('Starting to check duplicated shops')
    replacements = {10: 11, 1: 58, 0: 57, 40: 39}
    df['shop_id'] = df['shop_id'].replace(replacements)
    logger.info('Duplicated shops have been replaced')
    logger.info(f'Amount of duplicates after dicts similar shops replacement : {df.duplicated().sum()}')
    logger.info('Grouping duplicated shops and sum item_cnt_value...')
    df = df.groupby(['date', 'date_block_num', 'shop_id', 'item_id', 'item_price'], as_index=False).agg({'item_cnt_day': 'sum'})
    logger.info(f'Amount of duplicates after grouping : {df.duplicated().sum()}')
    return df

class ETL_pipeline():
    def __init__(self, config):
        self.config = config
    
    def date_convertation(self, sales):
        sales['date'] = pd.to_datetime(sales['date'], format='%d.%m.%Y')
        logger.info("Converted 'date' to datetime")
        return sales

    def duplicates_filtration(self, sales: pd.DataFrame):
        subset_dup = list(sales.columns)
        dup_count = sales.duplicated(subset = subset_dup).sum()
        sales = sales.drop_duplicates(subset = subset_dup).copy()
        logger.info(f"Dropped {dup_count} duplicated rows, cols are : {subset_dup}")
        return sales

    def transform(self, sales):

        # Basic preprocessing
        initial_len = sales.shape[0]
        logger.info(f'Initial sales shape: {sales.shape}')
        sales = self.date_convertation(sales)
        sales = self.duplicates_filtration(sales)
        sales = normalize_shop_ids(sales)
        sales = outliers_filtration(sales, 'item_price')
        sales = outliers_filtration(sales, 'item_cnt_day')

        # Reseting indexes and evalueate overall preprocessing
        sales = sales.reset_index(drop=True)
        final_len = sales.shape[0]
        logger.info(f'Final sales shape: {sales.shape}')
        logger.info(f'Initial table decreased by {initial_len - final_len} raws')
        return sales

    def load(self, sales):
        output_dir = Path(self.config.get('cleaned_dir'))
        output_dir.mkdir(parents=True, exist_ok=True)
        sales.to_parquet(self.config.get('cleaned_parquet'), index=False)
        #sales.to_csv(self.config.get('cleaned_test_schema_csv'), index = False)
        logger.info(f"Saved cleaned sales to {self.config.get('cleaned_parquet')}")


    def extract(self):
        sales           = pd.read_csv(self.config.get('sales'))
        items           = pd.read_csv(self.config.get('items'))
        item_categories = pd.read_csv(self.config.get('item_categories'))
        shops           = pd.read_csv(self.config.get('shops'))
        test            = pd.read_csv(self.config.get('test'))
        logger.info('Data loaded successfully')
        return sales, items, item_categories, shops, test

    def run_etl(self):
        logger.info('\n\n\n=== ETL process started ===')
        sales, items, item_categories, shops, test = self.extract()
        sales = self.transform(sales)
        self.load(sales)
        logger.info("\n=== ETL process finished ===\n\n\n\n")

if __name__ == "__main__":
    config = Config()
    logger = get_logger("etl", log_file = config.get('log_file_etl'))
    # logging.info(f"Loaded config:\n{config}") # uncomment for debugging
    etl = ETL_pipeline(config)
    etl.run_etl()
