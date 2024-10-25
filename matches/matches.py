from dotenv import load_dotenv
import os
import psycopg2
import requests
import time

load_dotenv('../env/.env')
API_KEY = os.environ.get("API_KEY")
db_password = os.environ.get("db_password")
db_host = os.environ.get("db_host")

conn = psycopg2.connect(
    database="riot_db",
    user="jacob",
    password=db_password,
    host=db_host,
    port="5432",
    sslmode="disable"
)
cursor = conn.cursor()

query = "SELECT puuid, region, tier, division FROM summoners;"
cursor.execute(query)

results = cursor.fetchall()
cursor.close()

def map_region(value):
    region_mapping = {
        'BR1': 'AMERICAS',
        'NA1': 'AMERICAS',
        'LA1': 'AMERICAS',
        'LA2': 'AMERICAS',
        'EUN1': 'EUROPE',
        'EUW1': 'EUROPE',
        'TR1': 'EUROPE',
        'RU': 'EUROPE',
        'KR': 'ASIA',
        'JP1': 'ASIA',
        'OC1': 'SEA',
        'PH2': 'SEA',
        'SG2': 'SEA',
        'TH2': 'SEA',
        'TW2': 'SEA',
        'VN2': 'SEA'
    }
    return region_mapping.get(value, 'UNKNOWN')

cursor = conn.cursor()

# October 23, 2024 @ 18:00:00 GMT
newMapEpoch = 1729706400

for row in results:
    region = map_region(row[1])
    tier = row[2]
    division = row[3]
    response = requests.get(f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{row[0]}/ids?startTime={newMapEpoch}&type=ranked&start=0&count=100&api_key={API_KEY}').json()
    for match in response:
        query = f"INSERT INTO matches (matchid, region, tier, division, queried) VALUES (%s, %s, %s, %s, %s)"
        values = (str(match), region, tier, division, False)
        try:
            cursor.execute(query, values)

            conn.commit()
                
            print("Data inserted successfully.")
        except (Exception, psycopg2.Error) as error:
            conn.rollback()
            print("Error inserting data:", error) 

cursor.close()
conn.close()