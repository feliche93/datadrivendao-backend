import os
import requests
import pandas as pd

headers = {
    'clientId': os.getenv('DISCORD_CLIENT_ID'),
    'authorization': f"Bot {os.getenv('DISCORD_TOKEN')}"
}


def get_channel_info(channel_id):

    response = requests.get(
        f'https://discord.com/api/v9/channels/{channel_id}',
        headers=headers,
    )

    return pd.json_normalize(response.json())


def get_guild_info(guild_id):

    response = requests.get(
        f'https://discord.com/api/v9/guilds/{guild_id}',
        headers=headers,
        params={'with_counts': 'true'}
    )

    return pd.json_normalize(response.json())


def get_channel_messages(channel_id):

    response = requests.get(
        f'https://discord.com/api/v9/channels/{channel_id}/messages',
        headers=headers,
        params={'limit': 100}
    )

    return pd.json_normalize(response.json())


guild_id = '883478451850473483' # DeveloperDAO
channel_id = '883495211064524811' # Announcements

df_guild_info = get_guild_info(guild_id)
df_channel_info = get_channel_info(channel_id)
df_channel_messages = get_channel_messages(channel_id)

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.get('https://discord.com/api/v9/channels/883495211064524811/messages?limit=50', headers=headers)'