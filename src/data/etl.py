import pandas as pd

class ETL_pipeline():

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def outliers_filtration(self, df, column: str):
        self.logger.info(f'\n\n Starting Outliers Filtration for {column} : \n')

        # Column feature filtration:
        q99 = df[column].quantile(0.99)
        q01 = df[column].quantile(0.01)
        count_above = df[df[column] > q99].shape[0]
        count_below = df[df[column] < q01].shape[0]
        self.logger.info(f'{column}: 99th percentile = {q99:.2f}, amount of outliers above = {count_above}')
        self.logger.info(f'{column}: 1st percentile = {q01:.2f}, amount of outliers below = {count_below}')

        # Column negatives
        df_negative_zero = df[df[column] <= 0].shape[0]
        self.logger.info(f'Amount of observations with zero value of {column} column or below: {df_negative_zero}')
        df = df[df[column] > 0].copy()
        self.logger.info('Observations with zero or negative values have been removed')

        # Column high values - clipping and marking
        was_column_outlier = f'was_{column}_outlier'
        df[was_column_outlier] = (df[column] > q99).astype('int8')
        df[column] = df[column].clip(0, q99)
        self.logger.info(f"{column} outliers have been marked as '{was_column_outlier}' binary feature")
        self.logger.info(f'Observations higher than 99th {column} percentile have been clipped to upper bound: {q99}\n')
        return df

    def normalize_shop_ids(self, df):
        self.logger.info('Starting to check duplicated shops')
        replacements = {10: 11, 1: 58, 0: 57, 40: 39}
        df['shop_id'] = df['shop_id'].replace(replacements)
        self.logger.info('Duplicated shops have been replaced')
        self.logger.info(f'Amount of duplicates after dicts similar shops replacement : {df.duplicated().sum()}')
        self.logger.info('Grouping duplicated shops and sum item_cnt_value...')
        df = df.groupby(['date', 'date_block_num', 'shop_id', 'item_id', 'item_price'], as_index=False).agg({'item_cnt_day': 'sum'})
        self.logger.info(f'Number of duplicates after grouping : {df.duplicated().sum()}')
        return df
    
    def date_conversion(self, sales):
        sales['date'] = pd.to_datetime(sales['date'], format='%d.%m.%Y')
        self.logger.info("Converted 'date' to datetime")
        return sales

    def duplicates_filtration(self, sales: pd.DataFrame):
        subset_dup = list(sales.columns)
        dup_count = sales.duplicated(subset = subset_dup).sum()
        sales = sales.drop_duplicates(subset = subset_dup).copy()
        self.logger.info(f"Dropped {dup_count} duplicated rows, cols are : {subset_dup}")
        return sales

    def transform(self, sales):

        # Basic preprocessing
        initial_len = sales.shape[0]
        self.logger.info(f'Initial sales shape: {sales.shape}')
        sales = self.date_conversion(sales)
        sales = self.duplicates_filtration(sales)
        sales = self.normalize_shop_ids(sales)
        sales = self.outliers_filtration(sales, 'item_price')
        sales = self.outliers_filtration(sales, 'item_cnt_day')

        # Resetting indexes and evalueate overall preprocessing
        sales = sales.reset_index(drop=True)
        final_len = sales.shape[0]
        self.logger.info(f'Final sales shape: {sales.shape}')
        self.logger.info(f'Initial table decreased by {initial_len - final_len} rows')
        return sales

    def load(self, sales):
        output_dir = Path(self.config.get('cleaned_dir'))
        output_dir.mkdir(parents=True, exist_ok=True)
        sales.to_parquet(self.config.get('cleaned_parquet'), index=False)
        #sales.to_csv(self.config.get('cleaned_test_schema_csv'), index = False)
        self.logger.info(f"Saved cleaned sales to {self.config.get('cleaned_parquet')}")


    def extract(self):
        sales           = pd.read_csv(self.config.get('sales'))
        items           = pd.read_csv(self.config.get('items'))
        item_categories = pd.read_csv(self.config.get('item_categories'))
        shops           = pd.read_csv(self.config.get('shops'))
        test            = pd.read_csv(self.config.get('test'))
        self.logger.info('Data loaded successfully')
        return sales, items, item_categories, shops, test

    def run_etl(self, validator_object=None, dry_run: bool=True):
        self.logger.info('\n\n\n=== ETL process started ===')
        sales, items, item_categories, shops, test = self.extract()
        sales = self.transform(sales)

        if validator_object is not None:
            sales = validator_object.validate(sales)
        else:
            self.logger.warning('!!! No validation schema passed to etl pipeline\
                                Pipeline made transformations without validation.')
        
        if not dry_run:
            self.load(sales)
        self.logger.info("\n=== ETL process finished ===\n\n\n\n")
