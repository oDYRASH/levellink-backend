def get_player_session_stats_mean(session_games, player_stat):
    if not session_games:
        return 0  # Retourner 0 si le tableau est vide pour éviter une division par zéro

    total_stat = sum(getattr(game.player, player_stat, 0) for game in session_games)
    return round(total_stat / len(session_games), 1)

def get_last_session_games(data):
    sorted_data = sorted(data, key=lambda x: x['gameEndTimestamp'], reverse=True)
    filtered_array = []

    if not sorted_data:
        return filtered_array

    for i in range(len(sorted_data) - 1):
        game_space_hour = (sorted_data[i]['gameEndTimestamp'] - sorted_data[i + 1]['gameEndTimestamp']) / 3600000

        if i == 0 or game_space_hour < 1.2:
            filtered_array.append(sorted_data[i])
        else:
            filtered_array.append(sorted_data[i])
            break

    return filtered_array
