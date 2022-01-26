import pandas as pd
import pyarrow.parquet as pq


pd.read_parquet('/Users/felixvemmer/Downloads/twitter_screen_names.parquet', engine='pyarrow')

parquet_file = pq.ParquetFile('/Users/felixvemmer/Downloads/twitter_screen_names.parquet')

parquet_file.schema