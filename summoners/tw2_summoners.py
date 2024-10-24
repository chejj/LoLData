from dotenv import load_dotenv
import os
import requests
import time
import json

load_dotenv('../env/.env')
API_KEY = os.environ.get('API_KEY')
sleep_duration = 100/120

tiers = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM','EMERALD', 'DIAMOND']
divisions = ['IV', 'III', 'II', 'I']

#regions = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1',
#          'OC1', 'PH2', 'RU', 'SG2', 'TH2', 'TR1', 'TW2', 'VN2']

region = 'TW2'
queue = 'RANKED_SOLO_5x5'
pageInt = 1

summoners = {}

summoners[region] = {}
for tier in tiers:
    summoners[region][tier] = {}
    for division in divisions:
        time.sleep(sleep_duration)
        players = requests.get(f'https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={pageInt}&api_key={API_KEY}').json()
        summoners[region][tier][division] = {}
        for player in players:
            summoners[region][tier][division] = players

for tier in summoners[region][tier]:
    for division in tier:
        for summoner in division:
            time.sleep(sleep_duration)

            try:
                response = requests.get(f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner["summonerId"]}?api_key={API_KEY}')
                response.raise_for_status()
                summoner['puuid'] = response.json().get('puuid')
            except requests.exceptions.HTTPError as e:

                print(f"HTTP error occurred: {e}")
                time.sleep(130)
                response = requests.get(f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner["summonerId"]}?api_key={API_KEY}')
                response.raise_for_status()
                summoner['puuid'] = response.json().get('puuid')

            except Exception as e:
                print(f"An error occurred: {e}")

with open(f"jsons/{region}_summoners.json", "w") as f:
    json.dump(summoners, f, indent=4)