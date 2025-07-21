import numpy as np
import pandas as pd
import xgboost as xgb
import pickle

from src.config import Config
from src.utils.logger import get_logger

class XGB_model():

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.model = xgb.XGBRegressor()

    def get_train_data(self):
        self.logger.info('Uploading training data...')
        X = pd.read_parquet(self.config.get('train_x'))
        y = pd.read_parquet(self.config.get('train_y'))
        return X, y
    
    def get_inference_data(self):
        self.logger.info('Uploading inference data...')
        inference_for = pd.read_parquet(self.config.get('inference'))
        return inference_for

    def save_model(self):
        path = self.config.get('xgb_model')
        self.logger.info(f'Saving model to {path}...')
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
    

    def train(self, save: bool=False):
        params =  {'n_estimators': 192, 'max_depth': 9, \
            'learning_rate': 0.018270981823248666, \
                'subsample': 0.7539246424525929, 'colsample_bytree': 0.562829755261984,\
                    'gamma': 0.3153933459249693, 'lambda': 0.1718951364361902, \
                        'alpha': 0.26986966152618785, 'enable_categorical':True}
        self.logger.info(f'XGB Model training function is starting...\n Parameters: {params}')
        X, y = self.get_train_data()
        X = self.select_features(X)
        self.model = xgb.XGBRegressor(**params)
        self.logger.info('Fit...')
        self.model.fit(X, y)
        self.logger.info(f'XGB has been trained')
        if save:
            self.save_model()
        return self.model

    def load_model(self):
        path = self.config.get('xgb_model')
        self.logger.info(f'Uploading model from .pkl, \
                         \nPath: {path}...')
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        self.logger.info('Model uploaded successfully')
    
    def predict(self, load: bool=True, save: bool=True):
        self.logger.info('Starting prediction function...')
        if load:
            self.load_model()
        inference_for = self.get_inference_data()
        inference_for = self.select_features(X=inference_for)
        self.logger.info('XGBoost is Predicting now...')
        predicted = self.model.predict(inference_for)
        if save:
            df_predicted = self.save_prediction(predicted)
        self.logger.info('Prediction process completed🫡')
        return df_predicted


    def save_prediction(self, predicted):
        self.logger.info('Saving predictions in appropriate format...')
        inference_y = predicted
        inference_y = np.clip(inference_y, 0, 20)
        df_y_pred = pd.DataFrame(inference_y)
        df_y_pred.columns = ['item_cnt_month']
        
        df_y_pred['ID'] = df_y_pred.index
        df_y_pred = df_y_pred[['ID','item_cnt_month']]
        df_y_pred.to_csv(self.config.get('predict'), index=False)
        return df_y_pred

    def select_features(self, X):
        self.logger.info('Selecting only important features from given data...')
        important_features = ['target_lag_1',
            'target_aggregated_max_premonthes_item_id_shop_id_lag_1',
            'target_aggregated_mean_premonthes_item_id_shop_id',
            'target_aggregated_max_premonthes_item_id_shop_id',
            'target_item_category_id_mean_lag_2',
            'target_aggregated_max_premonthes_item_id_lag_2',
            'target_predict_2_3',
            'first_month_item_id',
            'target_aggregated_max_premonthes_item_id_shop_id_lag_2',
            'item_category_id',
            'target_item_id_mean_lag_1',
            'item_id_was_in_test',
            'was_item_cnt_day_outlier_lag_1',
            'target_general_item_category_name_total_predict_1_2',
            'target_aggregated_max_premonthes_item_id',
            'target_item_id_total_lag_1',
            'target_general_item_category_name_total_predict_2_3',
            'target_lag_2',
            'month',
            'target_aggregated_mean_premonthes_shop_id_lag_1',
            'target_aggregated_mean_premonthes_shop_id',
            'target_item_category_id_total_delta_1_2',
            'target_item_id_total_predict_1_2',
            'target_lag_3',
            'target_aggregated_mean_premonthes_item_id_lag_3',
            'target_item_category_id_total_predict_1_2',
            'target_general_item_category_name_mean_lag_2',
            'target_shop_id_total_delta_1_2',
            'target_general_item_category_name_total_lag_1',
            'target_item_category_id_total_lag_1',
            'target_general_item_category_name_mean_lag_1',
            'target_shop_id_total_predict_2_3',
            'shop_id',
            'city',
            'date_block_num', 'item_id']
        X = X[important_features].copy()

        categorical = ['shop_id','item_id','item_category_id','city']
        
        self.logger.info('Marking categorical features...')
        X[categorical] =  X[categorical].astype('category')
        return X