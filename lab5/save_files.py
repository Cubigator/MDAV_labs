from lab5.functions import get_period_stats, get_players_data, get_penalty_data, get_seasons
import pandas as pd

game_data = pd.read_csv('archive/game.csv')
game_plays_data = pd.read_csv('archive/game_plays.csv')
game_plays_players_data = pd.read_csv('archive/game_plays_players.csv')
players_info_data = pd.read_csv('archive/player_info.csv')
game_skater_stats_data = pd.read_csv('archive/game_skater_stats.csv')

period_stats = get_period_stats(game_data, game_plays_data, 'Все сезоны')
period_stats.to_csv('datalens/periods_stats.csv', index=False)

fwd, def_ = get_players_data(game_data, game_plays_players_data, game_plays_data, players_info_data, 'Все сезоны')
fwd['type'] = 'Нападающие'
def_['type'] = 'Защитники'
age_stats = pd.concat([fwd, def_])
age_stats.to_csv('datalens/age_peak_stats.csv', index=False)

means = get_penalty_data(game_data, game_plays_data, game_plays_players_data, game_skater_stats_data, 'Все сезоны')
means.to_csv('datalens/discipline_stats.csv', index=False)