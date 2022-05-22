from pymongo import MongoClient
from datetime import datetime
import requests
import pandas as pd
from slugify import slugify

DATE_TODAY = datetime.now().strftime("%Y/%m/%d")

AWS_S3_BUCKET = "datadrivendao"
KEY_SPACES = f"snapshot/{DATE_TODAY}/spaces.parquet"
KEY_EXPLORE = f"snapshot/{DATE_TODAY}/explore.parquet"

spaces = pd.read_parquet(f"s3://{AWS_S3_BUCKET}/{KEY_SPACES}")
explore = pd.read_parquet(f"s3://{AWS_S3_BUCKET}/{KEY_EXPLORE}")

# Min requirement of +100 Followers on Snapshot
explore = explore[explore["followers"] >= 100]

spaces = spaces[spaces["id"].isin(explore["index"].to_list())]

target_cols = [
    "id",
    "name",
    "about",
    "symbol",
    "twitter",
    "website",
    "avatar",
    "github",
]

spaces = spaces[target_cols]


spaces.rename(
    columns={
        "id": "ensDomain",
        "twitter": "twitterProfileUrl",
        "github": "githubProfileUrl",
        "website": "websiteUrl",
        "avatar": "avatarUrl",
    },
    inplace=True,
)


def create_snapshot_url(ensDomain):
    url = f'https://snapshot.org/#/{ensDomain}'

    r = requests.get(url)

    if r.status_code == 200:
        return url


def create_github_url(githubProfileUrl):
    if githubProfileUrl is not None:

        url = f"https://github.com/{githubProfileUrl}"

        return url

def fix_avatar_url(avatarUrl):

    configured_domains= [
      'pbs.twimg.com',
      'abs.twimg.com',
      'cloudflare-ipfs.com',
      'gateway.pinata.cloud',
      'ipfs.io',
      'images.unsplash.com',
      'pbs.twimg.com',
      'avatars.githubusercontent.com',
      'raw.githubusercontent.com',
      'i.imgur.com',
    ]

    if avatarUrl is not None:
        if avatarUrl.startswith('ipfs://'):
            url = f"https://ipfs.io/ipfs/{avatarUrl.split('://')[1]}"

            return url

        if avatarUrl not in configured_domains:
            return

        if requests.get(avatarUrl).status_code == 200:
            return avatarUrl

spaces['snapshotProfileUrl'] = spaces['ensDomain'].apply(create_snapshot_url)
spaces['githubProfileUrl'] = spaces['githubProfileUrl'].apply(create_github_url)
spaces['twitterProfileUrl'] = spaces['twitterProfileUrl'].apply(lambda x: f'https://twitter.com/{x}' if x is not None else x)

spaces['avatarUrl'] = spaces['avatarUrl'].apply(fix_avatar_url)

spaces['createdAt'] = datetime.now()
spaces['updatedAt'] = datetime.now()
spaces['verified'] = False
spaces['source'] = 'snaphot'
spaces['slug'] = spaces['name'].apply(slugify)

# removing duplicate slugs and keeping those with more Followers
df = pd.merge(spaces, explore[["name", "followers"]], on="name", how='left')
df = df.sort_values(['slug','followers'], ascending=[True, False])
df.drop(columns=['followers'], inplace=True)

client = MongoClient("mongodb://159.223.147.152:56728/")

db = client["parse"]

collection = db["Daos"]

for index, row in df.iterrows():

    row = row.to_dict()

    for key, value in dict(row).items():
        if value is None:
            del row[key]

    collection.update_one({'slug': row["slug"]}, {'$set': row}, upsert=True)
