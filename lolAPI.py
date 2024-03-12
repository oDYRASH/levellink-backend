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

    # print("api key", api_key)

    name, tag= lol_name.split('#')
    # print(f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={api_key}")
    response = requests.get(
        f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={api_key}"
    )
    if response.status_code == 200:
                # Traitement en cas de succès
        return response.json()
    else:
        print({'erreur get_summoner()': 'La requête a échoué', 'code_statut': response.status_code})
        # Gérer les réponses non réussies (par exemple, 404, 401, 403)
        return {'erreur': 'La requête a échoué', 'code_statut': response.status_code}

def get_summoner_by_puuid(region, puuid):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
    )
    if response.status_code == 200:
                # Traitement en cas de succès
        return response.json()
    else:
        print({'erreur get_summoner_by_puuid()': 'La requête a échoué', 'code_statut': response.status_code})
        # Gérer les réponses non réussies (par exemple, 404, 401, 403)
        return {'erreur': 'La requête a échoué', 'code_statut': response.status_code}

def get_all_matches(region, puuid, page=10):
    url =  f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count={page}&api_key={api_key}"
    try:
            response = requests.get(
                url
            )
            # Vérifier le code de statut de la réponse
            if response.status_code == 200:
                # Traitement en cas de succès
                return response.json()
            else:
                print({'erreur get_all_matches()': 'La requête a échoué', 'code_statut': response.status_code})
                # Gérer les réponses non réussies (par exemple, 404, 401, 403)
                return {'erreur': 'La requête a échoué', 'code_statut': response.status_code}
    except requests.exceptions.RequestException as e:
        # Gérer les exceptions pour des problèmes de requête
        return {'erreur': f'Erreur de requête: {str(e)}'}



def get_rank(region, id):
    url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}?api_key={api_key}"
    response = requests.get(
        url
    )
    if response.status_code == 200:
                # Traitement en cas de succès
        return response.json()
    else:
        print({'erreur get_rank()': 'La requête a échoué', 'code_statut': response.status_code})
        # Gérer les réponses non réussies (par exemple, 404, 401, 403)
        return {'erreur': 'La requête a échoué', 'code_statut': response.status_code}

def get_mastery_points(region, id):
    response = requests.get(
        f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}?api_key={api_key}"
    )
    if response.status_code == 200:
                # Traitement en cas de succès
        return response.json()
    else:
        print({'erreur get_mastery_points()': 'La requête a échoué', 'code_statut': response.status_code})
        # Gérer les réponses non réussies (par exemple, 404, 401, 403)
        return {'erreur': 'La requête a échoué', 'code_statut': response.status_code}



def get_match(region, match_id):
    
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
    response = requests.get(
        url
    )
    if response.status_code == 200:
                # Traitement en cas de succès
        data = response.json()
        return data["info"]
    else:
        print({'erreur get_match()': 'La requête a échoué', 'code_statut': response.status_code})
        # Gérer les réponses non réussies (par exemple, 404, 401, 403)
        return {'erreur': 'La requête a échoué', 'code_statut': response.status_code}



def get_user_rank(puuid:str):
    summoner = get_summoner_by_puuid('euw1', puuid)
    rank = get_rank('euw1', summoner['id'])
    return next((element for element in rank if element['queueType'] == 'RANKED_SOLO_5x5'), None)


# function that is sending using multiple time get_match function to get all the games of a user uising multithreading 
from concurrent.futures import ThreadPoolExecutor
from playerStats import get_session_stats
def get_session_games(lol_user_name):

    summoner = get_summoner('europe', lol_user_name)
    summoner_puuid =  "kJFhUfu49K3RDx23fWMhOnA_bd_j6fjt3zwpGzKhg2hQBtFFTkq4ThInnbqI0Tg_VVqDcjX-A2l9UA"#summoner['puuid']#
    # print("summoner_puuid :", summoner_puuid)

    matches = get_all_matches('europe', summoner_puuid)
    # print("matches :", matches)
    
    # m = []
    # for element in matches:
    #     match = get_match('europe', element)
    #     print("match n°", len(m))
    #     m.append(match)
    # matches_lol_game_obj = [LolGame(game_dto, summoner_puuid) for game_dto in m]
    
    m = []

    with ThreadPoolExecutor() as executor:
        for element in matches:
            matche_res = executor.submit(get_match, 'europe', element)
            # print("match n°", len(m))
            m.append(matche_res)

    matches_lol_game_obj = [LolGame(game_dto.result(), summoner_puuid) for game_dto in m]

    # print('matches_lol_game_obj :', len(matches_lol_game_obj))

    session_matches = get_last_session_games(matches_lol_game_obj)
    
    session_stats = get_session_stats(session_matches)
    session_stats['rank'] = get_user_rank(summoner_puuid)
    # print('session_stats :', session_stats['rank'])
    return session_stats





# get_all_games("Thrysta#2346")