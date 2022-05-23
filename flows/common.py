"""Module for common flow tasks."""

from prefect import task
from datetime import datetime
from datetime import datetime
import pandas as pd
import numpy as np
from google.oauth2 import service_account


@task(log_stdout=True)
def df_to_gcs_parquet(df, google_service_account, bucket, file_name, service_name):

    # adding scraped timestamp
    df["scraped_at"] = pd.Timestamp.utcnow()

    # gcp make sure all missing values are equally filled
    df.fillna(value=np.nan, inplace=True)

    date_path = f"{datetime.utcnow().strftime('%Y_%m_%d')}"
    key = f"{service_name}/{file_name}/{date_path}_{service_name}_{file_name}.parquet"
    bucket = "datadrivendao"
    path = f"gs://{bucket}/{key}"

    # replace dot to underscore for bigquery
    df.columns = [col.replace(".", "_") for col in df.columns]

    credentials = service_account.Credentials.from_service_account_info(
        google_service_account,
        scopes=["https://www.googleapis.com/auth/devstorage.read_write"],
    )

    df.to_parquet(path, storage_options={"token": credentials}, index=False)

    print(f"Written parquet file to: {path}")

    return path
