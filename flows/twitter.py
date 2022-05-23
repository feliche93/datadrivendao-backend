"""Module to extract Twitter data."""

import pandas as pd
import requests
import tweepy
from prefect import Flow, task
from prefect.tasks.secrets import PrefectSecret

from common import df_to_gcs_parquet
from flow_config import RUN_CONFIG, STORAGE


@task(log_stdout=True)
def get_screen_names(api_route: str) -> list:
    # sourcery skip: raise-specific-error
    """Gets screen names from Twitter API.

    Args:
        api_route (str): API route to get screen names from.

    Raises:
        Exception: If API call fails.

    Returns:
        list: List of screen names.
    """

    response = requests.get(api_route)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")

    twitter_profile_urls = response.json()
    twitter_profile_urls = [e for e in twitter_profile_urls if e != "https://twitter.com/"]
    twitter_profile_urls = [e for e in twitter_profile_urls if e is not None]

    screen_names = [url.split("https://twitter.com/")[-1] for url in twitter_profile_urls]

    screen_names = list(set(screen_names))

    print(f"Found {len(screen_names)} DAOs")

    return screen_names


@task(log_stdout=True)
def auth_twitter(
    twitter_consumer_key: str,
    twitter_consumer_secret: str,
    twitter_access_token: str,
    twitter_access_token_secret: str,
) -> tweepy.API:  # sourcery skip: do-not-use-bare-except
    """Creates tweepy API object.

    Args:
        twitter_consumer_key (str): Consumer key
        twitter_consumer_secret (str): Consumer secret
        twitter_access_token (str): Access tooken
        twitter_access_token_secret (str): Twitter access token

    Returns:
        tweepy.API: API Instance
    """

    try:
        auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
        auth.set_access_token(twitter_access_token, twitter_access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

    except:
        print("An error occurred during the authentication")  # sourcery skip: do-not-use-bare-except

    return api


@task(log_stdout=True)
def get_users(api: tweepy.API, screen_names: list) -> pd.DataFrame:
    """Gets users from Twitter API.

    Args:
        api (tweepy.API): Instance of tweepy API
        screen_names (list): List of screen names

    Returns:
        pd.DataFrame: DataFrame of users
    """

    df_users = pd.DataFrame()

    size = 100
    list_of_screen_names = [screen_names[ i : i + size] for i in range(0, len(screen_names), size)]

    for list_screen_names in list_of_screen_names:

        users = api.lookup_users(screen_name=list_screen_names)
        json_response = [result._json for result in users]

        df_users = df_users.append(pd.json_normalize(json_response))

    return df_users


FLOW_NAME = "extract_twitter_data"

with Flow(
    FLOW_NAME,
    storage=STORAGE,
    run_config=RUN_CONFIG,
) as flow:

    api_route = "https://datadrivendao.xyz/api/daos"
    host = "mongodb://159.223.147.152:56728/"
    google_service_account = PrefectSecret("GOOGLE_SERVICE_ACCOUNT")
    twitter_consumer_key = PrefectSecret("TWITTER_CONSUMER_KEY")
    twitter_consumer_secret = PrefectSecret("TWITTER_CONSUMER_SECRET")
    twitter_access_token = PrefectSecret("TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret = PrefectSecret("TWITTER_ACCESS_TOKEN_SECRET")

    api = auth_twitter(
        twitter_consumer_key,
        twitter_consumer_secret,
        twitter_access_token,
        twitter_access_token_secret,
    )

    screen_names = get_screen_names(api_route)

    df_users = get_users(api, screen_names)

    result_users = df_to_gcs_parquet(
        df_users,
        google_service_account,
        bucket="datadrivendao",
        file_name="users",
        service_name="twitter",
    )

if __name__ == "__main__":
    # flow.run()
    flow.register(project_name="datadrivendao")
