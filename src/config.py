from pathlib import Path

class Config:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent / 'data'

        self._config = {
            'sales':            self.base_dir / 'sales_train.csv',
            'items':            self.base_dir / 'dicts/items.csv',
            'item_categories':  self.base_dir / 'dicts/item_categories.csv',
            'shops':            self.base_dir / 'dicts/shops.csv',
            'test':             self.base_dir / 'submission_data/test.csv',
            'output_dir':       self.base_dir / 'output',
            'output_parquet':   self.base_dir / 'output/sales_cleaned.parquet'
        }

    def get(self, key : str) -> Path:
            if key not in self._config:
                  raise KeyError(f"Config key '{key}' not found.\nPossible keys: {self.keys()}")
            return self._config[key]
    
    def set(self, key: str, value: Path | str) -> None:
            self._config[key] = Path(value)

    def as_dict(self) -> dict[str, Path]:
          return self._config.copy()
    
    def keys(self) -> list[str]:
          return list(self._config.keys())

    def __getitem__(self, key: str) -> Path:
        return self.get(key) # to have possibility call keys through dict syntax e.g. config['key'] 
    
    def __contains__(self, key: str) -> bool:
        return key in self._config # to support expressions as " if 'key' in config "
    
    def __repr__(self) -> str:
          return '\n'.join(f"{k}: {v}" for k, v in self._config.items()) # To use syntax as "print(config)"

    
    