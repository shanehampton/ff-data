import pandas as pd
import numpy as np

from constants import STAT_LOOKBACK_GAMES


def calc_stat_pg(games: pd.DataFrame, player: str, year: int, stat_name: str, n: int = STAT_LOOKBACK_GAMES):
    '''
    Calculates stat as mean per-game value over last n games
    '''
    try:
        return round(games.loc[(games.player == player) & (games.year < year)].sort_values('date', ascending=False)[:n][stat_name].mean(), 2)
    except:
        return np.nan


def calc_stat_total(games: pd.DataFrame, player: str, year: int, stat_name: str, n: int = STAT_LOOKBACK_GAMES):
    '''
    Calculates stat as total over last n games
    '''
    try:
        return games.loc[(games.player == player) & (games.year < year)].sort_values('date', ascending=False)[:n][stat_name].sum()
    except:
        return np.nan


def calc_100rush(games: pd.DataFrame, player: str, year: int, n: int = STAT_LOOKBACK_GAMES) -> int:
    '''
    Calculates 100-yard rushing games over last n games
    '''
    try:
        _100rush = games.loc[(games.player == player) & (
            games.year < year) & (games.rush_yd >= 100)].index.size
    except:
        _100rush = 0
    return 0 if pd.isna(_100rush) else _100rush


def calc_100rec(games: pd.DataFrame, player: str, year: int, n: int = STAT_LOOKBACK_GAMES) -> int:
    '''
    Calculates 100-yard receiving games over last n games
    '''
    try:
        _100rec = games.loc[(games.player == player) & (
            games.year < year) & (games.rec_yd >= 100)].index.size
    except:
        _100rec = 0
    return 0 if pd.isna(_100rec) else _100rec


def calc_awards_cr(seasons: pd.DataFrame, player: str, year: int) -> int:
    try:
        awards_cr = seasons.loc[(seasons.player == player) & (
            seasons.year < year)].awards.sum()
    except:
        awards_cr = 0
    return awards_cr


def calc_exp_team(seasons: pd.DataFrame, player: str, year: int) -> int:
    try:
        _team = seasons.loc[(seasons.player == player) & (
            seasons.year == year)].team.values[0]
        exp_team = seasons.loc[(seasons.player == player) & (
            seasons.year < year)].team.str.contains(_team).sum()
    except:
        exp_team = 0
    return exp_team


def calc_award_last_season(seasons: pd.DataFrame, player: str, year: int) -> bool:
    try:
        award_last_season = seasons.loc[(seasons.player == player) & (
            seasons.year == year - 1)].awards.sum() >= 1
    except:
        award_last_season = False
    return award_last_season


def calc_rush_att_cr(games: pd.DataFrame, player: str, year: int, n: int = 24) -> int:
    try:
        rush_att_cr = games.loc[(games.player == player) & (
            games.year < year)].sort_values('date', ascending=False)[:n].rush_att.sum()
    except:
        rush_att_cr = 0
    return rush_att_cr


def calc_gp_perc(players: pd.DataFrame, seasons: pd.DataFrame, games: pd.DataFrame, player: str, year: int, n: int = 3) -> float or np.nan:
    try:
        player_first_yr = int(
            players.loc[players.id == player].draft_year.values[0])
    except:  # undrafted player
        player_first_yr = seasons.loc[seasons.player == player].year.min()
    n = min(year - player_first_yr, n)
    if n > 0:
        season_years = list(range(year - n, year))
        eligibility = []
        for yr in season_years:
            if yr < 2021:
                eligibility.append(16)
            else:
                eligibility.append(17)
        eligible_games = sum(eligibility)
        games_played = games.loc[(games.player == player) & (
            games.year < year) & (games.year >= year - n)].index.size
        return round(games_played / eligible_games, 2)
    else:  # rookie
        return np.nan
