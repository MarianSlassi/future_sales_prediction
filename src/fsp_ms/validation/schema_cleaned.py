import pandera.pandas as pa
from pandera.pandas import Column, Check

class SchemaSales:
    def __init__(self):
        self.schema = pa.DataFrameSchema(
            {
                "date": Column(),
                "date_block_num": Column(pa.Int64, Check.in_range(min_value=0, max_value=33)),  # 0 to 33 inclusive
                "shop_id": Column(pa.Int64, Check.in_range(min_value=0, max_value=59)),        # 0 to 59 inclusive
                "item_id": Column(pa.Int64, Check.in_range(min_value=0, max_value=22169)),     # 0 to 22169 inclusive
                "item_price": Column(pa.Float64, Check.in_range(min_value=0, max_value=6000)), # price >=0, reasonable upper bound
                "item_cnt_day": Column(pa.Float64, Check.ge(0)),  # sales count >= 0 (no negatives)
                "was_item_price_outlier": Column(pa.Int8, Check.isin([0, 1])),  # must be 0 or 1
                "was_item_cnt_day_outlier": Column(pa.Int8, Check.isin([0, 1])) # must be 0 or 1
            },
            unique=["date", "shop_id", "item_id", "item_price"],  # each combination is unique
            strict=True
        )
