from pathlib import Path

class Config:
    def __init__(self):
        self.BASE_DIR         = Path(__file__).resolve().parent.parent / 'data'
        self.DICT_DIR         = self.BASE_DIR / 'dicts'
        self.SUBMISSION_DIR   = self.BASE_DIR / 'submission_data'
        self.OUTPUT_DIR       = self.BASE_DIR / 'output'

        self.PATH_SALES           = self.BASE_DIR / 'sales_train.csv'
        self.PATH_ITEMS           = self.DICT_DIR / 'items.csv'
        self.PATH_ITEM_CATEGORIES = self.DICT_DIR / 'item_categories.csv'
        self.PATH_SHOPS           = self.DICT_DIR / 'shops.csv'
        self.PATH_TEST            = self.SUBMISSION_DIR / 'test.csv'
        self.PATH_OUTPUT_PARQUET  = self.OUTPUT_DIR / 'sales_cleaned.parquet'

        self._config = {
            'sales': self.PATH_SALES,
            'items': self.PATH_ITEMS,
            'item_categories': self.PATH_ITEM_CATEGORIES,
            'shops': self.PATH_SHOPS,
            'test': self.PATH_TEST,
            'output_dir': self.OUTPUT_DIR,
            'output_parquet': self.PATH_OUTPUT_PARQUET
        }

    def get(self, key):
            return self._config.get(key)
    
    def set(self, key, value):
            self._config[key] = value