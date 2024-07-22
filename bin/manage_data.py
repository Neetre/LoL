import requests
import json
import os
import getpass

if "RIOT_KEY" not in os.environ:
    os.environ["RIOT_KEY"] = getpass.getpass('Enter your RIOT_KEY ---> ')
RIOT_KEY = os.environ["RIOT_KEY"]


username = input("Enter your username: ")
tag = input("Enter your tag: ")


def get_puuid(username, tag):
    request = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{username}/{tag}?api_key={RIOT_KEY}")
    puuid = request.json()['puuid']
    return puuid


def get_info_user(puuid):
    info_user = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={RIOT_KEY}")
    # print(info_user.json())
    return info_user


def get_user_matches(puuid):
    NUM_MATCHES = 100
    user_matches = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={NUM_MATCHES}&api_key={RIOT_KEY}")
    # print(user_matches.json())

    for match in user_matches.json():
        match_info = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{match}?api_key={RIOT_KEY}")
        # print(match_info.json())
        # nice headers: gameId,creationTime,gameDuration,seasonId,winner,firstBlood,firstTower,firstInhibitor,firstBaron,firstDragon,firstRiftHerald,t1_champ1id,t1_champ1_sum1,t1_champ1_sum2,t1_champ2id,t1_champ2_sum1,t1_champ2_sum2,t1_champ3id,t1_champ3_sum1,t1_champ3_sum2,t1_champ4id,t1_champ4_sum1,t1_champ4_sum2,t1_champ5id,t1_champ5_sum1,t1_champ5_sum2,t1_towerKills,t1_inhibitorKills,t1_baronKills,t1_dragonKills,t1_riftHeraldKills,t1_ban1,t1_ban2,t1_ban3,t1_ban4,t1_ban5,t2_champ1id,t2_champ1_sum1,t2_champ1_sum2,t2_champ2id,t2_champ2_sum1,t2_champ2_sum2,t2_champ3id,t2_champ3_sum1,t2_champ3_sum2,t2_champ4id,t2_champ4_sum1,t2_champ4_sum2,t2_champ5id,t2_champ5_sum1,t2_champ5_sum2,t2_towerKills,t2_inhibitorKills,t2_baronKills,t2_dragonKills,t2_riftHeraldKills,t2_ban1,t2_ban2,t2_ban3,t2_ban4,t2_ban5

        # print(match_info.json()['info']['participants'])

        break

def get_champions():
    champions = requests.get("https://ddragon.leagueoflegends.com/cdn/14.14.1/data/en_US/champion.json")
    champions = champions.json()
    # print(champions)

    with open("../data/new_champions.json", "w") as file:
        json.dump(champions, file, indent=4)

    return champions


def clear_champions(champions):
    new_champions = {}

    for campion in champions['data']:
        new_champions[campion['key']] = {
            "id": campion['id'],
            "name": campion['name'],
            "title": campion['title']
        }

    print(new_champions)


def main():
    puuid = get_puuid(username, tag)
    info_user = get_info_user(puuid)
    get_user_matches(puuid)
    champions = get_champions()
    clear_champions(champions)


if __name__ == "__main__":
    main()