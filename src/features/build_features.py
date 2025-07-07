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
config = Config()


from src.utils.logger import get_logger
logger = get_logger(name = "build_features", log_file = config.get('log_file_build_features'))

def size_memory_info(df: pd.DataFrame, name: str = 'current df'):
    size_in_bytes = df.memory_usage(deep=True).sum()
    size_in_megabytes = size_in_bytes / (1024 ** 2)
    size_in_gigabytes = size_in_bytes / (1024 ** 3)

    logger.info(f"\nMemory usage of {name}: {size_in_megabytes:.2f} MB ~ {size_in_gigabytes:.2f} GB\
                \nAmount of rows in this table: {df.shape[0]}\
                \nAmount of columns in this table: {df.shape[1]}\n")

# size_memory_info(df = full_df, name='full_df')

def extract():
    logger.info('Extracting all raw data...')
    # Main dataset
    sales = pd.read_parquet(config.get('cleaned_parquet'))

    # Data-Dicts
    items = pd.read_csv(config.get('items'))
    items_categories = pd.read_csv(config.get('item_categories'))
    shops = pd.read_csv(config.get('shops'))

    test = pd.read_csv(config.get('test')) 
    # the test set. You need to forecast the sales 
    # for these shops and products for November 2015.

    logger.info('All raw data has been extracted\n')
    return sales, items, items_categories, shops, test


def blank_schema(sales):
    logger.info('Creating full schema of items sold in every month for all shops...')

    ### Creating full schema of montly sold items for every shop - { df } 
    all_obs_combination_by = ['date_block_num', 'shop_id', 'item_id']
    all_shops_items = []

    for block_num in sales['date_block_num'].unique():
        unique_shops = sales[sales['date_block_num'] == block_num]['shop_id'].unique()
        unique_items = sales[sales['date_block_num'] == block_num]['item_id'].unique()
        all_shops_items.append(np.array(list(itertools.product([block_num], unique_shops, unique_items)),\
                                        dtype='int32'))

    # full schema with all unique combinations of month number, shop_id, and item_id for month:
    df = pd.DataFrame(np.vstack(all_shops_items), columns=all_obs_combination_by, dtype='int32')
    logger.info('Full blank schema of items sold in every month for all shops created succesfully')
    return df

def sales_aggregation(sales):
    ### Making a target feature and outliers flags from basic dataframe - { aggregated }
    all_obs_combination_by = ['date_block_num', 'shop_id', 'item_id']
    logger.info('Aggregatin sales to month time dimension...')
    aggregated = sales.groupby(all_obs_combination_by).agg({'item_price'  : 'mean', 'item_cnt_day': \
                                                        'sum','was_item_price_outlier':'mean', \
                                                            'was_item_cnt_day_outlier':'mean'})
    aggregated.rename(columns={'item_cnt_day': 'target'}, inplace = True)

    logger.info('Sales aggregated succesfully for month dimension, item_cnt_month columns marked as "target"')
    return aggregated

def merge_df_aggregated(df, aggregated):
    ### Merging full schema with agregated by target basic dataframe - contact { full_df } + {test}
    all_obs_combination_by = ['date_block_num', 'shop_id', 'item_id']
    logger.info("Merging blank schema of items to aggregated by month sales...")
    full_df = pd.merge(df, aggregated, on = all_obs_combination_by, how = 'left')
    full_df.fillna(value = 0, inplace= True)
    logger.info("Merged succesfully")
    return full_df

def concat_test(full_df, test): 
    test['date_block_num'] = 34
    logger.info('Assigned 34th month value to date_block_num in test')

    logger.info('Concatenating full schema with test...')
    full_df = pd.concat([full_df, test], ignore_index= True)
    full_df = full_df.drop('ID',axis=1)
    logger.info('Concatenated succesfully with resulting full_df table')
    logger.info(f'Percantage of zero values in target: {(full_df[full_df['target']==0]).shape[0] /  full_df.shape[0] :.2f}')
    size_memory_info(df = full_df, name= "full_df")
    return full_df

