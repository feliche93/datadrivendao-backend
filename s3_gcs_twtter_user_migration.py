# import pandas as pd
# import pathlib
# import numpy as np


# paths = pathlib.Path("/Users/felixvemmer/Downloads/raw_data/twitter").glob("**/twitter_users.parquet")

# final_df = pd.DataFrame()

# for path in sorted(list(paths)):
#     # print('Reading file: {}'.format(path))

# # path = '/Users/felixvemmer/Downloads/raw_data/twitter/2022/05/01/twitter_users.parquet'
#     df = pd.read_parquet(path)

#     # replace dot to underscore for bigquery
#     df.columns = [col.replace('.','_') for col in df.columns]

#     df.drop(columns=["index"], inplace=True)

#     df.fillna(value=np.nan, inplace=True)

#     # final_df = final_df.append(df)

#     service_name = "twitter"
#     file_name = "users"

#     date_path = '_'.join(path.parts[6:-1])
#     key = f"{service_name}/{file_name}/{date_path}_{service_name}_{file_name}.parquet"
#     bucket = "datadrivendao"
#     path_for_gcs = f"gs://{bucket}/{key}"

#     print(f"Writing parquet file to: {path_for_gcs}")

#     df.to_parquet(
#         path=path_for_gcs,
#         storage_options={
#             "token": "/Users/felixvemmer/Desktop/web3/datadrivendao-backend/datadrivendao-42c52b51132d.json"
#         },
#         index=False
#     )