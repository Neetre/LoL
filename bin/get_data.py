import requests
import json
import os
import getpass

if "RIOT_KEY" not in os.environ:
    os.environ["RIOT_KEY"] = getpass.getpass('Enter your RIOT_KEY ---> ')
RIOT_KEY = os.environ["RIOT_KEY"]

username = input("Enter your username: ")
tag = input("Enter your tag: ")

request = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}?api_key={RIOT_KEY}")
puuid = request.json()['puuid']

request = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={RIOT_KEY}")

print(request.json())

request = requests.get(f"https://europe.api.riftkit.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10&api_key={RIOT_KEY}")
print(request.json())