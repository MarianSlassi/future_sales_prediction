import numpy as np
import pandas as pd
import itertools
import tqdm
import gc


from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
print(ROOT)
sys.path.append(str(ROOT))
from config import Config
from src.utils.logger import get_logger


class Split():
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
       # self.logger = logger
    def extract(self):
        self.logger.info('Extracting full_df to split it...')
        full_df = pd.read_parquet(self.config.get('features'), engine='pyarrow')
        self.logger.info('Data has been extracted successfully')
        return full_df

    def split(self,full_df):
        self.logger.info('Starting spliting process...')
        train = full_df[full_df['date_block_num'] != 34]
        predict = full_df[full_df['date_block_num'] == 34]

        train_x = train.drop('target', axis = 1)
        train_y = train[['target']]
        predict = predict.drop('target', axis = 1)
        self.logger.info('Data has been split')
        return train_x, train_y, predict


    def load(self, train_x, train_y, predict):
        self.logger.info(f'Starting to save data to {self.config.get('processed_dir')}...')
        train_x.to_parquet(self.config.get('train_x'), engine='pyarrow')
        train_y.to_parquet(self.config.get('train_y'), engine='pyarrow')
        predict.to_parquet(self.config.get('inference'), engine='pyarrow')
        self.logger.info('Data for training and predict has been saved')

    def run(self):
        self.logger.info('\n=== SPLITTING process started ===\n')
        self.load(*self.split(self.extract()))
        # full_df = self.extract()
        # train_x, train_y, predict = self.split(full_df)
        # self.load(train_x, train_y, predict)
        self.logger.info("\n=== SPLITTIGNG process process finished ===\n\n\n\n\n")




if __name__ == '__main__'  :
    config = Config()
    logger = get_logger(name = "split", \
                            log_file = config.get('log_file_split'))
    split = Split(config, logger)
    split.run()


