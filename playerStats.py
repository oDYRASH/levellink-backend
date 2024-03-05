from utils import get_player_session_stats_mean

class LolGame:
    def __init__(self, match_dto, puuid):
        self.MatchDto = match_dto
        self.player = PlayerData(next((summoner for summoner in match_dto['participants'] if summoner['puuid'] == puuid), None))

    @property
    def game_duration(self):
        return self.MatchDto['gameDuration']

    @property
    def game_end_timestamp(self):
        return self.MatchDto['gameEndTimestamp']

    @property
    def game_start_timestamp(self):
        return self.MatchDto['gameStartimestamp']

    @property
    def game_id(self):
        return self.MatchDto['gameId']

    @property
    def game_mode(self):
        return self.MatchDto['gameMode']

    @property
    def game_name(self):
        return self.MatchDto['gameName']

    @property
    def game_type(self):
        return self.MatchDto['gameType']

    @property
    def game_version(self):
        return self.MatchDto['gameVersion']

    @property
    def queue_id(self):
        return self.MatchDto['queueId']


class PlayerData:
    def __init__(self, player_data):
        self.player_data = player_data

    @property
    def game_duration(self):
        return self.player_data['challenges']['gameLength']

    @property
    def assists(self):
        return self.player_data['assists']

    @property
    def kills(self):
        return self.player_data['kills']

    @property
    def deaths(self):
        return self.player_data['deaths']

    @property
    def kda_ratio(self):
        return round(self.player_data['challenges']['kda'], 2)

    @property
    def kda_string(self):
        return f"{self.kills} / {self.assists} / {self.deaths}"

    @property
    def kill_participation_percentage(self):
        return round(self.player_data['challenges']['killParticipation'] * 100)

    @property
    def champ_level(self):
        return self.player_data['champLevel']

    @property
    def champion_name(self):
        return self.player_data['championName']

    @property
    def win(self):
        return self.player_data['win']

    @property
    def items(self):
        return [self.player_data[f'item{i}'] for i in range(7)]

    @property
    def total_minions_killed(self):
        return self.player_data['totalMinionsKilled']

    @property
    def neutral_minions_killed(self):
        return self.player_data['neutralMinionsKilled']

    @property
    def cs(self):
        return self.neutral_minions_killed + self.total_minions_killed

    @property
    def cs_min(self):
        return round(self.cs / (self.game_duration / 60), 1)

    @property
    def total_damage_dealt_to_champions(self):
        return self.player_data['totalDamageDealtToChampions']

    @property
    def damage_per_minute(self):
        return round(self.player_data['challenges']['damagePerMinute'])

    @property
    def summoner1_id(self):
        return self.player_data['summoner1Id']

    @property
    def summoner2_id(self):
        return self.player_data['summoner2Id']

    @property
    def main_rune(self):
        return self.player_data['perks']['styles'][0]['selections'][0]['perk']

    @property
    def secondary_rune(self):
        return self.player_data['perks']['styles'][1]['style']

    @property
    def gold_earned(self):
        return self.player_data['goldEarned']

    @property
    def gold_per_minute(self):
        return round(self.player_data['challenges']['goldPerMinute'])

    @property
    def vision_score(self):
        return self.player_data['visionScore']

    @property
    def vision_score_per_minute(self):
        return round(self.player_data['challenges']['visionScorePerMinute'], 2)

    @property
    def team_position(self):
        return self.player_data['teamPosition']


def get_session_game_base_stats(session_games):
    return [
        {
            'title': 'KDA',
            'value': f"{get_player_session_stats_mean(session_games, 'kills')} / {get_player_session_stats_mean(session_games, 'deaths')} / {get_player_session_stats_mean(session_games, 'assists')}"
        },
        {
            'title': 'CS / min',
            'value': get_player_session_stats_mean(session_games, 'CSmin')
        },
        {
            'title': 'DGT / min',
            'value': get_player_session_stats_mean(session_games, 'damagePerMinute')
        }
    ]

def calculate_win_percentage(games):
    if not games:
        return 0
    win_count = sum(1 for game in games if game.player.win)
    return round((win_count / len(games)) * 100)

def get_session_stats(session_games):
    win_rate = calculate_win_percentage(session_games)
    session_game_count = len(session_games)
    return {
        'sessionGameCount': session_game_count,
        'winRate': win_rate
    }
