import pandas as pd
import tweepy
from prefect.tasks.secrets import PrefectSecret
from google.oauth2 import service_account
from prefect import task, Flow

from common import df_to_s3_parquet
from flow_config import RUN_CONFIG, STORAGE


@task(log_stdout=True)
def get_dims_daos(service_account_info):

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info
    )

    sql = """
        SELECT * FROM dbt.dims_daos
    """

    df = pd.read_gbq(sql, project_id="datadrivendao", credentials=credentials)

    return df


@task(log_stdout=True)
def get_missing_twitter_names(df, api):

    no_twitter = df[df["twitter"].isnull()]
    names = no_twitter["name"].to_list()

    for name in names:
        try:
            user = api.search_users(q=name, count=1)
            twitter = user[0]._json.get("screen_name")
            df.loc[df["name"] == name, "twitter"] = twitter
        except IndexError as e:
            print(f"No twitter found for: {name}")

    df.set_index("id", inplace=True)

    return df[["twitter"]]


@task(log_stdout=True)
def auth_twitter(
    twitter_consumer_key,
    twitter_consumer_secret,
    twitter_access_token,
    twitter_access_token_secret,
):

    try:
        auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
        auth.set_access_token(twitter_access_token, twitter_access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

    except:
        print("An error occurred during the authentication")

    return api


@task(log_stdout=True)
def get_users(api, df):

    df_users = pd.DataFrame()

    size = 100
    list_of_dfs = [df.loc[i : i + size - 1, :] for i in range(0, len(df), size)]

    for df in list_of_dfs:

        names = df[df["twitter"].notnull()]["twitter"].to_list()

        # try:
        users = api.lookup_users(screen_name=names)
        json_response = [result._json for result in users]
        df_users = df_users.append(pd.json_normalize(json_response))
        # except tweepy.TweepError as e:
        #     print(f"An error occurred: {e}")

    return df_users


FLOW_NAME="extract_twitter_data"

with Flow(
    FLOW_NAME,
    storage=STORAGE,
    run_config=RUN_CONFIG,
) as flow:

    google_service_account = PrefectSecret("GOOGLE_SERVICE_ACCOUNT")
    twitter_consumer_key = PrefectSecret("TWITTER_CONSUMER_KEY")
    twitter_consumer_secret = PrefectSecret("TWITTER_CONSUMER_SECRET")
    twitter_access_token = PrefectSecret("TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret = PrefectSecret("TWITTER_ACCESS_TOKEN_SECRET")
    aws_credentials = PrefectSecret("AWS_CREDENTIALS")

    api = auth_twitter(
        twitter_consumer_key,
        twitter_consumer_secret,
        twitter_access_token,
        twitter_access_token_secret,
    )

    df_daos = get_dims_daos(service_account_info=google_service_account)

    df_users = get_users(api, df_daos)


    # result_daos = df_to_s3_parquet(
    #     df_daos,
    #     aws_credentials,
    #     bucket="datadrivendao",
    #     file_name="twitter_screen_names",
    #     service_name="twitter",
    # )

    result_users = df_to_s3_parquet(
        df_users,
        aws_credentials,
        bucket="datadrivendao",
        file_name="twitter_users",
        service_name="twitter",
    )
