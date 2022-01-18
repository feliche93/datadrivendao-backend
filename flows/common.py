import boto3
import awswrangler as wr
import boto3
from prefect import task
from datetime import datetime
from cmath import log
from datetime import datetime
from math import ceil

@task(log_stdout=True)
def df_to_s3_parquet(df, aws_credentials, bucket, file_name, service_name):

    session = boto3.Session(
        region_name="us-east-1",
        aws_access_key_id=aws_credentials.get("ACCESS_KEY"),
        aws_secret_access_key=aws_credentials.get("SECRET_ACCESS_KEY"),
    )

    date_path = f"{datetime.utcnow().strftime('%Y/%m/%d')}"
    key = f"{service_name}/{date_path}/{file_name}.parquet"
    bucket = "datadrivendao"
    path = f"s3://{bucket}/{key}"

    result = wr.s3.to_parquet(
        df=df.reset_index(),
        path=path,
        # dataset=False,
        boto3_session=session,
        index=False,
    )

    print(f"Written parquet file to: {result['paths']}")

    return result