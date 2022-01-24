import requests
import pandas as pd

headers = {
    'authority': 'discord.com',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    'x-super-properties': 'eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJkZSIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS85Ny4wLjQ2OTIuNzEgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6Ijk3LjAuNDY5Mi43MSIsIm9zX3ZlcnNpb24iOiIxMC4xNS43IiwicmVmZXJyZXIiOiJodHRwczovL2ZvcnVtLmRldmVsb3BlcmRhby5jb20vIiwicmVmZXJyaW5nX2RvbWFpbiI6ImZvcnVtLmRldmVsb3BlcmRhby5jb20iLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTExMzMwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
    'x-debug-options': 'bugReporterEnabled',
    'sec-ch-ua-mobile': '?0',
    'authorization': 'ODI2NTYwNjc3NzUzMjU4MDE0.YeWhog.XYkmEwMqePZJLd7kcf4exRC9dvI',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'x-discord-locale': 'en-US',
    'sec-ch-ua-platform': '"macOS"',
    'accept': '*/*',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://discord.com/channels/883478451850473483/883495211064524811',
    'accept-language': 'de,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': '__dcfduid=f8e9110073c811ecac36376bd8ba3864; __sdcfduid=f8e9110173c811ecac36376bd8ba3864ac123e47baff8df4a4441d83f70c10d47b79f76dbd3cb09c8f9f3905f7563d36; _ga=GA1.2.571407696.1642698279; _gid=GA1.2.2147087594.1642698279; OptanonConsent=isIABGlobal=false&datestamp=Thu+Jan+20+2022+18%3A18%3A41+GMT%2B0100+(Central+European+Standard+Time)&version=6.17.0&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0&AwaitingReconsent=false; locale=en-US',
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