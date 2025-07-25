import pandas as pd
import pandera.pandas as pa

class Validator:
    def __init__(self, logger):
        self.logger = logger
        pass

    def validate(self, schema: pa.DataFrameSchema, df: pd.DataFrame, scheme_name:str) -> pd.DataFrame:
        self.logger.info(f'Initializing validation schema: {scheme_name}...\n')
        self.logger.info(f'Starting validation for Dframe with {len(df)} records...')

        try:
            validated_df = schema.schema.validate(df)
            self.logger.info(f'Data frame has passed validation!\n')
        except pa.errors.SchemaErrors as e:
            self.logger.error("!!! DataFrame validation failed.")
            self.logger.error(f"\n{e.failure_cases}")  # This logs the specific columns, checks, and offending values
            raise
        return validated_df
