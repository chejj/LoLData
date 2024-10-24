from dotenv import load_dotenv
import os
import psycopg2
import requests
import time

load_dotenv('../env/.env')
API_KEY = os.environ.get("API_KEY")

tiers = ['IRON', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM','EMERALD', 'DIAMOND']
divisions = ['IV', 'III', 'II', 'I']
#regions = ['BR1', 'EUN1', 'EUW1', 'JP1', 'KR', 'LA1', 'LA2', 'NA1',
#          'OC1', 'PH2', 'RU', 'SG2', 'TH2', 'TR1', 'TW2', 'VN2']
region = 'NA1'

queue = 'RANKED_SOLO_5x5'
pageInt = 1

region_tier_division = {}

for tier in tiers:
    for division in divisions:
        key = f"{region}_{tier}_{division}"
        players = requests.get(f'https://{region}.api.riotgames.com/lol/league/v4/entries/{queue}/{tier}/{division}?page={pageInt}&api_key={API_KEY}').json()
        region_tier_division[key] = players

conn = psycopg2.connect(database="riotdb", user="jake", password="password", host="localhost", port="5432")
cursor = conn.cursor()

for key in region_tier_division:
    for index, summoner in enumerate(region_tier_division[key]):
        response = requests.get(f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner["summonerId"]}?api_key={API_KEY}')
        if response.status_code == 429:
            print("Reached rate limit, sleeping for 3 minutes")
            time.sleep(180)
            response = requests.get(f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{summoner["summonerId"]}?api_key={API_KEY}').json()
            
        else:
            response = response.json()
        
        summoner['puuid'] = response['puuid']
        insert_query = f'INSERT INTO summoners (puuid, summonerid, summonername, region, tier, division, wins, losses, hotstreak) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        value = (summoner['puuid'], summoner['summonerId'], summoner['summonerName'], region, summoner['tier'], summoner['rank'], summoner['wins'], summoner['losses'], summoner['hotStreak'])
        try:
            cursor.execute(insert_query, value)
            conn.commit()
            print("Data inserted successfully.")
        except (Exception, psycopg2.Error) as error:
            conn.rollback()
            print("Error inserting data:", error)
            break
            
cursor.close()
conn.close()