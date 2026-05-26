import pandas as pd

def calculate_conversion_rate(data):
    total_goals = len(data[data['event'] == 'Goal'])
    total_shots = len(data[data['event'] == 'Shot']) + total_goals
    return total_goals / total_shots * 100

def get_period_stats(game_data, game_plays_data, selected_season):
    season_map = game_data[['game_id', 'season']].drop_duplicates()
    shots = game_plays_data[
        (game_plays_data['event'].isin(['Shot', 'Goal'])) &
        (game_plays_data['period'] <= 3)
        ][['game_id', 'period', 'event']]
    shots = shots.merge(season_map, on='game_id')

    seasons = get_seasons(game_data)
    seasons.remove('Все сезоны')
    seasons = list(map(int, seasons))

    shots = shots[shots['season'].isin(seasons)]

    if selected_season != 'Все сезоны':
        shots = shots[shots['season'] == int(selected_season)]

    # Считаем реализацию через apply
    period_stats = shots.groupby('period').apply(calculate_conversion_rate).reset_index()
    period_stats.columns = ['period', 'conversion_rate']

    return period_stats

def get_seasons(game_data):
    seasons = sorted(map(str, list(game_data['season'].unique())))
    for s in ['20122013', '20182019', '20192020', '20002001', '20012002', '20022003', '20032004', '20052006',
              '20062007', '20072008', '20082009', '20092010']:
        seasons.remove(s)
    seasons.append('Все сезоны')
    seasons = sorted(seasons, reverse=True)
    return seasons


def get_players_data(game_data,
                     game_plays_players_data,
                     game_plays_data,
                     players_info_data,
                     selected_season):
    season_map = game_data[['game_id', 'season']].drop_duplicates()

    goal_players = game_plays_players_data[game_plays_players_data['playerType'] == 'Scorer'][['play_id', 'player_id']]
    goal_plays = goal_players.merge(
        game_plays_data[['play_id', 'game_id']], on='play_id'
    )
    goal_plays = goal_plays.merge(season_map, on='game_id')

    if selected_season != 'Все сезоны':
        goal_plays = goal_plays[goal_plays['season'].astype(str) == str(selected_season)]

    goal_players_info = goal_plays.merge(players_info_data[['player_id', 'birthDate', 'primaryPosition']],
                                         on='player_id')

    game_dates = game_plays_data.groupby('game_id')['dateTime'].first().reset_index()
    goal_players_info = goal_players_info.merge(game_dates, on='game_id')
    goal_players_info['birthDate'] = pd.to_datetime(goal_players_info['birthDate'])
    goal_players_info['gameDate'] = pd.to_datetime(goal_players_info['dateTime'])
    goal_players_info['age'] = (goal_players_info['gameDate'] - goal_players_info['birthDate']).dt.days / 365.25

    forwards = goal_players_info[goal_players_info['primaryPosition'].isin(['C', 'LW', 'RW', 'F', 'L', 'R'])]
    defensemen = goal_players_info[goal_players_info['primaryPosition'] == 'D']

    fwd_goals = forwards.groupby(forwards['age'].round().astype(int)).size().reset_index(name='goals')
    def_goals = defensemen.groupby(defensemen['age'].round().astype(int)).size().reset_index(name='goals')
    fwd_goals.columns = ['age', 'goals']
    def_goals.columns = ['age', 'goals']

    fwd_goals['pct'] = fwd_goals['goals'] / fwd_goals['goals'].max() * 100
    def_goals['pct'] = def_goals['goals'] / def_goals['goals'].max() * 100

    return fwd_goals, def_goals


def get_penalty_data(game_data,
                     game_plays_data,
                     game_plays_players_data,
                     game_skater_stats_data,
                     selected_season):
    season_map = game_data[['game_id', 'season']].drop_duplicates()

    ice_time = game_skater_stats_data[['game_id', 'player_id', 'timeOnIce']].copy()
    ice_time = ice_time.merge(season_map, on='game_id')

    if selected_season != 'Все сезоны':
        ice_time = ice_time[ice_time['season'].astype(str) == str(selected_season)]

    ice_time['rank'] = ice_time.groupby('game_id')['timeOnIce'].rank(ascending=False)

    leaders = ice_time[ice_time['rank'] <= 3].copy()
    bottom = ice_time[ice_time['rank'] >= 10].copy()
    leaders['group'] = 'Топ-3 (лидеры)'
    bottom['group'] = '3-4 звено'

    penalties = game_plays_data[game_plays_data['event'] == 'Penalty'][['play_id', 'game_id']]
    penalty_players = penalties.merge(
        game_plays_players_data[['play_id', 'player_id']], on='play_id'
    )
    penalty_counts = penalty_players.groupby(['game_id', 'player_id']).size().reset_index(name='penalty_count')

    leaders = leaders.merge(penalty_counts, on=['game_id', 'player_id'], how='left').fillna(0)
    bottom = bottom.merge(penalty_counts, on=['game_id', 'player_id'], how='left').fillna(0)

    all_players = pd.concat([leaders, bottom])
    means = all_players.groupby('group')['penalty_count'].mean().reset_index()

    return means