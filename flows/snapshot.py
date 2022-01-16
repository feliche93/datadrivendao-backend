from datetime import datetime
from math import ceil
import requests
import json
import pandas as pd
import math
from prefect.run_configs import ECSRun
from prefect.storage import Docker
from prefect import task, Flow
import prefect
from datetime import datetime
import awswrangler as wr
import boto3
from prefect.tasks.secrets import PrefectSecret
from prefect.client.secrets import Secret
import pyarrow as pa


RUN_CONFIG = ECSRun(
    image="262367897508.dkr.ecr.eu-central-1.amazonaws.com/datadrivendao:latest",
    cpu="256",
    memory="512",
    labels=["prod"],
    task_role_arn="arn:aws:iam::262367897508:role/prefectTaskRole",
    execution_role_arn="arn:aws:iam::262367897508:role/prefectECSAgentTaskExecutionRole",
    run_task_kwargs=dict(
        cluster="prefectEcsCluster",
        launchType="FARGATE",
    ),
)

STORAGE = Docker(
    registry_url="262367897508.dkr.ecr.us-east-1.amazonaws.com",
    image_name="datadrivendao",
    dockerfile="Dockerfile",
)

FLOW_NAME = "extract_snapshot_data"


@task(log_stdout=True)
def df_to_s3_parquet(df, aws_credentials, bucket, file_name, service_name):

    session = boto3.Session(
        region_name="us-east-1",
        aws_access_key_id=aws_credentials.get("ACCESS_KEY"),
        aws_secret_access_key=aws_credentials.get("SECRET_ACCESS_KEY"),
    )

    date_path = f"{datetime.now().strftime('%Y/%m/%d')}"
    key = f"{service_name}/{date_path}/{file_name}.parquet"
    bucket = "datadrivendao"
    path = f"s3://{bucket}/{key}"

    result = wr.s3.to_parquet(
        df=df,
        path=path,
        dataset=False,
        boto3_session=session,
    )

    print(f"Written parquet file to: {result['paths']}")

    return result


@task(log_stdout=True)
def extract_snapshot_expore_data():

    url = "https://hub.snapshot.org/api/explore"
    r = requests.get(
        url,
    )
    print(r.status_code)

    json_data = json.loads(r.text)

    spaces = pd.DataFrame.from_dict(json_data["spaces"], orient="index")

    # fixing boolean
    spaces["private"] = spaces["private"].apply(lambda x: True if x == "true" or x is True else False)

    data = pd.DataFrame(json_data).drop(columns=["spaces"])

    explore_data = data.join(spaces)
    explore_data["scraped_at"] = pd.Timestamp.utcnow()
    explore_data["network"] = pd.to_numeric(explore_data["network"])

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
                plugins
                avatar
                email
                private
                categories
                location
                github
                website
                terms
                admins
                members
                plugins
            }}
            }}
        """

        print(f"Request {i+1} of {number_of_requests}")
        print(f"First: {first}")
        print(f"Skip: {skip}")

        url = "https://hub.snapshot.org/graphql"
        r = requests.get(url, json={"query": query})
        print(r.status_code)

        json_data = json.loads(r.text)

        # TODO: Remove old code when not neeeded
        # cleaning strategy data
        # for record in json_data["data"]["spaces"]:
        #     for strategy in record["strategies"]:
        #         d = strategy["params"]
        #         keys = ['symbol', 'address', "decimals"]
        #         filtered_d = dict((k, d[k]) for k in keys if k in d)
        #         strategy["params"] = filtered_d

        df = pd.json_normalize(json_data["data"]["spaces"])

        spaces_data = spaces_data.append(df)

        skip += increase

    spaces_data.set_index("id", inplace=True)
    spaces_data["network"] = pd.to_numeric(spaces_data["network"])

    # TODO: Remove old code when not neeeded
    # normalizing strategy data
    # putting every strategy into it's own column
    # strategy_df = pd.DataFrame(spaces_data["strategies"].to_list(), index=spaces_data.index)
    # strategy_df_columns = [f"strategy_{col+1}" for col in range(len(strategy_df.columns))]
    # strategy_df.columns = strategy_df_columns
    # strategy_df.index = spaces_data.index

    # normalizing nested json into several columns
    # for col in strategy_df_columns:
    #     noramlized_df = pd.json_normalize(strategy_df[col])
    #     noramlized_df = noramlized_df.add_prefix(f"{col}_")
    #     noramlized_df.index = strategy_df.index
    #     strategy_df = strategy_df.join(noramlized_df)

    # dropping nested ones
    # strategy_df.drop(columns=strategy_df_columns, inplace=True)

    # merging strategy data with spaces data for final df
    # spaces_data.drop(columns=["strategies"], inplace=True)
    # spaces_data = spaces_data.join(strategy_df)

    # adding scraping timestamp
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

    df_to_s3_parquet(
        df=explore_data,
        aws_credentials=aws_credentials,
        bucket="datadrivendao",
        file_name="explore_data",
        service_name="snapshot",
    )
    df_to_s3_parquet(
        df=spaces_data,
        aws_credentials=aws_credentials,
        bucket="datadrivendao",
        file_name="spaces_data",
        service_name="snapshot",
    )

if __name__ == "__main__":
    flow.register("datadrivendao")
