import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, Check

from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from config import Config
from src.utils.logger import get_logger

class SchemaSales:
    def __init__(self, logger):
        self.logger = logger
        self.schema = pa.DataFrameSchema(
            {
                "date": Column(), 
                "date_block_num": Column(pa.Int64, Check.in_range(min_value=0, max_value=33)),  # 0 to 33 inclusive
                "shop_id": Column(pa.Int64, Check.in_range(min_value=2, max_value=59)),        # 2 to 59 inclusive
                "item_id": Column(pa.Int64, Check.in_range(min_value=0, max_value=22169)),     # 0 to 22169 inclusive
                "item_price": Column(pa.Float64, Check.in_range(min_value=0, max_value=6000)), # price >=0, reasonable upper bound
                "item_cnt_day": Column(pa.Float64, Check.ge(0)),  # sales count >= 0 (no negatives)
                "was_item_price_outlier": Column(pa.Int8, Check.isin([0, 1])),  # must be 0 or 1
                "was_item_cnt_day_outlier": Column(pa.Int8, Check.isin([0, 1])) # must be 0 or 1
            },
            unique=["date", "shop_id", "item_id", "item_price"],  # each combination is unique
            strict=True
        )
    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info('Initializing SchemaSales validation...')
        self.logger.info(f'Starting validation for sales data with {len(df)} records...')
        try:
            validated_df = self.schema.validate(df)
            self.logger.info('Data frame has passed validation!')
        except pa.errors.SchemaErrors as e:
            self.logger.error("DataFrame validation failed.")
            self.logger.error(f"\n{e.failure_cases}")  # log specific failure details
            raise
        return validated_df

if __name__ == '__main__':
    config = Config()
    logger = get_logger(name="validation_schema_cleaned", log_file=config.get('validation_schema_cleaned'))

    sales_df = pd.read_parquet(config.get('cleaned_parquet'))
    schema_validator = SchemaSales(logger)
    validated_df = schema_validator.validate(sales_df)
