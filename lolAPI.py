import requests
from helper import transform_region
from utils import get_last_session_games
from playerStats import LolGame
import settings


api_key = settings.LOL_API_KEY

async def get_summoner(region, name):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={api_key}"
    )
    data = response.json()
    return data

async def get_rank(region, id):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}?api_key={api_key}"
    )
    data = response.json()
    return data

async def get_mastery_points(region, id):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}?api_key={api_key}"
    )
    data = response.json()
    return data

async def get_all_matches(region, puuid, page=17):
    region_ = transform_region(region)
    response = requests.get(
        f"https://{region_}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={page}&api_key={api_key}"
    )
    data = response.json()
    return data

async def get_match(region, match_id):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    )
    data = response.json()
    return data['info']

async def get_session_games(lol_user_name):
    summoner = await get_summoner('euw1', lol_user_name)
    summoner_puuid = summoner['puuid']
    matches = await get_all_matches('euw1', summoner_puuid)
    m = []
    for element in matches:
        match = await get_match('europe', element)
        m.append(match)
    matches_lol_game_obj = [LolGame(game_dto, summoner_puuid) for game_dto in m]
    session_matches = get_last_session_games(matches_lol_game_obj)
    return session_matches

async def get_user_rank(lol_user_name):
    summoner = await get_summoner('euw1', lol_user_name)
    rank = await get_rank('euw1', summoner['id'])
    return next((element for element in rank if element['queueType'] == 'RANKED_SOLO_5x5'), None)
