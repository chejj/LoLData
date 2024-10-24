from dotenv import load_dotenv
import os
import psycopg2
import requests
import time

load_dotenv('../env/.env')
API_KEY = os.environ.get('API_KEY')

tiers = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM','EMERALD', 'DIAMOND']
divisions = ['IV', 'III', 'II', 'I']

#regions = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1',
#          'OC1', 'PH2', 'RU', 'SG2', 'TH2', 'TR1', 'TW2', 'VN2']

region = 'NA1'
queue = 'RANKED_SOLO_5x5'
pageInt = 1

summoners = {}

summoners[region] = {}
for tier in tiers:
    summoners[region][tier] = {}
    for division in divisions:
        players = requests.get(f'https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={pageInt}&api_key={API_KEY}').json()
        summoners[region][tier][division] = {}
        for player in players:
            summoners[region][tier][division] = players