def encode_dicts(items, shops, items_categories): # This method modifies transfered in arguments dicts
    logger.info('Encoding cities, categories and general category columns from dicts...')
    items_categories['general_item_category_name'] = items_categories['item_category_name'].\
    apply(lambda x: 'Игровые консоли' if x.split()[0] == 'Игровые' else x.split()[0] )
    items_categories['general_item_category_name'] = pd.Categorical(items_categories.general_item_category_name).codes
    items_categories = items_categories.drop('item_category_name', axis=1)

    shops['city'] = shops['shop_name'].apply(lambda x: 'Якутск' if x.split()[0] == '!Якутск' else x.split()[0] )
    shops['city'] = pd.Categorical(shops.city).codes

    shops = shops.drop('shop_name', axis=1)
    items = items.drop('item_name', axis=1)
    logger.info('Dicts encoded successfully')

    return items, shops, items_categories

def merge_full_df_dicts(full_df, items, items_categories, shops): # supposed to receive encoded dicts
    logger.info('Merging dicts with full df...')
    full_df = full_df.merge(items, on='item_id', how='left')
    full_df = full_df.merge(items_categories, on = 'item_category_id', how = 'left')
    full_df = full_df.merge(shops, on = 'shop_id', how = 'left')
    logger.info('Encoded values from dicts added successfully resulting modified full_df')


    logger.info('full_df created\n')
    size_memory_info(df = full_df, name ='full_df')
    return full_df

def merge_sales_dicts(sales, items, items_categories, shops): # supposed to receive encoded dicts, modifies sales
    # This function is viable to aggregate target based on other features
    sales = sales.merge(items, on='item_id', how='left')
    sales = sales.merge(items_categories, on = 'item_category_id', how = 'left')
    sales = sales.merge(shops, on = 'shop_id', how = 'left')
    size_memory_info(df = sales, name = 'sales_train' )
    return sales

def full_schema(sales, items, items_categories, shops, test) -> pd.DataFrame:
    logger.info('Creating a common dataframe with test, all items, and sales by monthes:')

    

    return full_df, sales

