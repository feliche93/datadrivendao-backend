from cmath import log
from datetime import datetime
from math import ceil
import requests
import json
import pandas as pd
import math
from prefect import task, Flow
import prefect
from datetime import datetime
import awswrangler as wr
import boto3
from prefect.tasks.secrets import PrefectSecret
from prefect.tasks.airbyte.airbyte import AirbyteConnectionTask

from flow_config import RUN_CONFIG, STORAGE

FLOW_NAME = "extract_snapshot_data"

airbyte_task = AirbyteConnectionTask(
    airbyte_server_host="34.206.52.76",
)

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


@task(log_stdout=True)
def extract_snapshot_expore_data():

    url = "https://hub.snapshot.org/api/explore"
    r = requests.get(
        url,
    )
    print(f"Request with status code: {r.status_code}")

    json_data = json.loads(r.text)

    spaces = pd.DataFrame.from_dict(json_data["spaces"], orient="index")

    # fixing boolean
    spaces["private"] = spaces["private"].apply(
        lambda x: True if x == "true" or x is True else False
    )

    data = pd.DataFrame(json_data).drop(columns=["spaces"])

    explore_data = data.join(spaces)
    explore_data["scraped_at"] = pd.Timestamp.utcnow()

    numeric_cols = [
        "network",
        "proposals",
        "followers",
        "activeProposals",
        "followers_1d",
        "voters_1d",
        "proposals_1d",
    ]

    for col in numeric_cols:
        explore_data[col] = pd.to_numeric(explore_data[col])

    # TODO: Check why airbyte is failing processing this
    explore_data.drop(columns=["categories"], inplace=True)

    return explore_data


@task(log_stdout=True)
def extract_multiple_spaces_data(explore_data):

    number_of_daos = len(explore_data)
    number_of_requests = math.ceil(number_of_daos / 100)

    first = 100
    skip = 0
    increase = 100

    spaces_data = pd.DataFrame()

    for i in range(number_of_requests):

        query = f"""
            {{
        spaces(first: {first}, skip: {skip}, orderBy: "created", orderDirection: desc) {{
                id
                name
                about
                network
                symbol
                twitter
                domain
                avatar
                email
                private
                location
                github
                website
                terms
            }}
            }}
        """

        # print(f"First: {first}")
        # print(f"Skip: {skip}")

        url = "https://hub.snapshot.org/graphql"
        r = requests.get(url, json={"query": query})

        print(f"Request {i+1} of {number_of_requests} ({r.status_code})")

        json_data = json.loads(r.text)

        df = pd.json_normalize(json_data["data"]["spaces"])

        spaces_data = spaces_data.append(df)

        skip += increase

    spaces_data.set_index("id", inplace=True)
    spaces_data["scraped_at"] = pd.Timestamp.utcnow()

    return spaces_data


with Flow(
    FLOW_NAME,
    storage=STORAGE,
    run_config=RUN_CONFIG,
) as flow:

    aws_credentials = PrefectSecret("AWS_CREDENTIALS")

    explore_data = extract_snapshot_expore_data()
    spaces_data = extract_multiple_spaces_data(explore_data)

    result_explore = df_to_s3_parquet(
        df=explore_data,
        aws_credentials=aws_credentials,
        bucket="datadrivendao",
        file_name="explore",
        service_name="snapshot",
    )
    result_spaces = df_to_s3_parquet(
        df=spaces_data,
        aws_credentials=aws_credentials,
        bucket="datadrivendao",
        file_name="spaces",
        service_name="snapshot",
    )

    loaded_explore = airbyte_task(
        connection_id="f4d0f610-a053-4524-9e9b-c36ddd68915a"
    ).set_upstream(result_explore)

    loaded_spaces = airbyte_task(
        connection_id="6d7f919c-a20f-4f1f-91d0-6fe706dac10d"
    ).set_upstream(result_spaces)

if __name__ == "__main__":
    flow.register("datadrivendao")
