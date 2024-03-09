import requests
from helper import transform_region
from utils import get_last_session_games
from playerStats import LolGame
import settings


api_key = settings.LOL_API_KEY


# def get_summoner(region, name):
#     response = requests.get(
#         f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={api_key}"
#     )
#     data = response.json()
#     return data

def get_summoner(region, lol_name:str):
    name, tag= lol_name.split('#')
    response = requests.get(
        f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={api_key}"
    )
    data = response.json()
    return data


def get_summoner_by_puuid(region, puuid):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
    )
    data = response.json()
    return data

def get_all_matches(region, puuid, page=4):
    url =  f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={page}&api_key={api_key}"
    try:
            response = requests.get(
                url
            )
            # Vérifier le code de statut de la réponse
            if response.status_code == 200:
                # Traitement en cas de succès
                return response.json()
            else:
                # Gérer les réponses non réussies (par exemple, 404, 401, 403)
                return {'erreur': 'La requête a échoué', 'code_statut': response.status_code}
    except requests.exceptions.RequestException as e:
        # Gérer les exceptions pour des problèmes de requête
        return {'erreur': f'Erreur de requête: {str(e)}'}



def get_rank(region, id):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}?api_key={api_key}"
    )
    data = response.json()
    return data

def get_mastery_points(region, id):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}?api_key={api_key}"
    )
    data = response.json()
    return data



def get_match(region, match_id):
    
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    response = requests.get(
        url
    )
    data = response.json()
    return data["info"]



def get_user_rank(puuid:str):
    summoner = get_summoner_by_puuid('euw1', puuid)
    rank = get_rank('euw1', summoner['id'])
    return next((element for element in rank if element['queueType'] == 'RANKED_SOLO_5x5'), None)



from playerStats import get_session_stats
def get_session_games(lol_user_name):

    summoner = get_summoner('europe', lol_user_name)
    summoner_puuid = "rCt_aJGIP3rHvcBqoYIpvPg3Z05LzY8l2aPvyVNYEQjOV-NIrJnqGTMIFK_7Iye_itfrrR3OfEczhg"#summoner['puuid']

    matches = get_all_matches('europe', summoner_puuid)

    m = []
    for element in matches:
        match = get_match('europe', element)
        m.append(match)
    matches_lol_game_obj = [LolGame(game_dto, summoner_puuid) for game_dto in m]
    session_matches = get_last_session_games(matches_lol_game_obj)
    
    session_stats = get_session_stats(session_matches)
    session_stats['rank'] = get_user_rank(summoner_puuid)

    return session_stats