def month_aggregations(full_df: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    logger.info('Starting aggregating target for other features...')

    group_keys = [
        'item_id',
        'shop_id',
        'item_category_id',
        'general_item_category_name',
        'city'
    ]

    aggregations = {
        'total': 'sum',
        'mean': 'mean'
    }

    for key in group_keys:
        group_cols = ['date_block_num', key]
        logger.info(f'Grouping by: {group_cols} ...')

        for suffix, agg_func in tqdm.tqdm(aggregations.items()):
            col_name = f'target_{key}_{suffix}'
            tqdm.tqdm.write(f'{col_name}')
            temp = sales.groupby(group_cols, as_index=False)['item_cnt_day'].agg(agg_func)
            temp = temp.rename(columns={'item_cnt_day': col_name})

            full_df = full_df.merge(temp, on=group_cols, how='left') 
        
        logger.info('Grouped successfully')
    logger.info('Aggregations finished successfully')
    size_memory_info(full_df)
    return full_df

def first_month(full_df):
    logger.info('Starting to mark items which sold first time in this month:')

    full_df['not_full_historical_data'] = 0
    logger.info('not_full_historical_data column intitialised.')

    logger.info('Creating a df of minimal month for every item...')
    first_month = full_df.groupby('item_id', as_index=False)['date_block_num'].min()
    first_month.rename(columns={'date_block_num': 'first_month_item_id_num'}, inplace=True)

    logger.info('Merging first month of appeareance to full_df..')
    full_df = full_df.merge(first_month, on='item_id', how='left')

    logger.info('Checking if first month of appereance is the current month and marking...')
    full_df['first_month_item_id'] = (full_df['date_block_num'] == full_df['first_month_item_id_num']).astype('int8')
    full_df = full_df.drop('first_month_item_id_num', axis = 1)

    logger.info('Marked first month with not_full_histoical_data')
    full_df.loc[full_df['date_block_num'] == 0, 'not_full_historical_data'] = 1
    full_df['not_full_historical_data'] = full_df['not_full_historical_data'].astype(np.int8)    

    logger.info('Items selling in this month first time are marked successfully')
    size_memory_info(full_df)
    return full_df

def expanding_window(full_df):
    logger.info('Starting leakege free target expanding window  aggregation:')
    
    aggregating_target_by = [['item_id', 'shop_id'], ['item_id'], ['shop_id']]
    logger.info("aggregating_target_by = [['item_id', 'shop_id'], ['item_id'], ['shop_id']]")

    for feature in aggregating_target_by:
        col = '_'.join(['target_aggregated_mean_premonthes', *feature])
        col2 = '_'.join(['target_aggregated_max_premonthes', *feature])
        full_df[col] = np.nan
        full_df[col2] = np.nan

        logger.info(f'Gathering target data for {feature} for all previous monthes and assgning value to the current month...')

        for d in tqdm.tqdm(full_df.date_block_num.unique()):
            valid_month = (full_df.date_block_num < d)
            current_month = (full_df.date_block_num == d)
            tqdm.tqdm.write(f'Gather previous statistic for {d} month...')

            temp = full_df.loc[valid_month].groupby(feature)[['target']].mean().reset_index()
            agg = full_df.loc[current_month][feature].merge(temp, on=feature, how='left')[['target']].copy()
            agg.set_index(full_df.loc[current_month].index, inplace=True)
            full_df.loc[current_month, col] = agg['target']

            temp = full_df.loc[valid_month].groupby(feature)[['target']].max().reset_index()
            agg = full_df.loc[current_month][feature].merge(temp, on=feature, how='left')[['target']].copy()
            agg.set_index(full_df.loc[current_month].index, inplace=True)
            full_df.loc[current_month, col2] = agg['target']

        logger.info(f'Expanding window statistics for {feature} have been created')

    logger.info('Leakege free target expanding window aggregation has been finished')

    size_memory_info(full_df)
    return full_df

def year_month(full_df):
    logger.info('Adding month and year feaetures...')
    full_df['month'] = ((full_df['date_block_num'] % 12) + 1).astype(np.int8)
    full_df['year'] = (2013 + (full_df['date_block_num'] // 12))
    logger.info('Month and year features were added successfully')
    return full_df

def was_in_test(full_df, test):
    logger.info('Starting to mark shops and items which contained in test...')

    shop_id_test = test['shop_id'].unique()
    item_id_test = test['item_id'].unique()
    full_df['item_id_was_in_test'] = 0
    full_df['shop_id_was_in_test'] = 0
    logger.info('Empty raws and columns item_id_was_in_test, shop_id_was_in_test have been created')

    logger.info('Assigning values...')
    full_df.loc[(full_df['item_id'].isin(item_id_test)), 'item_id_was_in_test'] =  1
    full_df.loc[full_df['shop_id'].isin(shop_id_test), 'shop_id_was_in_test'] =  1
    full_df['item_id_was_in_test'] = full_df['item_id_was_in_test'].astype(np.int8)
    full_df['shop_id_was_in_test'] = full_df['shop_id_was_in_test'].astype(np.int8)

    if int(full_df.loc[(full_df['date_block_num']== 34)&((full_df['shop_id_was_in_test']!= 1 )|(full_df['item_id_was_in_test']!= 1 )), ['shop_id_was_in_test', 'item_id_was_in_test']].shape[0]) != 0 :
        logger.info('All observation were merked for test as well')
    else:
        logger.info('!!! Some observation in test aren not marked as they are in test')
    
    logger.info('Shops and items which contained in test have been marked')
    size_memory_info(full_df)
    return full_df

def downcast_dtypes(full_df, only_to_show_loses: bool = False, logs: bool = True):
    if logs:
        logger.info('Downcasting current dataframe...')

    if only_to_show_loses:
        float_cols = full_df.select_dtypes(include='float64').columns
        int_cols = full_df.select_dtypes(include='int64').columns

        for col in float_cols:
            max_diff = (full_df[col] - full_df[col].astype('float32')).abs().max()
            print(f"{col}: max precision loss when downcasted to float32 = {max_diff}")

        for col in int_cols:
            min_val = full_df[col].min()
            max_val = full_df[col].max()
            if min_val < -2_147_483_648 or max_val > 2_147_483_647:
                print(f"{col}: OVERFLOW when downcasted to int32 (values out of range)")
        return
    
    mem_start = full_df.memory_usage(deep=True).sum()

    float_cols = full_df.select_dtypes(include=['float64']).columns
    int_cols = full_df.select_dtypes(include=['int64']).columns

    full_df[float_cols] = full_df[float_cols].astype('float32')
    full_df[int_cols] = full_df[int_cols].astype('int32')

    mem_end = full_df.memory_usage(deep=True).sum()

    if logs:
        logger.info(f'Memory usage reduced by: {(mem_start-mem_end)/ (1024**2)}MB')
    return full_df

def lags(full_df, additional: list[str] = ['was_item_price_outlier', 'was_item_cnt_day_outlier', 'item_price']):
    logger.info('Starting to create lags...')

    all_obs_combination_by = ['date_block_num', 'shop_id', 'item_id']
    shift_range = [1, 2, 3, 12]
    shifted_columns = [c for c in full_df if 'target' in c]
    shifted_columns = shifted_columns + additional

    for shift in tqdm.tqdm(shift_range):
        temp = full_df[all_obs_combination_by + shifted_columns].copy()
        temp['date_block_num'] = temp['date_block_num'] + shift

        foo = lambda x: f'{x}_lag_{shift}' if x in shifted_columns else x
        temp = temp.rename(columns=foo)

        full_df = pd.merge(full_df, temp, on = all_obs_combination_by, how= 'left').fillna(0)
        full_df = downcast_dtypes(full_df = full_df, logs=False)

        del temp
        gc.collect()
    
    logger.info(f'Lags have been create for {shifted_columns}...')
    size_memory_info(full_df)
    return full_df # added possibility to chose additional lags features

def deltas(full_df: pd.DataFrame, columns_to_delta: list[str] = ['target', 'target_item_id_total', 'target_shop_id_total','target_item_category_id_total',\
                        'target_general_item_category_name_total', 'target_city_total']):
    logger.info('Starting creating deltas...')
    # columns_to_delta = ['target', 'target_by_item_id_total', 'target_by_shop_id_total','target_by_category_total',\
    #                     'target_by_general_category_total', 'target_by_city_total']

    for target_predict in columns_to_delta:
        logger.info(f'Creating deltas for {target_predict} feature...')
        full_df[target_predict + '_delta_1_2'] = full_df[target_predict + '_lag_1'] - full_df[target_predict + '_lag_2']
        full_df[target_predict + '_delta_2_3'] = full_df[target_predict + '_lag_2'] - full_df[target_predict + '_lag_3']

        full_df[target_predict + '_predict_1_2'] = full_df[target_predict + '_lag_1'] + full_df[target_predict + '_delta_1_2']
        full_df[target_predict + '_predict_2_3'] = full_df[target_predict + '_lag_1'] + full_df[target_predict + '_delta_2_3']\
            + full_df[target_predict + '_predict_1_2']
        logger.info(f'Deltas have been created for {target_predict} feature...')

    logger.info(f'Deltas for {target_predict} have been created.')
    size_memory_info(full_df)
    return full_df # added possibility to chose deltas features

def output(full_df, constant_features: set[str] = {'target','item_id_was_in_test', 'shop_id_was_in_test','not_full_historical_data'} ):
    logger.info('Output fucntion has been triggered:')
    logger.info('Looking for leakege features..')
    temp = full_df[full_df['date_block_num'] == 34] # Chose last month only

    # Make a boolean mask for columns to delete which consist\
    # of all 0 for all observations

    leakege_true = list((temp == 0).sum() == 214200) 

    del temp
    gc.collect()

    leakege_features = set(full_df.loc[:,leakege_true].columns)
    #constant_features = {'target','item_id_was_in_test', 'shop_id_was_in_test','not_full_historical_data'}
    leakege_features = list(leakege_features - constant_features)

    full_df = full_df.drop(columns=leakege_features, axis = 1)
    logger.info('Leakege features were removed')

    full_df.to_parquet(config.get('features'), engine='pyarrow')
    logger.info(f'full_df with test set and without lekege feature was save to {config.get('features')}')
    logger.info('Output function has been executed')
    size_memory_info(full_df)


if __name__ == '__main__'  :
    logger.info('\n=== FEATURE ENGINEERING process started ===\n')
    sales, items, items_categories, shops, test = extract()
    #full_df, sales = full_schema(sales, items, items_categories, shops, test)
    
    df = blank_schema(sales)
    aggregated = sales_aggregation(sales)
    full_df = merge_df_aggregated(df, aggregated)
    full_df = concat_test(full_df, test)
    items, shops, items_categories =  \
        encode_dicts(items, shops, items_categories)
    full_df = merge_full_df_dicts(full_df, items, items_categories, shops)
    sales = merge_sales_dicts(sales, items, items_categories, shops)


    full_df = month_aggregations(full_df=full_df, sales = sales)
    full_df = first_month(full_df)
    full_df = expanding_window(full_df)
    full_df = year_month(full_df)
    full_df = was_in_test(full_df, test)
    full_df = lags(full_df)
    full_df = deltas(full_df)
    output(full_df)
    # sales, items, items_categories, shops, test = extract()
    # full_df, sales = full_schema(sales, items, items_categories, shops, test)
    # full_df = month_aggregations(full_df=full_df, sales=sales)
    logger.info("\n=== FEATURE ENGINEERING process finished ===\n\n\n\n\n")
