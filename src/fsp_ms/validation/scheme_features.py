import pandera.pandas as pa
from pandera.pandas import Check

class SchemaFeatures:
    def __init__(self):
        self.schema = pa.DataFrameSchema(
            {
                # Core identifiers and time-related columns:
                "date_block_num": pa.Column(pa.Int32, Check.in_range(min_value=0, max_value=34)),
                "shop_id": pa.Column(pa.Int32, Check.in_range(min_value=0, max_value=59)),
                "item_id": pa.Column(pa.Int32, Check.in_range(min_value=0, max_value=22169)),
                "item_category_id": pa.Column(pa.Int32, Check.in_range(min_value=0, max_value=83)),
                "general_item_category_name": pa.Column(pa.Int8, Check.in_range(min_value=0, max_value=14)),
                "city": pa.Column(pa.Int8, Check.in_range(min_value=0, max_value=30)),
                "month": pa.Column(pa.Int8, Check.in_range(min_value=1, max_value=12)),
                "year": pa.Column(pa.Int32, Check.isin([2013, 2014, 2015])),

                # Binary flag columns (0 or 1):
                "item_id_was_in_test": pa.Column(pa.Int8, Check.isin([0, 1])),
                "shop_id_was_in_test": pa.Column(pa.Int8, Check.isin([0, 1])),
                "not_full_historical_data": pa.Column(pa.Int8, Check.isin([0, 1])),
                "first_month_item_id": pa.Column(pa.Int8, Check.isin([0, 1])),

                # Target and aggregated historical features:
                "target": pa.Column(pa.Float32, Check.ge(0)),  # monthly item count, non-negative
                "target_aggregated_mean_premonthes_item_id_shop_id": pa.Column(pa.Float32, Check.ge(0)),
                "target_aggregated_max_premonthes_item_id_shop_id": pa.Column(pa.Float32, Check.ge(0)),
                "target_aggregated_mean_premonthes_item_id": pa.Column(pa.Float32, Check.ge(0)),
                "target_aggregated_max_premonthes_item_id": pa.Column(pa.Float32, Check.ge(0)),
                "target_aggregated_mean_premonthes_shop_id": pa.Column(pa.Float32, Check.ge(0)),
                "target_aggregated_max_premonthes_shop_id": pa.Column(pa.Float32, Check.ge(0)),

                # Lag features (regex patterns to cover all lag columns):
                r"^target.*_lag_\d+$": pa.Column(pa.Float32, Check.ge(0), regex=True),  # all target-related lag columns >= 0
                r"^was_item.*_outlier_lag_\d+$": pa.Column(pa.Float32, Check.in_range(min_value=0, max_value=1), regex=True),  # outlier flags 0-1
                r"^item_price_lag_\d+$": pa.Column(pa.Float32, Check.ge(0), regex=True),  # price lags non-negative

                # Delta features (differences between lagged targets):
                r".*_delta_1_2$": pa.Column(pa.Float32, regex=True),
                r".*_delta_2_3$": pa.Column(pa.Float32, regex=True),

                # Predict features (extrapolated predictions from deltas):
                r".*_predict_1_2$": pa.Column(pa.Float32, regex=True),
                r".*_predict_2_3$": pa.Column(pa.Float32, regex=True),
            },
            # Each (date_block_num, shop_id, item_id) tuple should be unique in the DataFrame
            unique=["date_block_num", "shop_id", "item_id"],
            strict=True
        )
