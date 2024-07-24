import requests
import json
import argparse
from scrap import get_riot_ids
import time
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = "https://{}.api.riotgames.com"
DDRAGON_URL = "https://ddragon.leagueoflegends.com/cdn/14.14.1/data/en_US/champion.json"
RIOT_KEY = os.getenv("RIOT_KEY")


# Utility function for API requests
def make_request(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None


# Rate limiter decorator
def rate_limit(func):
    def wrapper(*args, **kwargs):
        while True:
            result = func(*args, **kwargs)
            if result is not None:
                return result
            if result.status_code == 404:
                return None
            logging.info("Rate limit reached. Waiting 10 seconds...")
            time.sleep(10)
    return wrapper


@rate_limit
def get_puuid(region, username, tag):
    url = f"{BASE_URL}/riot/account/v1/accounts/by-riot-id/{username}/{tag}"
    data = make_request(url.format(region), params={"api_key": RIOT_KEY})
    return data['puuid'] if data else None


@rate_limit
def get_info_user(server, puuid):
    url = f"{BASE_URL}/lol/summoner/v4/summoners/by-puuid/{puuid}"
    return make_request(url.format(server), params={"api_key": RIOT_KEY})


@rate_limit
def get_user_matches(region, puuid, num_matches=20):
    url = f"{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"start": 0, "count": num_matches, "api_key": RIOT_KEY}
    return make_request(url.format(region), params=params)


@rate_limit
def get_match_info(region, match_id):
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}"
    return make_request(url.format(region), params={"api_key": RIOT_KEY})


def get_champions():
    return make_request(DDRAGON_URL)


def clear_champions(champions):
    new_champions = {
        "type": "champion",
        "version": champions['version'],
        "data": {}
    }
    base = new_champions.copy()
    
    for i, (key, champ) in enumerate(champions['data'].items(), start=1):
        if champ['name'] == 'Fiddlesticks':
            champ_name = 'FiddleSticks' # what the hell
        else:
            champ_name = champ['name']

        champ_data = {
            "title": champ['title'],
            "id": i,
            "key": champ_name,
            "name": champ_name
        }
        new_champions['data'][str(i)] = champ_data
        base['data'][key] = champ_data
    
    return new_champions, base


def extract_match_info(match_info, base):
    info = match_info['info']
    teams = info['teams']
    
    # Check for invalid positions
    if any(p['individualPosition'] == 'INVALID' for p in info['participants']):
        logging.info(f"Skipping match {info['gameId']} due to invalid position")
        return None

    data = [
        info['gameId'],
        info['gameCreation'],
        info['gameDuration'],
        info['gameVersion'].split('.')[0],
        1 if teams[0]['win'] else 2,
        1 if teams[0]['objectives']['champion']['first'] else 2,
        1 if teams[0]['objectives']['tower']['first'] else 2,
        1 if teams[0]['objectives']['inhibitor']['first'] else 2,
        1 if teams[0]['objectives']['baron']['first'] else 2,
        1 if teams[0]['objectives']['dragon']['first'] else 2,
        1 if teams[0]['objectives']['riftHerald']['first'] else 2
    ]
    
    position_map = {"TOP": 1, "JUNGLE": 2, "MIDDLE": 3, "BOTTOM": 4, "UTILITY": 5}
    
    try:
        champions = sorted(
            [(p['championName'], position_map[p['individualPosition']]) 
             for p in info['participants']],
            key=lambda x: (x[1], x[0])
        )
    except KeyError as e:
        logging.warning(f"Unexpected position in match {info['gameId']}: {e}")
        return None

    champion_ids = []
    for champ, _ in champions:
        if champ not in base['data']:
            logging.warning(f"Unknown champion '{champ}' in match {info['gameId']}")
            return None
        champion_ids.append(base['data'][champ]['id'])

    data.extend(champion_ids)
    
    return data


def write_to_csv(filename, data):
    print(data)
    try:
        with open(filename, "a") as file:
            file.write(",".join(map(str, data)) + "\n")
    except IOError as e:
        logging.error(f"Error writing to CSV: {e}")


def main():
    parser = argparse.ArgumentParser(description="RIOT API data manager")
    parser.add_argument("-u", "--username", required=False, help="The username of the user")
    parser.add_argument("-t", "--tag", required=False, help="The tag of the user")
    parser.add_argument("-r", "--region", required=True, help="The region of the user")
    parser.add_argument("-s", "--server", required=True, help="The server of the user")
    parser.add_argument("-n", "--num_matches", type=int, default=20, help="The number of matches to get")
    parser.add_argument("-ti", "--tier", required=True, help="The tier of the user")
    parser.add_argument("-p", "--page", required=True, help="The page of the tier")
    args = parser.parse_args()

    champions = get_champions()
    new_champions, base = clear_champions(champions)
    with open("../data/champion_info_3.json", "w") as file:
        json.dump(new_champions, file, indent=4)

    csv_file = f"../data/game_{args.tier}.csv"
    if not os.path.exists(csv_file):
        headers = "gameId,creationTime,gameDuration,seasonId,winner,firstBlood,firstTower,firstInhibitor,firstBaron,firstDragon,firstRiftHerald," + \
                  ",".join([f"t{i}_champ{j}id" for i in range(1, 3) for j in range(1, 6)])
        write_to_csv(csv_file, headers.split(','))
    
    riot_ids = get_riot_ids("kr" if args.server == "kr" else args.server[:-1], args.tier, args.page)
    for riot_id in riot_ids:
        puuid = get_puuid(args.region, riot_id[0], riot_id[1])
        
        if puuid:
            user_matches = get_user_matches(args.region, puuid, args.num_matches)
            for match_id in user_matches:
                match_info = get_match_info(args.region, match_id)
                if match_info:
                    data = extract_match_info(match_info, base)
                    if data:
                        write_to_csv(csv_file, data)
                    else:
                        logging.info(f"Skipped match {match_id} due to invalid data")


if __name__ == "__main__":
    main()