from dotenv import load_dotenv
import os
import json
import psycopg2

load_dotenv('../env/.env')
db_password = os.environ.get('db_password')
db_host = os.environ.get('db_host')

def summoner_upload(region: str):
    with open(f"jsons/{region}_summoners.json", "r") as file:
        summoners = json.load(file)

    conn = psycopg2.connect(
        database="riot_db",
        user="jacob",
        password=db_password,
        host=db_host,
        port="5432",
        sslmode="disable"
    )
    cursor = conn.cursor()

    for tier in summoners[region]:
        for division in summoners[region][tier]:
            for summoner in summoners[region][tier][division]:
                insert_query = f'INSERT INTO summoners (puuid, summonerid, region, tier, division, wins, losses, hotstreak, freshBlood) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                if 'puuid' not in summoner:
                    print("Missing 'puuid' key, exiting loop.")
                    break
                value = (summoner['puuid'], summoner['summonerId'], region, summoner['tier'], summoner['rank'], summoner['wins'], summoner['losses'], summoner['hotStreak'], summoner['freshBlood'])
                try:
                    cursor.execute(insert_query, value)
                    conn.commit()
                    print("Data inserted successfully.")
                except (Exception, psycopg2.Error) as error:
                    conn.rollback()
                    print("Error inserting data:", error)
                    continue

    cursor.close()
    conn.close()

regions = ['la1', 'la2', 'na1']

for region in regions:
    summoner_upload(region)

