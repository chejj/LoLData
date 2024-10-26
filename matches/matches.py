from dotenv import load_dotenv
import os
import psycopg2
import requests
import time

rate_limit = 120/100

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

query = "SELECT puuid, region, tier, division FROM summoners WHERE region = 'na1';"
cursor.execute(query)

results = cursor.fetchall()
cursor.close()

region_mapping = {
    'br1': 'AMERICAS',
    'na1': 'AMERICAS',
    'la1': 'AMERICAS',
    'la2': 'AMERICAS',
    'eun1': 'EUROPE',
    'euw1': 'EUROPE',
    'tr1': 'EUROPE',
    'ru': 'EUROPE',
    'kr': 'ASIA',
    'jp1': 'ASIA',
    'oc1': 'SEA',
    'ph2': 'SEA',
    'sg2': 'SEA',
    'th2': 'SEA',
    'tw2': 'SEA',
    'vn2': 'SEA'
}

cursor = conn.cursor()

# October 23, 2024 @ 18:00:00 GMT
new_patch_epoch = 1729706400

for row in results:
    print(row)
    region = row[1]
    api_region = region_mapping[str(region)]
    tier = row[2]
    division = row[3]
    time.sleep(rate_limit)

    try:    
        response = requests.get(f'https://{api_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{row[0]}/ids?startTime={new_patch_epoch}&type=ranked&start=0&count=100&api_key={API_KEY}')
        response.raise_for_status
        response = response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        time.sleep(130)
        response = requests.get(f'https://{api_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{row[0]}/ids?startTime={new_patch_epoch}&type=ranked&start=0&count=100&api_key={API_KEY}')
        response.raise_for_status()
        response = response.json()
    except:
        print(f"An error occurred: {e}")
        time.sleep (300)
        continue
    
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