from html import entities
import pandas as pd
import tweepy
from prefect.tasks.secrets import PrefectSecret
from google.oauth2 import service_account

from common import df_to_s3_parquet

@task(log_stdout=True)
def get_dims_daos(service_account_info):

    credentials = service_account.Credentials.from_service_account_info(service_account_info)

    sql="""
        SELECT * FROM dbt.dims_daos
    """

    df = pd.read_gbq(sql, project_id="datadrivendao", credentials=credentials)

    return df

@task(log_stdout=True)
def find_missing_twitter_names(df, api):

    no_twitter = df[df['twitter'].isnull()]
    names = no_twitter['name'].to_list()

    for name in names:
        try:
            user = api.search_users(q=name, count=1)
            twitter = user[0]._json.get("screen_name")
            df.loc[df['name'] == name, 'twitter'] = twitter
        except IndexError as e:
            print(f"No twitter found for: {name}")

    return df[['id', 'twitter']]

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


google_service_account = PrefectSecret("GOOGLE_SERVICE_ACCOUNT").run()
twitter_consumer_key = PrefectSecret("TWITTER_CONSUMER_KEY").run()
twitter_consumer_secret = PrefectSecret("TWITTER_CONSUMER_SECRET").run()
twitter_access_token = PrefectSecret("TWITTER_ACCESS_TOKEN").run()
twitter_access_token_secret = PrefectSecret("TWITTER_ACCESS_TOKEN_SECRET").run()
aws_credentials = PrefectSecret("AWS_CREDENTIALS").run()


api = auth_twitter(
    twitter_consumer_key,
    twitter_consumer_secret,
    twitter_access_token,
    twitter_access_token_secret,
)

df = get_dims_daos(service_account_info=google_service_account)

result = df_to_s3_parquet(
    df, aws_credentials,
    bucket="datadrivendao",
    file_name="twitter_screen_names",
    service_name="twitter"
)