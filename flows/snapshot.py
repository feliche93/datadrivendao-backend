import requests
import json
import pandas as pd
import math
from prefect import task, Flow
from prefect.tasks.secrets import PrefectSecret
from prefect.tasks.airbyte.airbyte import AirbyteConnectionTask

from common import df_to_gcs_parquet
from flow_config import RUN_CONFIG, STORAGE

FLOW_NAME = "extract_snapshot_data"

# airbyte_task = AirbyteConnectionTask(
#     airbyte_server_host="34.206.52.76",
# )


@task(log_stdout=True)
def extract_snapshot_expore_data():

    url = "https://hub.snapshot.org/api/explore"
    r = requests.get(
        url,
    )
    print(f"Request with status code: {r.status_code}")

    json_data = json.loads(r.text)

    df = pd.DataFrame.from_dict(json_data["spaces"], orient="index")

    # fixing boolean
    df["private"] = df["private"].apply(
        lambda x: True if x == "true" or x is True else False
    )

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
        df[col] = pd.to_numeric(df[col])

    df.reset_index(inplace=True)
    df.rename(columns={"index": "id"}, inplace=True)

    return df


@task(log_stdout=True)
def extract_multiple_spaces_data(explore_data):

    number_of_daos = len(explore_data)

    print(f"Total Number of Daos: {number_of_daos}")

    number_of_requests = math.ceil(number_of_daos / 100)

    first = 100
    skip = 0
    increase = 100

    spaces_data = pd.DataFrame()

    for i in range(number_of_requests):

        query = """
            query Spaces($first: Int, $skip: Int) {
            spaces(first: $first, skip: $skip, orderBy: "created", orderDirection: desc) {
                id
                name
                symbol
                about
                location
                avatar
                network
                categories
                email
                domain
                github
                twitter
                website
                admins
                members
                followersCount
                proposalsCount
                private
                skin
                terms
            }
            }
        """

        url = "https://hub.snapshot.org/graphql"

        variables={"first": first, "skip": skip}

        r = requests.get(url, json={"query": query, "variables": variables})

        print(f"Request {i+1} of {number_of_requests} (Status Code: {r.status_code})")

        json_data = json.loads(r.text)

        df = pd.json_normalize(json_data["data"]["spaces"])

        spaces_data = spaces_data.append(df)

        skip += increase

    spaces_data.drop_duplicates(subset=['id'], inplace=True)

    return spaces_data


with Flow(
    FLOW_NAME,
    storage=STORAGE,
    run_config=RUN_CONFIG,
) as flow:

    google_service_account = PrefectSecret("GOOGLE_SERVICE_ACCOUNT")

    explore_data = extract_snapshot_expore_data()

    result_explore = df_to_gcs_parquet(
        df=explore_data,
        google_service_account=google_service_account,
        bucket="datadrivendao",
        file_name="explore",
        service_name="snapshot",
    )

    spaces_data = extract_multiple_spaces_data(explore_data)

    result_spaces = df_to_gcs_parquet(
        df=spaces_data,
        google_service_account=google_service_account,
        bucket="datadrivendao",
        file_name="spaces",
        service_name="snapshot",
    )

if __name__ == "__main__":
    flow.register("datadrivendao")
    # flow.run()
