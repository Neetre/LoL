import requests
import json
import argparse
from scrap import get_riot_ids
import time

# import os
# import getpass
# if "RIOT_KEY" not in os.environ:
#     os.environ["RIOT_KEY"] = getpass.getpass('Enter your RIOT_KEY ---> ')
# RIOT_KEY = os.environ["RIOT_KEY"]
RIOT_KEY = None

'''
regions = {
    "europe" : ["euw1", "eun1", "tr1", "ru", "la1", "la2"],
    "americas" : ["na1", "br1"],
    "asia" : ["kr", "jp1", "ph2", "sg2", "th2", "tw2", "vn2"],
    "sea" : ["oc1"]
}
'''


def get_puuid(region, username, tag):
    request = requests.get(f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}?api_key={RIOT_KEY}")
    if request.status_code != 200:
        print("Error puuid: ", request.json())
        return None

    puuid = request.json()['puuid']
    return puuid


def get_info_user(server, puuid):
    info_user = requests.get(f"https://{server}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={RIOT_KEY}")
    if info_user.status_code != 200:
        print("Error info user: ", info_user.json())
        return None
    # print(info_user.json())
    return info_user


def get_user_matches(region, puuid, NUM_MATCHES=20):
    user_matches = requests.get(f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={NUM_MATCHES}&api_key={RIOT_KEY}")
    if user_matches.status_code != 200:
        print("Error user matches: ", user_matches.json())
        return None
    # print(user_matches.json())
    
    return user_matches.json()


def get_match_info(region, user_matches):
    game_ids = []
    if len(user_matches) > 1:
        for match in user_matches:
            while True:
                match_info = requests.get(f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match}?api_key={RIOT_KEY}")
                if match_info.status_code != 200:
                    print("Error match info: ", match_info.json())
                    return None
                if match_info.status_code == 429:
                    time.sleep(10)
                    print("Error 429: ", match_info.json())
                    print("Waiting 10 seconds...")
                    continue

                game_ids.append(match_info.json())
                return game_ids

    else:
        match_info = requests.get(f"https://{region}.api.riotgames.com/lol/match/v5/matches/{user_matches[0]}?api_key={RIOT_KEY}")
        if match_info.status_code != 200:
            print("Error match info: ", match_info.json())
            return None
        game_ids.append(match_info.json())

        return game_ids


def extract_match_info(match_info):
    # csv headers: gameId,creationTime,gameDuration,seasonId,winner,firstBlood,firstTower,firstInhibitor,firstBaron,firstDragon,firstRiftHerald,t1_champ1id,t1_champ1_sum1,t1_champ1_sum2,t1_champ2id,t1_champ2_sum1,t1_champ2_sum2,t1_champ3id,t1_champ3_sum1,t1_champ3_sum2,t1_champ4id,t1_champ4_sum1,t1_champ4_sum2,t1_champ5id,t1_champ5_sum1,t1_champ5_sum2,t1_towerKills,t1_inhibitorKills,t1_baronKills,t1_dragonKills,t1_riftHeraldKills,t1_ban1,t1_ban2,t1_ban3,t1_ban4,t1_ban5,t2_champ1id,t2_champ1_sum1,t2_champ1_sum2,t2_champ2id,t2_champ2_sum1,t2_champ2_sum2,t2_champ3id,t2_champ3_sum1,t2_champ3_sum2,t2_champ4id,t2_champ4_sum1,t2_champ4_sum2,t2_champ5id,t2_champ5_sum1,t2_champ5_sum2,t2_towerKills,t2_inhibitorKills,t2_baronKills,t2_dragonKills,t2_riftHeraldKills,t2_ban1,t2_ban2,t2_ban3,t2_ban4,t2_ban5
    champions_used = [match_info['info']['participants'][i]['championName'] for i in range(len(match_info['info']['participants']))]
    print(champions_used)


def get_other_players(match_info):
    players = match_info['metadata']['participants']
    print(players)


def get_champions():
    champions = requests.get("https://ddragon.leagueoflegends.com/cdn/14.14.1/data/en_US/champion.json")
    if champions.status_code != 200:
        print("Error champions: ", champions.json())
        return None
    champions = champions.json()
    # print(champions)

    with open("../data/new_champions.json", "w") as file:
        json.dump(champions, file, indent=4)

    return champions


def clear_champions(champions):
    new_champions = {}
    # print(champions['data']['Aatrox'])

    i = 1
    for campion in champions['data']:
        #print(champions['data'][campion])
        break

    # print(new_champions)

def args_parser():
    parser = argparse.ArgumentParser(description="RIOT API data manager")
    parser.add_argument("-k", "--key", help="The RIOT API key", required=True)
    parser.add_argument("-u", "--username", help="The username of the user", required=False)
    parser.add_argument("-t", "--tag", help="The tag of the user", required=False)
    parser.add_argument("-r", "--region", help="The region of the user ('europe', 'sea', 'asia', ...)", required=False)
    parser.add_argument("-s", "--server", help="The server of the user ('na1', 'euw1', 'kr', ...)", required=False)
    parser.add_argument("-n", "--num_matches", help="The number of matches to get", required=False)
    parser.add_argument("-ti", "--tier", help="The tier of the user ('challenger', 'grandmaster', 'master', ...)", required=False)
    parser.add_argument("-p", "--page", help="The page of the tier", required=False)
    return parser.parse_args()


def main():
    global RIOT_KEY
    args = args_parser()
    RIOT_KEY = args.key
    
    username = args.username
    tag = args.tag
    region = args.region
    server = args.server
    num_matches = args.num_matches
    tier = args.tier
    page = args.page
    
    riot_ids = get_riot_ids(server[:-1], tier, page)[0]
    
    puuid = get_puuid(region, riot_ids[0], riot_ids[1])
    info_user = get_info_user(server, puuid)
    user_matches = get_user_matches(region, puuid, num_matches)
    match_info = get_match_info(region, user_matches)
    for match in match_info:
        extract_match_info(match)
        # get_other_players(match)
        break
    # print(user_matches[0])
    champions = get_champions()
    clear_champions(champions)


if __name__ == "__main__":
    main()
