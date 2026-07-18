import json
import re
import time
import pandas as pd
import numpy as np
from datetime import datetime
from bs4 import BeautifulSoup, Comment
from urllib.request import urlopen

from constants import SCRAPE_PLAYER_COUNT

SKILL_POSITIONS = [
    'QB',
    'RB',
    'WR',
    'TE'
]

OL_POSITIONS = [
    'OL',
    'LT',
    'LG',
    'C',
    'RG',
    'RT',
    'G',
    'OG',
    'T',
    'C/LG',
    'LG/C',
    'RG/C'
    'C/RG',
    'C-G',
    'G-C',
    'G-T',
    'T-G',
    'C-T',
    'T-C',
    'G-T-C'
]

OFFENSIVE_POSITIONS = SKILL_POSITIONS + OL_POSITIONS

PLAYER_COLS = [
    'id',
    'position',
    'height',
    'weight',
    'dob',
    'pro_relatives',
    'forty',
    'bench',
    'broad_jump',
    'shuttle',
    'cone',
    'vertical'
]

PLAYER_SEASON_COLS = [
    'player',
    'year',
    'season_num',
    'team',
    'age',
    'av'
]

PLAYER_GAME_COLS = [
    'player',
    'year',
    'date',
    'game_num',
    'week_num',
    'team',
    'opp',
    'home',
    'result',
    'team_score',
    'opp_score',
    'active',
    'start',
    'dnp_reason',
    'pass_comp',
    'pass_att',
    'pass_yd',
    'pass_td',
    'pass_int',
    'qb_rate',
    'rush_att',
    'rush_yd',
    'rush_td',
    'rec',
    'rec_tgt',
    'rec_yd',
    'rec_td'
]

TRANSACTION_COLS = [
    'player',
    'date',
    'txn_type'
]

TEAM_SEASON_COLS = [
    'team',
    'year',
    'win_pct',
    'proj_win_pct',
    'proj_sb_odds',
]

TEAM_GAME_COLS = [
    'team',
    'year',
    'date',
    'game_num',
    'week_num',
    'opp',
    'home',
    'result',
    'team_score',
    'opp_score',
    'pass_comp',
    'pass_att',
    'pass_yd',
    'pass_td',
    'pass_int',
    'qb_rate',
    'sack',
    'rush_att',
    'rush_yd',
    'rush_td',
    'team_top',
    'opp_top',
    'fourth_down_att',
    'fourth_down_conv',
    'third_down_att',
    'third_down_conv'
]

TEAM_COACH_COLS = [
    'team',
    'year',
    'coach',
    'role',
    'start_game_num',
    'end_game_num'
]

TEAM_ROSTER_COLS = [
    'team',
    'year',
    'player',
    'position'
]

DRAFT_PICK_COLS = [
    'year',
    'round',
    'pick',
    'team',
    'player',
    'age',
    'position'
]

AWARD_COLS = [
    'year',
    'award_type',
    'player',
    'vote_share',
    'win'
]

ALL_PRO_COLS = [
    'year',
    'player'
]

PRO_BOWL_COLS = [
    'year',
    'player'
]

TEAMS = [
    'buf',
    'mia',
    'nwe',
    'nyj',
    'jax',
    'oti',
    'clt',
    'htx',
    'cin',
    'rav',
    'pit',
    'cle',
    'kan',
    'sdg',
    'rai',
    'den',
    'phi',
    'dal',
    'nyg',
    'was',
    'tam',
    'atl',
    'nor',
    'car',
    'min',
    'det',
    'gnb',
    'chi',
    'sfo',
    'sea',
    'ram',
    'crd'
]

TRAIN_COLS_BASE = [
    'season_id',
    'age',
    'season_num',
    'draft_cap',
    'draft_age',
    'height',
    'weight',
    'pro_relatives',
    'forty',
    'bench',
    'broad_jump',
    'shuttle',
    'cone',
    'vertical',
    'career_starts',
    'games_exp_team',
    'games_exp_coach',
    # 'starter',
    'career_av',
    'av_last_season',
    'drafted_by_coach',
    'traded_recently',
    'injured_recently',
    'career_injuries',
    'missed_game_pct',
    'all_pro_ratio',
    'all_pro_last_season',
    'pro_bowl_ratio',
    'pro_bowl_last_season',
    'mvp_cand_last_season',
    'opoy_cand_last_season',
    'cpoy_cand_last_season',
    'oroy_cand_last_season',
    'team_proj_win_pct',
    'team_proj_sb_odds',
    'team_win_pct_last_season',
    'team_roster_turnover',
    'team_pos_turnover',
    'team_age',
    'team_inc_draft_cap_total',
    'team_inc_draft_cap_pos',
    'team_ol_draft_cap',
    'team_ol_career_av',
    'team_ol_all_pro_ratio',
    'team_ol_pro_bowl_ratio',
    'team_ol_career_starts',
    'team_ol_size_index',
    'team_ol_turnover',
    'team_qb_rate',
    'team_qb_draft_cap',
    'team_qb_career_av',
    'team_qb_all_pro_ratio',
    'team_qb_pro_bowl_ratio',
    'team_qb_career_starts',
    'team_qb_pass_att',
    'team_qb_pass_yd',
    'team_qb_pass_td',
    'team_qb_comp_pct',
    'team_qb_rush_rate',
    'team_qb_rush_share',
    'team_qb_rush_td_share',
    'team_rb_draft_cap',
    'team_rb_career_av',
    'team_rb_all_pro_ratio',
    'team_rb_pro_bowl_ratio',
    'team_rb_career_starts',
    'team_rb_career_rush_att',
    'team_rb_rush_share',
    'team_rb_rush_yd',
    'team_rb_rush_td',
    'team_rb_rush_td_share',
    'team_rb_rush_td_rate',
    'team_rb_touch',
    'team_rb_yd_touch',
    'team_rb_tgt_share',
    'team_rb_rec_yd',
    'team_rb_rec_td',
    'team_rb_forty',
    'team_rb_bench',
    'team_rb_shuttle',
    'team_rb_broad_jump',
    'team_rb_cone',
    'team_rb_vertical',
    'team_wr_draft_cap',
    'team_wr_career_av',
    'team_wr_all_pro_ratio',
    'team_wr_pro_bowl_ratio',
    'team_wr_career_starts',
    'team_wr_career_rec',
    'team_wr_tgt_share',
    'team_wr_rec',
    'team_wr_rec_yd',
    'team_wr_yd_touch',
    'team_wr_yd_tgt',
    'team_wr_rec_td',
    'team_wr_rec_td_share',
    'team_wr_rec_td_rate',
    'team_wr_height',
    'team_wr_forty',
    'team_wr_bench',
    'team_wr_shuttle',
    'team_wr_broad_jump',
    'team_wr_cone',
    'team_wr_vertical',
    'team_te_draft_cap',
    'team_te_career_av',
    'team_te_all_pro_ratio',
    'team_te_pro_bowl_ratio',
    'team_te_starts',
    'team_te_career_rec',
    'team_te_tgt_share',
    'team_te_rec',
    'team_te_rec_yd',
    'team_te_yd_touch',
    'team_te_yd_tgt',
    'team_te_rec_td',
    'team_te_rec_td_share',
    'team_te_rec_td_rate',
    'team_te_height',
    'team_te_forty',
    'team_te_bench',
    'team_te_shuttle',
    'team_te_broad_jump',
    'team_te_cone',
    'team_te_vertical',
    'hc_season_num',
    'hc_season_num_team',
    'hc_win_pct',
    'coach_pass_pct',
    'coach_pass_yd_pct',
    'coach_pass_td_pct',
    'coach_qb_rate',
    'coach_pass_yd_comp',
    'coach_total_yd',
    'coach_top_pct',
    'coach_tempo',
    'coach_yd_play',
    'coach_fourth_down_att',
    'coach_rush_conc',
    'coach_tgt_conc',
    'coach_wr_tgt_share',
    'coach_rb_tgt_share',
    'coach_te_tgt_share'
]

TRAIN_COLS_QB = [
    'win_pct',
    'qb_rate',
    'td_int_ratio',
    'comp_pct',
    'rush_rate',
    'rush_share',
    'rush_yd',
    'rush_td',
    'rush_td_share',
    'pass_att',
    'pass_yd',
    'pass_td',
    'pass_yd_comp',
    'team_wr_tgt_history',
    'team_te_tgt_history',
    'team_rb_tgt_history'
]

TRAIN_COLS_RB = [
    'career_rush_att',
    'rush_share',
    'rush_yd',
    'rush_td',
    'rush_td_share',
    'rush_td_rate',
    'touch',
    'yd_touch',
    'career_tgt_qb',
    'tgt_share',
    'yd_tgt',
    'rec',
    'rec_yd',
    'rec_td',
    'catch_rate'
]

TRAIN_COLS_WR = [
    'career_rec',
    'career_tgt_qb',
    'tgt_share',
    'rec',
    'rec_yd',
    'yd_touch',
    'yd_tgt',
    'rec_td',
    'rec_td_share',
    'rec_td_rate',
    'catch_rate'
]

TRAIN_COLS_TE = [
    'career_rec',
    'career_tgt_qb',
    'tgt_share',
    'rec',
    'rec_yd',
    'yd_touch',
    'yd_tgt',
    'rec_td',
    'rec_td_share',
    'rec_td_rate',
    'catch_rate'
]


class FFData:
    def __init__(self):
        self.players = pd.read_csv('csv/players.csv', index_col=0)
        self.player_seasons = pd.read_csv('csv/player_seasons.csv', index_col=0)
        self.player_games = pd.read_csv('csv/player_games.csv', index_col=0)
        self.all_pros = pd.read_csv('csv/all_pros.csv', index_col=0)
        self.awards = pd.read_csv('csv/awards.csv', index_col=0)
        self.draft_picks = pd.read_csv('csv/draft_picks.csv')
        self.team_seasons = pd.read_csv('csv/team_seasons.csv', index_col=0)
        self.team_games = pd.read_csv('csv/team_games_new.csv', index_col=0)
        self.team_coaches = pd.read_csv('csv/team_coaches.csv')
        self.rosters = pd.read_csv('csv/rosters.csv')
        self.pro_bowls = pd.read_csv('csv/pro_bowls.csv', index_col=0)
        self.transactions = pd.read_csv('csv/transactions.csv', index_col=0)
        self.draft_pick_values = pd.read_csv('csv/draft_pick_values.csv', index_col=0)
        self.train_base = pd.DataFrame(columns=TRAIN_COLS_BASE)


def scrape_master(start_year: int = 1996, end_year: int = 2022) -> dict:
    roster_df = pd.DataFrame(columns=TEAM_ROSTER_COLS)
    player_df = pd.DataFrame(columns=PLAYER_COLS)
    player_season_df = pd.DataFrame(columns=PLAYER_SEASON_COLS)
    player_game_df = pd.DataFrame(columns=PLAYER_GAME_COLS)
    transaction_df = pd.DataFrame(columns=TRANSACTION_COLS)
    team_coach_df = pd.DataFrame(columns=TEAM_COACH_COLS)
    team_season_df = pd.DataFrame(columns=TEAM_SEASON_COLS)
    team_game_df = pd.DataFrame(columns=TEAM_GAME_COLS)
    print('executing scrape_master()...')
    award_df = get_awards()
    draft_pick_df = get_draft_picks()
    all_pro_df = get_all_pros()
    pro_bowl_df = get_pro_bowls()
    for team in TEAMS:
        team_coach_entry = get_team_coaches(team)
        team_coach_df = pd.concat(
            [team_coach_df, team_coach_entry],
            ignore_index=True
        )
        team_season_entry = get_team_seasons(team)
        team_season_df = pd.concat(
            [team_season_df, team_season_entry],
            ignore_index=True
        )
        for year in range(start_year, end_year + 1):
            try:
                (roster_entry, player_df, player_season_df, player_game_df, transaction_df) = get_team_roster(
                    team,
                    year,
                    player_df=player_df,
                    player_game_df=player_game_df,
                    player_season_df=player_season_df,
                    transaction_df=transaction_df
                )
                roster_df = pd.concat(
                    [roster_df, roster_entry],
                    ignore_index=True
                )
            except:
                continue
            try:
                team_game_entry = get_team_games(team, year)
                team_game_df = pd.concat(
                    [team_game_df, team_game_entry],
                    ignore_index=True
                )
            except:
                continue
    return {
        'roster_df': roster_df,
        'player_df': player_df,
        'player_season_df': player_season_df,
        'player_game_df': player_game_df,
        'transaction_df': transaction_df,
        'team_coach_df': team_coach_df,
        'team_season_df': team_season_df,
        'team_game_df': team_game_df,
        'award_df': award_df,
        'draft_pick_df': draft_pick_df,
        'all_pro_df': all_pro_df,
        'pro_bowl_df': pro_bowl_df
    }


def get_player_full(player_id: str, soup: BeautifulSoup = None) -> tuple:
    if soup is None:
        url = f'https://www.pro-football-reference.com/players/{player_id[0].upper()}/{player_id}.htm'
        soup = get_soup(url)
    player_df = get_player_details(player_id, soup=soup)
    player_season_df = get_player_seasons(player_id, soup=soup)
    player_transaction_df = get_transactions(player_id, soup=soup)
    return player_df, player_season_df, player_transaction_df


def get_player_details(player_id: str, soup: BeautifulSoup = None) -> pd.DataFrame:
    player_df = pd.DataFrame(columns=PLAYER_COLS)
    url = f'https://www.pro-football-reference.com/players/{player_id[0].upper()}/{player_id}.htm'
    if soup is None:
        soup = get_soup(url)
    try:
        position = re.search(
            '(?<=Position: )(.*?)(?=\\n)',
            soup.find('strong', string='Position').find_parent('p').get_text()
        ).group(0)
        if position in OL_POSITIONS:
            position = 'OL'
    except:
        print(f'could not determine position for {url}')
        position = np.nan
    try:
        base_details = json.loads(
            soup.find('script', attrs={'type': 'application/ld+json'}).get_text())
    except:
        base_details = {}
    height_str = base_details.get('height', {}).get('value')
    try:
        height_ft = height_str.split('-')[0]
        height_in = height_str.split('-')[1]
        height = int(height_ft) * 12 + int(height_in)
    except:
        height = np.nan
    weight_str = base_details.get('weight', {}).get('value')
    try:
        weight = int(weight_str.split(' ')[0])
    except:
        weight = np.nan
    dob = base_details.get('birthDate', np.nan)
    try:
        pro_relatives_str = soup.find(
            'strong', string='Relatives').parent.get_text()
        pro_relatives = max(pro_relatives_str.count(';'), pro_relatives_str.count(',')) + 1
    except:
        pro_relatives = 0
    combine_comment = soup.find(text=lambda text: isinstance(text, Comment) and 'div_combine' in text)
    try:
        combine_soup = BeautifulSoup(combine_comment, features='lxml')
    except:
        combine_soup = None
    try:
        combine_table = combine_soup.find('table', attrs={'id': 'combine'}).find('tbody')
    except:
        combine_table = None
    try:
        forty = float(combine_table.find('td', attrs={'data-stat': 'forty_yd'}).get_text())
    except:
        forty = np.nan
    try:
        bench = float(combine_table.find('td', attrs={'data-stat': 'bench_reps'}).get_text())
    except:
        bench = np.nan
    try:
        broad_jump = float(combine_table.find('td', attrs={'data-stat': 'broad_jump'}).get_text())
    except:
        broad_jump = np.nan
    try:
        shuttle = float(combine_table.find('td', attrs={'data-stat': 'shuttle'}).get_text())
    except:
        shuttle = np.nan
    try:
        cone = float(combine_table.find('td', attrs={'data-stat': 'cone'}).get_text())
    except:
        cone = np.nan
    try:
        vertical = float(combine_table.find('td', attrs={'data-stat': 'vertical'}).get_text())
    except:
        vertical = np.nan
    player_entry = {
        'id': [player_id],
        'position': [position],
        'height': [height],
        'weight': [weight],
        'dob': [dob],
        'pro_relatives': [pro_relatives],
        'forty': [forty],
        'bench': [bench],
        'broad_jump': [broad_jump],
        'shuttle': [shuttle],
        'cone': [cone],
        'vertical': [vertical]
    }
    player_df = pd.concat(
        [player_df, pd.DataFrame.from_dict(player_entry)],
        ignore_index=True
    )
    return player_df


def get_player_seasons(player_id: str, soup: BeautifulSoup = None) -> pd.DataFrame:
    player_season_df = pd.DataFrame(columns=PLAYER_SEASON_COLS)
    if soup is None:
        url = f'https://www.pro-football-reference.com/players/{player_id[0].upper()}/{player_id}.htm'
        soup = get_soup(url)
    av_cell = soup.find('td', attrs={'data-stat': 'av'})
    if av_cell:
        player_season_table = av_cell.find_parent('table')
    else:
        player_season_table = None
    player_season_entries = []
    if player_season_table:
        season_num = 1
        for row in player_season_table.find_all('tr', attrs={'class': 'full_table'}):
            year_cell = row.find('th', attrs={'data-stat': 'year_id'})
            try:
                year = int(year_cell.find('a').get_text())
            except:
                continue
            team_cell = row.find('td', attrs={'data-stat': 'team'})
            try:
                team = team_cell.a['href'].split('/')[2].lower()
            except:
                team = team_cell.get_text().lower()
            try:
                age = int(row.find('td', attrs={'data-stat': 'age'}).get_text())
            except:
                age = np.nan
            av_cell = row.find('td', attrs={'data-stat': 'av'})
            try:
                av = int(av_cell.get_text())
            except:
                av = np.nan
            player_season_entries.append({
                'player': player_id,
                'year': year,
                'season_num': season_num,
                'team': team,
                'age': age,
                'av': av
            })
            season_num += 1
    player_season_df = pd.concat(
        [player_season_df, pd.DataFrame.from_records(player_season_entries)],
        ignore_index=True
    )
    return player_season_df


def get_player_games(player_id: str) -> pd.DataFrame:
    player_game_df = pd.DataFrame(columns=PLAYER_GAME_COLS)
    url = f'https://www.pro-football-reference.com/players/{player_id[0]}/{player_id}/gamelog'
    soup = get_soup(url)
    stat_table = soup.find('table', attrs={'id': 'stats'})
    player_game_entries = []
    if stat_table:
        for row in stat_table.find_all('tr', attrs={'id': re.compile('stats.[0-9]')}):  # active games
            active = True
            dnp_reason = np.nan
            try:
                year = int(row.find('td', attrs={'data-stat': 'year_id'}).get_text())
            except:
                year = np.nan
            try:
                game_date = row.find('td', attrs={'data-stat': 'game_date'}).get_text()
            except:
                game_date = np.nan
            try:
                game_num = row.find('td', attrs={'data-stat': 'game_num'}).get_text()
            except:
                game_num = np.nan
            try:
                week_num = row.find('td', attrs={'data-stat': 'week_num'}).get_text()
            except:
                week_num = np.nan
            try:
                team = row.find('td', attrs={'data-stat': 'team'}).a['href'].split('/')[2].lower()
            except:
                team = np.nan
            try:
                opp = row.find('td', attrs={'data-stat': 'opp'}).a['href'].split('/')[2].lower()
            except:
                opp = np.nan
            try:
                game_location_cell = row.find('td', attrs={'data-stat': 'game_location'})
                if game_location_cell.get_text() == '@':
                    home = False
                else:
                    home = True
            except:
                home = np.nan
            try:
                game_start_cell = row.find('td', attrs={'data-stat': 'gs'})
                if game_start_cell.get_text() == '*':
                    start = True
                else:
                    start = False
            except:
                start = np.nan
            try:
                result_text = row.find('td', attrs={'data-stat': 'game_result'}).get_text()
                win_loss = result_text.split()[0].upper()
                score_text = result_text.split()[1]
                team_score = int(score_text.split('-')[0])
                opp_score = int(score_text.split('-')[1])
            except:
                win_loss = np.nan
                score_text = np.nan
                team_score = np.nan
                opp_score = np.nan
            try:
                pass_comp = int(row.find('td', attrs={'data-stat': 'pass_cmp'}).get_text())
            except:
                pass_comp = 0
            try:
                pass_att = int(row.find('td', attrs={'data-stat': 'pass_att'}).get_text())
            except:
                pass_att = 0
            try:
                pass_yd = int(row.find('td', attrs={'data-stat': 'pass_yds'}).get_text())
            except:
                pass_yd = 0
            try:
                pass_td = int(row.find('td', attrs={'data-stat': 'pass_td'}).get_text())
            except:
                pass_td = 0
            try:
                pass_int = int(row.find('td', attrs={'data-stat': 'pass_int'}).get_text())
            except:
                pass_int = 0
            try:
                qb_rate = float(row.find('td', attrs={'data-stat': 'pass_rating'}).get_text())
            except:
                qb_rate = 0.
            try:
                rush_att = int(row.find('td', attrs={'data-stat': 'rush_att'}).get_text())
            except:
                rush_att = 0
            try:
                rush_yd = int(row.find('td', attrs={'data-stat': 'rush_yds'}).get_text())
            except:
                rush_yd = 0
            try:
                rush_td = int(row.find('td', attrs={'data-stat': 'rush_td'}).get_text())
            except:
                rush_td = 0
            try:
                rec = int(row.find('td', attrs={'data-stat': 'rec'}).get_text())
            except:
                rec = 0
            try:
                rec_tgt = int(row.find('td', attrs={'data-stat': 'targets'}).get_text())
            except:
                rec_tgt = 0
            try:
                rec_yd = int(row.find('td', attrs={'data-stat': 'rec_yds'}).get_text())
            except:
                rec_yd = 0
            try:
                rec_td = int(row.find('td', attrs={'data-stat': 'rec_td'}).get_text())
            except:
                rec_td = 0
            player_game_entries.append({
                'player': player_id,
                'year': year,
                'date': game_date,
                'game_num': game_num,
                'week_num': week_num,
                'team': team,
                'opp': opp,
                'home': home,
                'result': win_loss,
                'team_score': team_score,
                'opp_score': opp_score,
                'active': active,
                'start': start,
                'dnp_reason': dnp_reason,
                'pass_comp': pass_comp,
                'pass_att': pass_att,
                'pass_yd': pass_yd,
                'pass_td': pass_td,
                'pass_int': pass_int,
                'qb_rate': qb_rate,
                'rush_att': rush_att,
                'rush_yd': rush_yd,
                'rush_td': rush_td,
                'rec': rec,
                'rec_tgt': rec_tgt,
                'rec_yd': rec_yd,
                'rec_td': rec_td
            })
        for row in stat_table.find_all('tr', attrs={'class': 'gamelog_dnp'}):  # inactive games
            active = False
            try:
                year = int(row.find('td', attrs={'data-stat': 'year_id'}).get_text())
            except:
                year = np.nan
            try:
                game_date = row.find('td', attrs={'data-stat': 'game_date'}).get_text()
            except:
                game_date = np.nan
            try:
                game_num = row.find('td', attrs={'data-stat': 'game_num'}).get_text()
            except:
                game_num = np.nan
            try:
                week_num = row.find('td', attrs={'data-stat': 'week_num'}).get_text()
            except:
                week_num = np.nan
            try:
                team = row.find('td', attrs={'data-stat': 'team'}).a['href'].split('/')[2].lower()
            except:
                team = np.nan
            try:
                opp = row.find('td', attrs={'data-stat': 'opp'}).a['href'].split('/')[2].lower()
            except:
                opp = np.nan
            try:
                game_location_cell = row.find('td', attrs={'data-stat': 'game_location'})
                if game_location_cell.get_text() == '@':
                    home = False
                else:
                    home = True
            except:
                home = np.nan
            try:
                game_start_cell = row.find('td', attrs={'data-stat': 'gs'})
                if game_start_cell.get_text() == '*':
                    start = True
                else:
                    start = False
            except:
                start = np.nan
            try:
                result_text = row.find('td', attrs={'data-stat': 'game_result'}).get_text()
                win_loss = result_text.split()[0].upper()
                score_text = result_text.split()[1]
                team_score = int(score_text.split('-')[0])
                opp_score = int(score_text.split('-')[1])
            except:
                win_loss = np.nan
                score_text = np.nan
                team_score = np.nan
                opp_score = np.nan
            try:
                dnp_reason = row.find('td', attrs={'data-stat': 'reason'}).get_text().lower()
                dnp_reason = '_'.join(dnp_reason.split())
            except:
                dnp_reason = np.nan
            player_game_entries.append({
                'player': player_id,
                'year': year,
                'date': game_date,
                'game_num': game_num,
                'week_num': week_num,
                'team': team,
                'opp': opp,
                'home': home,
                'result': win_loss,
                'team_score': team_score,
                'opp_score': opp_score,
                'active': active,
                'start': start,
                'dnp_reason': dnp_reason,
                'pass_comp': 0,
                'pass_att': 0,
                'pass_yd': 0,
                'pass_td': 0,
                'pass_int': 0,
                'qb_rate': 0.,
                'rush_att': 0,
                'rush_yd': 0,
                'rush_td': 0,
                'rec': 0,
                'rec_tgt': 0,
                'rec_yd': 0,
                'rec_td': 0
            })
    player_game_df = pd.concat(
        [player_game_df, pd.DataFrame.from_records(player_game_entries)],
        ignore_index=True
    )
    return player_game_df


def get_transactions(player_id: str, soup: BeautifulSoup = None) -> pd.DataFrame:
    transaction_df = pd.DataFrame(columns=TRANSACTION_COLS)
    transaction_entries = []
    url = f'https://www.pro-football-reference.com/players/{player_id[0]}/{player_id}.htm'
    if soup is None:
        soup = get_soup(url)
    transaction_comment = soup.find(text=lambda text: isinstance(text, Comment) and 'div_transactions' in text and 'news_stories' in text)
    if transaction_comment:
        transaction_soup = BeautifulSoup(transaction_comment, features='lxml')
        for entry in transaction_soup.find_all('li'):
            entry_id = entry.get('id')
            if entry_id is not None and entry_id == 'transactions_toggler':
                continue
            if re.search('(?:on IR|physically unable to perform|NFI list|on IRD)', entry.get_text()):
                txn_type = 'injury_list'
            elif re.search('traded', entry.get_text()):
                txn_type = 'trade'
            else:
                continue
            date_str = entry.strong.get_text()[:-1]
            date = datetime.strptime(date_str, '%B %d, %Y').date().isoformat()
            transaction_entries.append({
                'player': player_id,
                'date': date,
                'txn_type': txn_type
            })
    transaction_df = pd.concat(
        [transaction_df, pd.DataFrame.from_records(transaction_entries)],
        ignore_index=True
    )
    return transaction_df


def get_team_seasons(team: str, start_year: int = 1995, end_year: int = 2022) -> pd.DataFrame:
    team_season_df = pd.DataFrame(columns=TEAM_SEASON_COLS)
    team_season_entries = []
    for year in range(start_year, end_year + 1):
        url = f'https://www.pro-football-reference.com/teams/{team}/{year}.htm'
        try:
            soup = get_soup(url)
        except:
            continue
        try:
            record_str = re.search(r'[0-9]{1,2}-[0-9]{1,2}-[0-9]{1,2}', soup.find('strong', string='Record:').find_parent('p').get_text()).group()
            record_str_split = record_str.split('-')
            wins = int(record_str_split[0])
            losses = int(record_str_split[1])
            ties = int(record_str_split[2])
            g = wins + losses + ties
            win_pct = float(wins / g)
        except:
            win_pct = np.nan
        try:
            ps_odds_str = soup.find('a', attrs={'href': re.compile('\/years\/[0-9]{4}\/preseason_odds.htm')}).get_text()
            ps_odds_str_split = ps_odds_str.split(';')
            sb_odds_str = ps_odds_str_split[0]
            proj_wins_str = ps_odds_str_split[1]
            proj_sb_odds = int(re.search(r'[0-9]+$', sb_odds_str).group())
            proj_wins = float(re.search(r'[0-9]{1,2}.[0-9]{1}', proj_wins_str).group())
            proj_win_pct = float(proj_wins / g)
        except:
            proj_win_pct = np.nan
            proj_sb_odds = np.nan
        team_season_entries.append({
            'team': team,
            'year': year,
            'win_pct': win_pct,
            'proj_win_pct': proj_win_pct,
            'proj_sb_odds': proj_sb_odds
        })
    team_season_df = pd.concat(
        [team_season_df, pd.DataFrame.from_records(team_season_entries)],
        ignore_index=True
    )
    return team_season_df


def get_team_games(team: str, year: int) -> pd.DataFrame:
    team_game_df = pd.DataFrame(columns=TEAM_GAME_COLS)
    url = f'https://www.pro-football-reference.com/teams/{team}/{year}/gamelog'
    soup = get_soup(url)
    opp_gamelog_table = soup.find('table', attrs={'id': re.compile('^gamelog_opp[0-9]{4}')})
    opp_top_data = {}
    for row in opp_gamelog_table.find_all('tr', attrs={'id': re.compile('^gamelog_opp[0-9]{4}.[0-9]')}):
        try:
            opp_game_date = row.find('td', attrs={'data-stat': 'game_date'})['csk']
        except:
            continue
        try:
            opp_top_str = row.find('td', attrs={'data-stat': 'time_of_poss'}).get_text().split(':')
            opp_mins = int(opp_top_str[0])
            opp_secs = int(opp_top_str[1])
            opp_top_data[opp_game_date] = opp_mins * 60 + opp_secs
        except:
            continue
    gamelog_table = soup.find('table', attrs={'id': re.compile('^gamelog[0-9]{4}')})
    team_game_entries = []
    game_num = 0
    for row in gamelog_table.find_all('tr', attrs={'id': re.compile('^gamelog[0-9]{4}.[0-9]')}):
        game_num += 1
        try:
            game_date = row.find('td', attrs={'data-stat': 'game_date'})['csk']
        except:
            game_date = np.nan
        try:
            week_num = int(row.find('th', attrs={'data-stat': 'week_num'}).get_text())
        except:
            week_num = np.nan
        try:
            opp = row.find('td', attrs={'data-stat': 'opp'}).a['href'].split('/')[2].lower()
        except:
            opp = np.nan
        try:
            game_location_cell = row.find('td', attrs={'data-stat': 'game_location'})
            if game_location_cell.get_text() == '@':
                home = False
            else:
                home = True
        except:
            home = np.nan
        try:
            result = row.find('td', attrs={'data-stat': 'game_outcome'}).get_text().upper()
        except:
            result = np.nan
        try:
            team_score = int(row.find('td', attrs={'data-stat': 'pts_off'}).get_text())
        except:
            team_score = np.nan
        try:
            opp_score = int(row.find('td', attrs={'data-stat': 'pts_def'}).get_text())
        except:
            opp_score = np.nan
        try:
            pass_comp = int(row.find('td', attrs={'data-stat': 'pass_cmp'}).get_text())
        except:
            pass_comp = 0
        try:
            pass_att = int(row.find('td', attrs={'data-stat': 'pass_att'}).get_text())
        except:
            pass_att = 0
        try:
            pass_yd = int(row.find('td', attrs={'data-stat': 'pass_yds'}).get_text())
        except:
            pass_yd = 0
        try:
            pass_td = int(row.find('td', attrs={'data-stat': 'pass_td'}).get_text())
        except:
            pass_td = 0
        try:
            pass_int = int(row.find('td', attrs={'data-stat': 'pass_int'}).get_text())
        except:
            pass_int = 0
        try:
            qb_rate = float(row.find('td', attrs={'data-stat': 'pass_rating'}).get_text())
        except:
            qb_rate = 0.
        try:
            sack = int(row.find('td', attrs={'data-stat': 'pass_sacked'}).get_text())
        except:
            sack = 0
        try:
            rush_att = int(row.find('td', attrs={'data-stat': 'rush_att'}).get_text())
        except:
            rush_att = 0
        try:
            rush_yd = int(row.find('td', attrs={'data-stat': 'rush_yds'}).get_text())
        except:
            rush_yd = 0
        try:
            rush_td = int(row.find('td', attrs={'data-stat': 'rush_td'}).get_text())
        except:
            rush_td = 0
        try:
            third_down_att = int(row.find('td', attrs={'data-stat': 'third_down_att'}).get_text())
        except:
            third_down_att = np.nan
        try:
            third_down_conv = int(row.find('td', attrs={'data-stat': 'third_down_success'}).get_text())
        except:
            third_down_conv = np.nan
        try:
            fourth_down_att = int(row.find('td', attrs={'data-stat': 'fourth_down_att'}).get_text())
        except:
            fourth_down_att = np.nan
        try:
            fourth_down_conv = int(row.find('td', attrs={'data-stat': 'fourth_down_success'}).get_text())
        except:
            fourth_down_conv = np.nan
        try:
            team_top_str = row.find('td', attrs={'data-stat': 'time_of_poss'}).get_text().split(':')
            mins = int(team_top_str[0])
            secs = int(team_top_str[1])
            team_top = mins * 60 + secs
        except:
            team_top = np.nan
        try:
            opp_top = opp_top_data[game_date]
        except:
            opp_top = np.nan
        team_game_entries.append({
            'team': team,
            'year': year,
            'date': game_date,
            'game_num': game_num,
            'week_num': week_num,
            'opp': opp,
            'home': home,
            'result': result,
            'team_score': team_score,
            'opp_score': opp_score,
            'pass_comp': pass_comp,
            'pass_att': pass_att,
            'pass_yd': pass_yd,
            'pass_td': pass_td,
            'pass_int': pass_int,
            'qb_rate': qb_rate,
            'sack': sack,
            'rush_att': rush_att,
            'rush_yd': rush_yd,
            'rush_td': rush_td,
            'team_top': team_top,
            'opp_top': opp_top,
            'fourth_down_att': fourth_down_att,
            'fourth_down_conv': fourth_down_conv,
            'third_down_att': third_down_att,
            'third_down_conv': third_down_conv
        })
    team_game_df = pd.concat(
        [team_game_df, pd.DataFrame.from_records(team_game_entries)],
        ignore_index=True
    )
    return team_game_df


def get_team_coaches(team, start_year: int = 1982) -> pd.DataFrame:
    team_coach_df = pd.DataFrame(columns=TEAM_COACH_COLS)
    url = f'https://www.pro-football-reference.com/teams/{team}/coaches.htm'
    soup = get_soup(url)
    coach_table = soup.find('table', attrs={'id': 'coaches_year'}).find('tbody')
    team_coach_entries = []
    for row in coach_table.find_all('tr'):
        try:
            year = int(row.find('th', attrs={'data-stat': 'year_id'}).get_text())
        except:
            year = None
        if year and year < start_year:
            break
        try:
            coach = row.find('td', attrs={'data-stat': 'coach'}).a['href'].split('/')[2].split('.')[0]
        except:
            coach = np.nan
        games = int(row.find('td', attrs={'data-stat': 'g'}).get_text())
        if year:
            year_games = get_season_games(year, team=team)
            start_game_num = year_games - games + 1
        else:
            prev_row = row.find_previous('tr')
            year = int(prev_row.find('th', attrs={'data-stat': 'year_id'}).get_text())
            start_game_num = 1
        end_game_num = start_game_num + games - 1
        team_coach_entries.append({
            'team': team,
            'year': year,
            'coach': coach,
            'role': 'hc',
            'start_game_num': start_game_num,
            'end_game_num': end_game_num
        })
        try:
            oc = row.find('td', attrs={'data-stat': 'oc'}).a['href'].split('/')[2].split('.')[0]
        except:
            oc = None
        if oc:
            team_coach_entries.append({
                'team': team,
                'year': year,
                'coach': oc,
                'role': 'oc',
                'start_game_num': start_game_num,
                'end_game_num': end_game_num
            })
        try:
            dc = row.find('td', attrs={'data-stat': 'dc'}).a['href'].split('/')[2].split('.')[0]
        except:
            dc = None
        if dc:
            team_coach_entries.append({
                'team': team,
                'year': year,
                'coach': dc,
                'role': 'dc',
                'start_game_num': start_game_num,
                'end_game_num': end_game_num
            })
    team_coach_df = pd.concat(
        [team_coach_df, pd.DataFrame.from_records(team_coach_entries)],
        ignore_index=True
    )
    return team_coach_df


def get_team_roster(team: str,
                    year: int,
                    player_df: pd.DataFrame = None,
                    player_game_df: pd.DataFrame = None,
                    player_season_df: pd.DataFrame = None,
                    transaction_df: pd.DataFrame = None) -> tuple:
    if player_df is None:
        player_df = pd.DataFrame(columns=PLAYER_COLS)
    if player_game_df is None:
        player_game_df = pd.DataFrame(columns=PLAYER_GAME_COLS)
    if player_season_df is None:
        player_season_df = pd.DataFrame(columns=PLAYER_SEASON_COLS)
    if transaction_df is None:
        transaction_df = pd.DataFrame(columns=TRANSACTION_COLS)
    team_roster_df = pd.DataFrame(columns=TEAM_ROSTER_COLS)
    url = f'https://www.pro-football-reference.com/teams/{team}/{year}_roster.htm'
    soup = get_soup(url)
    starters = []
    starter_table = soup.find('table', attrs={'id': 'starters'})
    if starter_table:
        for row in starter_table.find('tbody').find_all('tr', attrs={'class': 'full_table'}):
            try:
                starters.append(row.find('td', attrs={'data-stat': 'player'})['data-append-csv'])
            except:
                continue
    comment = soup.find(text=lambda text: isinstance(text, Comment) and 'div_roster' in text)
    if not comment:
        raise ValueError(f'could not scrape team roster | team = {team} | year = {year}')
    comment_soup = BeautifulSoup(comment, features='lxml')
    roster_table = comment_soup.find('table', attrs={'id': 'roster'}).find('tbody')
    roster_entries = []
    for row in roster_table.find_all('tr'):
        try:
            player_id = row.find('td', attrs={'data-stat': 'player'}).a['href'].split('/')[-1].split('.htm')[0]
        except:
            continue
        try:
            position = row.find('td', attrs={'data-stat': 'pos'}).get_text().upper()
            if position in OL_POSITIONS:
                position = 'OL'
        except:
            continue
        if position in OFFENSIVE_POSITIONS:
            player = player_df.loc[player_df.id == player_id]
            if player.empty:  # scrape all player data
                (player, player_seasons, player_transactions) = get_player_full(player_id)
                player_games = get_player_games(player_id)
                player_df = pd.concat(
                    [player_df, player],
                    ignore_index=True
                )
                player_season_df = pd.concat(
                    [player_season_df, player_seasons],
                    ignore_index=True
                )
                transaction_df = pd.concat(
                    [transaction_df, player_transactions],
                    ignore_index=True
                )
                player_game_df = pd.concat(
                    [player_game_df, player_games],
                    ignore_index=True
                )
            else:
                print(f'already scraped {player_id}, skipping...')
                player_games = player_game_df.loc[player_game_df.player == player_id]
            player_roster_games = player_games.loc[(player_games.year == year) & (player_games.team == team)]
            if player_roster_games.week_num.min() == '1' or player_roster_games.empty:  # include this player on the team roster
                if starters:
                    is_starter = True if player_id in starters else False
                else:
                    is_starter = np.nan
                roster_entries.append({
                    'team': team,
                    'year': year,
                    'player': player_id,
                    'position': position,
                    'is_starter': is_starter
                })
    team_roster_df = pd.concat(
        [team_roster_df, pd.DataFrame.from_records(roster_entries)],
        ignore_index=True
    )
    return team_roster_df, player_df, player_season_df, player_game_df, transaction_df


def get_draft_picks(start_year: int = 1982, end_year: int = 2022) -> pd.DataFrame:
    draft_pick_df = pd.DataFrame(columns=DRAFT_PICK_COLS)
    draft_pick_entries = []
    for year in range(start_year, end_year + 1):
        url = f'https://www.pro-football-reference.com/years/{year}/draft.htm'
        soup = get_soup(url)
        draft_table = soup.find('table', attrs={'id': 'drafts'}).find('tbody')
        for row in draft_table.find_all('tr'):
            row_class = row.get('class')
            if row_class and 'thead' in row_class:
                # print('skipping header row...')
                continue
            player_cell = row.find('td', attrs={'data-stat': 'player'})
            if not player_cell:
                continue
            player_link = player_cell.find('a')
            if player_link:
                try:
                    player = player_link['href'].split('/')[-1].split('.htm')[0]
                except:
                    raise ValueError('could not parse player URL')
            else:
                player = player_cell.get_text().replace(' ', '')
            try:
                rnd = int(row.find('th', attrs={'data-stat': 'draft_round'}).get_text())
            except:
                rnd = np.nan
            try:
                pick = int(row.find('td', attrs={'data-stat': 'draft_pick'}).get_text())
            except:
                pick = np.nan
            try:
                age = int(row.find('td', attrs={'data-stat': 'age'}).get_text())
            except:
                age = np.nan
            try:
                team = row.find('td', attrs={'data-stat': 'team'}).a['href'].split('/')[2].lower()
            except:
                team = np.nan
            try:
                position = row.find('td', attrs={'data-stat': 'pos'}).get_text().upper()
                if position in OL_POSITIONS:
                    position = 'OL'
            except:
                position = np.nan
            draft_pick_entries.append({
                'year': year,
                'round': rnd,
                'pick': pick,
                'player': player,
                'team': team,
                'age': age,
                'position': position
            })
    draft_pick_df = pd.concat(
        [draft_pick_df, pd.DataFrame.from_records(draft_pick_entries)],
        ignore_index=True
    )
    return draft_pick_df


def get_awards(start_year: int = 1982, end_year: int = 2022) -> pd.DataFrame:
    award_df = pd.DataFrame(columns=AWARD_COLS)
    award_entries = []
    for year in range(start_year, end_year + 1):
        url = f'https://www.pro-football-reference.com/awards/awards_{year}.htm'
        soup = get_soup(url)

        # MVP
        mvp_table = soup.find('table', attrs={'id': 'voting_apmvp'}).find('tbody')
        for row in mvp_table.find_all('tr'):
            award_type = 'mvp'
            row_class = row.get('class')
            if row_class and 'bold' in row_class:
                win = True
            else:
                win = False
            try:
                player = row.find('td', attrs={'data-stat': 'player'}).a['href'].split('/')[-1].split('.htm')[0]
            except:
                continue
            try:
                vote_share = float(row.find('td', attrs={'data-stat': 'share'}).get_text()[:-1]) / 100.
            except:
                vote_share = np.nan
            award_entries.append({
                'year': year,
                'player': player,
                'award_type': award_type,
                'win': win,
                'vote_share': vote_share
            })

        # OPOY
        opoy_table = soup.find('table', attrs={'id': 'voting_apopoy'}).find('tbody')
        for row in opoy_table.find_all('tr'):
            award_type = 'opoy'
            row_class = row.get('class')
            if row_class and 'bold' in row_class:
                win = True
            else:
                win = False
            try:
                player = row.find('td', attrs={'data-stat': 'player'}).a['href'].split('/')[-1].split('.htm')[0]
            except:
                continue
            try:
                vote_share = float(row.find('td', attrs={'data-stat': 'share'}).get_text()[:-1]) / 100.
            except:
                vote_share = np.nan
            award_entries.append({
                'year': year,
                'player': player,
                'award_type': award_type,
                'win': win,
                'vote_share': vote_share
            })

        # OROY
        oroy_table = soup.find('table', attrs={'id': 'voting_aporoy'}).find('tbody')
        for row in oroy_table.find_all('tr'):
            award_type = 'oroy'
            row_class = row.get('class')
            if row_class and 'bold' in row_class:
                win = True
            else:
                win = False
            try:
                player = row.find('td', attrs={'data-stat': 'player'}).a['href'].split('/')[-1].split('.htm')[0]
            except:
                continue
            try:
                vote_share = float(row.find('td', attrs={'data-stat': 'share'}).get_text()[:-1]) / 100.
            except:
                vote_share = np.nan
            award_entries.append({
                'year': year,
                'player': player,
                'award_type': award_type,
                'win': win,
                'vote_share': vote_share
            })

        # CPOY
        try:
            cpoy_table = soup.find('table', attrs={'id': 'voting_apcpoy'}).find('tbody')
        except:
            cpoy_table = None
        if cpoy_table:
            for row in cpoy_table.find_all('tr'):
                award_type = 'cpoy'
                row_class = row.get('class')
                if row_class and 'bold' in row_class:
                    win = True
                else:
                    win = False
                try:
                    player = row.find('td', attrs={'data-stat': 'player'}).a['href'].split('/')[-1].split('.htm')[0]
                except:
                    continue
                try:
                    vote_share = float(row.find('td', attrs={'data-stat': 'share'}).get_text()[:-1]) / 100.
                except:
                    vote_share = np.nan
                award_entries.append({
                    'year': year,
                    'player': player,
                    'award_type': award_type,
                    'win': win,
                    'vote_share': vote_share
                })
    award_df = pd.concat(
        [award_df, pd.DataFrame.from_records(award_entries)],
        ignore_index=True
    )
    return award_df


def get_all_pros(start_year: int = 1982, end_year: int = 2022) -> pd.DataFrame:
    all_pro_df = pd.DataFrame(columns=ALL_PRO_COLS)
    all_pro_entries = []
    for year in range(start_year, end_year + 1):
        url = f'https://www.pro-football-reference.com/years/{year}/allpro.htm'
        soup = get_soup(url)
        all_pro_table = soup.find('table', attrs={'id': 'all_pro'}).find('tbody')
        for row in all_pro_table.find_all('tr'):
            row_class = row.get('class')
            if row_class and 'thead' in row_class:
                # print('skipping header row...')
                continue
            player_cell = row.find('td', attrs={'data-stat': 'player'})
            if player_cell.get('data-append-csv') is not None:
                player = player_cell.get('data-append-csv')
            else:
                player_link = player_cell.find('a')
                if player_link:
                    try:
                        player = player_link['href'].split('/')[-1].split('.htm')[0]
                    except:
                        raise ValueError('could not parse player URL')
                else:
                    raise ValueError('could not identify player')
            all_pro_entries.append({
                'year': year,
                'player': player
            })
    all_pro_df = pd.concat(
        [all_pro_df, pd.DataFrame.from_records(all_pro_entries)],
        ignore_index=True
    )
    return all_pro_df


def get_pro_bowls(start_year: int = 1982, end_year: int = 2022) -> pd.DataFrame:
    pro_bowl_df = pd.DataFrame(columns=PRO_BOWL_COLS)
    pro_bowl_entries = []
    for year in range(start_year, end_year + 1):
        url = f'https://www.pro-football-reference.com/years/{year}/probowl.htm'
        soup = get_soup(url)
        pro_bowl_table = soup.find('table', attrs={'id': 'pro_bowl'}).find('tbody')
        for row in pro_bowl_table.find_all('tr'):
            player_cell = row.find('td', attrs={'data-stat': 'player'})
            if player_cell.get('data-append-csv') is not None:
                player = player_cell.get('data-append-csv')
            else:
                player_link = player_cell.find('a')
                if player_link:
                    try:
                        player = player_link['href'].split('/')[-1].split('.htm')[0]
                    except:
                        raise ValueError('could not parse player URL')
                else:
                    raise ValueError('could not identify player')
            pro_bowl_entries.append({
                'year': year,
                'player': player
            })
    pro_bowl_df = pd.concat(
        [pro_bowl_df, pd.DataFrame.from_records(pro_bowl_entries)],
        ignore_index=True
    )
    return pro_bowl_df


def scrape_data(start: int = 2021, end: int = 2021, player_count: int = SCRAPE_PLAYER_COUNT) -> dict:

    players = pd.DataFrame(columns=['id', 'position', 'height', 'weight', 'dob',
                                    'draft_year', 'draft_team', 'draft_round', 'draft_pick', 'num_relatives'])
    seasons = pd.DataFrame(columns=['player', 'year', 'team', 'age', 'g', 'gs', 'qb_win', 'qb_loss', 'qb_draw', 'qb_rate', 'qb_fqc', 'qb_gwd', 'pass_comp', 'pass_att', 'pass_yd', 'pass_td',
                                    'pass_int', 'pass_1d', 'pass_long', 'rush_att', 'rush_yd', 'rush_td', 'rush_1d', 'rush_long', 'rec', 'rec_tgt', 'rec_yd', 'rec_td', 'rec_1d', 'rec_long', 'pfr_av', 'awards'])
    games = pd.DataFrame(columns=['player', 'year', 'date', 'game_num', 'week_num', 'team', 'opp', 'home', 'result', 'start', 'qb_rate',
                                  'pass_comp', 'pass_att', 'pass_yd', 'pass_td', 'pass_int', 'rush_att', 'rush_yd', 'rush_td', 'rec', 'rec_tgt', 'rec_yd', 'rec_td'])
    player_ids = get_player_universe(start, end)
    for player_id in player_ids[:player_count]:
        player_df, season_df = scrape_player(player_id)
        game_df = scrape_player_gamelogs(player_id)
        players = pd.concat([players, player_df], ignore_index=True)
        seasons = pd.concat([seasons, season_df], ignore_index=True)
        games = pd.concat([games, game_df], ignore_index=True)
    return {
        'players': players,
        'seasons': seasons,
        'games': games
    }


def get_player_universe(start: int, end: int, n: int = SCRAPE_PLAYER_COUNT):
    player_ids = []
    for year in range(start, end + 1):
        url = f'https://www.pro-football-reference.com/years/{year}/fantasy.htm'
        # sleep to ensure we don't violate PFF rate limiting guidelines
        time.sleep(3)
        print(f'scraping {url}\n')
        html = urlopen(url)
        soup = BeautifulSoup(html, features="lxml")
        year_player_ids = [td.a['href'].split(
            '/')[3].split('.htm')[0] for td in soup.find_all('td', attrs={'data-stat': 'player'})][:n]
        # only add net new players each year
        player_ids.extend(
            [player_id for player_id in year_player_ids if player_id not in player_ids])
    return player_ids


def scrape_player_gamelogs(player_id: str):
    game_df = pd.DataFrame(columns=['player', 'year', 'date', 'game_num', 'week_num', 'team', 'opp', 'home', 'result', 'start', 'qb_rate',
                                    'pass_comp', 'pass_att', 'pass_yd', 'pass_td', 'pass_int', 'rush_att', 'rush_yd', 'rush_td', 'rec', 'rec_tgt', 'rec_yd', 'rec_td'])
    url = f'https://www.pro-football-reference.com/players/{player_id[0]}/{player_id}/gamelog'
    print(f'scraping {url}\n')
    try:
        html = urlopen(url)
        soup = BeautifulSoup(html, features="lxml")
    except Exception as e:
        print(f'encountered exception: {e}')
        time.sleep(1)
        html = urlopen(url)
        soup = BeautifulSoup(html, features="lxml")
    stat_table = soup.find('table', attrs={'id': 'stats'})
    game_entries = []
    for row in stat_table.find_all('tr', attrs={'id': re.compile('stats.[0-9]')}):
        try:
            year = row.find_next(
                'td', attrs={'data-stat': 'year_id'}).get_text()
        except:
            year = None
        try:
            date = row.find_next(
                'td', attrs={'data-stat': 'game_date'}).get_text()
        except:
            date = None
        try:
            game_num = row.find_next(
                'td', attrs={'data-stat': 'game_num'}).get_text()
        except:
            game_num = None
        try:
            week_num = row.find_next(
                'td', attrs={'data-stat': 'week_num'}).get_text()
        except:
            week_num = None
        try:
            team = row.find_next(
                'td', attrs={'data-stat': 'team'}).a['href'].split('/')[2]
        except:
            team = None
        try:
            opp = row.find_next(
                'td', attrs={'data-stat': 'opp'}).a['href'].split('/')[2]
        except:
            opp = None
        try:
            at = row.find_next(
                'td', attrs={'data-stat': 'game_location'}).get_text()
            if at:
                home = False
            else:
                home = True
        except:
            home = None
        try:
            gs = row.find_next('td', attrs={'data-stat': 'gs'}).get_text()
            if gs:
                start = True
            else:
                start = False
        except:
            start = None
        try:
            result = row.find_next(
                'td', attrs={'data-stat': 'game_result'}).get_text()[0].upper()
        except:
            result = None
        try:
            pass_comp = row.find_next(
                'td', attrs={'data-stat': 'pass_cmp'}).get_text()
        except:
            pass_comp = 0
        try:
            pass_att = row.find_next(
                'td', attrs={'data-stat': 'pass_att'}).get_text()
        except:
            pass_att = 0
        try:
            pass_yd = row.find_next(
                'td', attrs={'data-stat': 'pass_yds'}).get_text()
        except:
            pass_yd = 0
        try:
            pass_td = row.find_next(
                'td', attrs={'data-stat': 'pass_td'}).get_text()
        except:
            pass_td = 0
        try:
            pass_int = row.find_next(
                'td', attrs={'data-stat': 'pass_int'}).get_text()
        except:
            pass_int = 0
        try:
            qb_rate = row.find_next(
                'td', attrs={'data-stat': 'pass_rating'}).get_text()
        except:
            qb_rate = 0
        try:
            rush_att = row.find_next(
                'td', attrs={'data-stat': 'rush_att'}).get_text()
        except:
            rush_att = 0
        try:
            rush_yd = row.find_next(
                'td', attrs={'data-stat': 'rush_yds'}).get_text()
        except:
            rush_yd = 0
        try:
            rush_td = row.find_next(
                'td', attrs={'data-stat': 'rush_td'}).get_text()
        except:
            rush_td = 0
        try:
            rec_tgt = row.find_next(
                'td', attrs={'data-stat': 'targets'}).get_text()
        except:
            rec_tgt = 0
        try:
            rec = row.find_next('td', attrs={'data-stat': 'rec'}).get_text()
        except:
            rec = 0
        try:
            rec_yd = row.find_next(
                'td', attrs={'data-stat': 'rec_yds'}).get_text()
        except:
            rec_yd = 0
        try:
            rec_td = row.find_next(
                'td', attrs={'data-stat': 'rec_td'}).get_text()
        except:
            rec_td = 0
        game_entry = {
            'player': player_id,
            'year': year,
            'date': date,
            'game_num': game_num,
            'week_num': week_num,
            'team': team,
            'opp': opp,
            'home': home,
            'result': result,
            'start': start,
            'pass_comp': pass_comp,
            'pass_att': pass_att,
            'pass_yd': pass_yd,
            'pass_td': pass_td,
            'pass_int': pass_int,
            'qb_rate': qb_rate,
            'rush_att': rush_att,
            'rush_yd': rush_yd,
            'rush_td': rush_td,
            'rec_tgt': rec_tgt,
            'rec': rec,
            'rec_yd': rec_yd,
            'rec_td': rec_td
        }
        game_entries.append(game_entry)
    game_df = pd.concat(
        [game_df, pd.DataFrame.from_records(game_entries)], ignore_index=True)
    return game_df


def scrape_player(player_id: str):
    player_df = pd.DataFrame(columns=['id', 'position', 'height', 'weight', 'dob',
                                      'draft_year', 'draft_team', 'draft_round', 'draft_pick', 'num_relatives'])
    season_df = pd.DataFrame(columns=['player', 'year', 'team', 'age', 'g', 'gs', 'qb_win', 'qb_loss', 'qb_draw', 'qb_rate', 'qb_fqc', 'qb_gwd', 'pass_comp', 'pass_att', 'pass_yd', 'pass_td',
                                      'pass_int', 'pass_1d', 'pass_long', 'rush_att', 'rush_yd', 'rush_td', 'rush_1d', 'rush_long', 'rec', 'rec_tgt', 'rec_yd', 'rec_td', 'rec_1d', 'rec_long', 'pfr_av', 'awards'])
    url = f'https://www.pro-football-reference.com/players/{player_id[0]}/{player_id}.htm'
    time.sleep(2)
    print(f'scraping {url}\n')
    try:
        html = urlopen(url)
        soup = BeautifulSoup(html, features="lxml")
    except:
        time.sleep(10)
        html = urlopen(url)
        soup = BeautifulSoup(html, features="lxml")
    try:
        position = re.search('(?:QB|WR|TE|RB)', soup.find(
            'strong', string='Position').parent.get_text()).group(0)
    except:
        position = np.nan
    try:
        base_details = json.loads(
            soup.find('script', attrs={'type': 'application/ld+json'}).get_text())
    except:
        base_details = {}
    height_str = base_details.get('height', {}).get('value')
    try:
        height_ft = height_str.split('-')[0]
        height_in = height_str.split('-')[1]
        height = int(height_ft) * 12 + int(height_in)
    except:
        height = np.nan
    weight_str = base_details.get('weight', {}).get('value')
    try:
        weight = int(weight_str.split(' ')[0])
    except:
        weight = np.nan
    dob = base_details.get('birthDate', np.nan)
    try:
        draft = soup.find(
            'strong', string='Draft').parent.get_text().split(': ')[1]
    except:
        draft = ''
    try:
        draft_round = int(
            re.search('[0-9]{1,3}(?:st|nd|rd|th)', draft).group(0)[0])
    except:
        draft_round = np.nan
    try:
        draft_pick = int(
            re.search('[0-9]{1,3}', draft[draft.find('(')+1:draft.find(')')]).group(0))
    except:
        draft_pick = np.nan
    try:
        draft_team = soup.find(
            'strong', string='Draft').parent.a['href'].split('/')[2]
    except:
        draft_team = np.nan
    try:
        draft_year = int(re.search(
            '[0-9]{4}', soup.find('strong', string='Draft').parent.a['href'].split('/')[3]).group(0))
    except:
        draft_year = np.nan
    try:
        relatives_str = soup.find(
            'strong', string='Relatives').parent.get_text()
        relatives = max(relatives_str.count(';'), relatives_str.count(',')) + 1
    except:
        relatives = 0
    player_entry = {
        'id': [player_id],
        'position': [position],
        'height': [height],
        'weight': [weight],
        'dob': [dob],
        'draft_round': [draft_round],
        'draft_pick': [draft_pick],
        'draft_team': [draft_team],
        'draft_year': [draft_year],
        'num_relatives': [relatives]
    }
    player_df = pd.concat(
        [player_df, pd.DataFrame.from_dict(player_entry)], ignore_index=True)

    season_entries = []
    passing = soup.find('table', id='passing')
    if passing:
        for row in passing.find_all('th', attrs={'data-stat': 'year_id', 'csk': re.compile('^[0-9]{4}')}):
            year = row.get_text()
            if not year:
                continue
            year = year[:4]
            age = row.find_next('td', attrs={'data-stat': 'age'}).get_text()
            team_cell = row.find_next('td', attrs={'data-stat': 'team'})
            try:
                team = team_cell.a['href'].split('/')[2]
            except:
                team = team_cell.get_text()
            g = int(row.find_next('td', attrs={'data-stat': 'g'}).get_text())
            gs = int(row.find_next('td', attrs={'data-stat': 'gs'}).get_text())
            awards_cell = row.find_next('td', attrs={'data-stat': 'awards'})
            awards = None
            if awards_cell is not None:
                try:
                    awards = len(
                        [a for a in awards_cell.get_text().split(', ') if a])
                except:
                    awards = 0
            av_cell = row.find_next('td', attrs={'data-stat': 'av'})
            av = None
            if av_cell is not None:
                try:
                    av = int(av_cell.get_text())
                except:
                    av = 0
            if year not in [entry.get('year') for entry in season_entries]:
                season_entries.append(
                    {
                        'player': player_id,
                        'year': year,
                        'age': age,
                        'team': team,
                        'g': g,
                        'gs': gs
                    }
                )
            season_entry = next(
                entry for entry in season_entries if entry.get('year') == year)
            try:
                record_str = row.find_next(
                    'td', attrs={'data-stat': 'qb_rec'}).get_text()
                record = record_str.split('-') if record_str else []
                qb_win = record[0]
                qb_loss = record[1]
                qb_draw = record[2]
            except:
                qb_win = 0
                qb_loss = 0
                qb_draw = 0
            try:
                qb_rate = float(row.find_next(
                    'td', attrs={'data-stat': 'pass_rating'}).get_text())
            except:
                qb_rate = 0
            try:
                qb_4qc = int(row.find_next(
                    'td', attrs={'data-stat': 'comebacks'}).get_text())
            except:
                qb_4qc = 0
            try:
                qb_gwd = int(row.find_next(
                    'td', attrs={'data-stat': 'gwd'}).get_text())
            except:
                qb_gwd = 0
            try:
                pass_comp = int(row.find_next(
                    'td', attrs={'data-stat': 'pass_cmp'}).get_text())
            except:
                pass_comp = 0
            try:
                pass_att = int(row.find_next(
                    'td', attrs={'data-stat': 'pass_att'}).get_text())
            except:
                pass_att = 0
            try:
                pass_yd = int(row.find_next(
                    'td', attrs={'data-stat': 'pass_yds'}).get_text())
            except:
                pass_yd = 0
            try:
                pass_td = int(row.find_next(
                    'td', attrs={'data-stat': 'pass_td'}).get_text())
            except:
                pass_td = 0
            try:
                pass_int = int(row.find_next(
                    'td', attrs={'data-stat': 'pass_int'}).get_text())
            except:
                pass_int = 0
            try:
                pass_1d = int(row.find_next(
                    'td', attrs={'data-stat': 'pass_first_down'}).get_text())
            except:
                pass_1d = 0
            try:
                pass_long = int(row.find_next(
                    'td', attrs={'data-stat': 'pass_long'}).get_text())
            except:
                pass_long = 0
            row_stats = {
                'qb_win': qb_win,
                'qb_loss': qb_loss,
                'qb_draw': qb_draw,
                'qb_rate': qb_rate,
                'qb_fqc': qb_4qc,
                'qb_gwd': qb_gwd,
                'pass_comp': pass_comp,
                'pass_att': pass_att,
                'pass_yd': pass_yd,
                'pass_td': pass_td,
                'pass_int': pass_int,
                'pass_1d': pass_1d,
                'pass_long': pass_long
            }
            if awards is not None:
                row_stats['awards'] = awards
            if av is not None:
                row_stats['pfr_av'] = av
            season_entry.update(row_stats)
    rush_rec = soup.find('table', id='rushing_and_receiving')
    if not rush_rec:
        rush_rec = soup.find('table', id='receiving_and_rushing')
    if rush_rec:
        for row in rush_rec.find_all('th', attrs={'data-stat': 'year_id', 'csk': re.compile('^[0-9]{4}')}):
            year = row.get_text()
            if not year:
                continue
            year = year[:4]
            age = row.find_next('td', attrs={'data-stat': 'age'}).get_text()
            team_cell = row.find_next('td', attrs={'data-stat': 'team'})
            try:
                team = team_cell.a['href'].split('/')[2]
            except:
                team = team_cell.get_text()
            g = int(row.find_next('td', attrs={'data-stat': 'g'}).get_text())
            gs = int(row.find_next('td', attrs={'data-stat': 'gs'}).get_text())
            awards_cell = row.find_next('td', attrs={'data-stat': 'awards'})
            awards = None
            if awards_cell is not None:
                try:
                    awards = len(
                        [a for a in awards_cell.get_text().split(', ') if a])
                except:
                    awards = 0
            av_cell = row.find_next('td', attrs={'data-stat': 'av'})
            av = None
            if av_cell is not None:
                try:
                    av = int(av_cell.get_text())
                except:
                    av = 0
            if year not in [entry.get('year') for entry in season_entries]:
                season_entries.append(
                    {
                        'player': player_id,
                        'year': year,
                        'age': age,
                        'team': team,
                        'g': g,
                        'gs': gs
                    }
                )
            season_entry = next(
                entry for entry in season_entries if entry.get('year') == year)
            try:
                rush_att = int(row.find_next(
                    'td', attrs={'data-stat': 'rush_att'}).get_text())
            except:
                rush_att = 0
            try:
                rush_yd = int(row.find_next(
                    'td', attrs={'data-stat': 'rush_yds'}).get_text())
            except:
                rush_yd = 0
            try:
                rush_td = int(row.find_next(
                    'td', attrs={'data-stat': 'rush_td'}).get_text())
            except:
                rush_td = 0
            try:
                rush_1d = int(row.find_next(
                    'td', attrs={'data-stat': 'rush_first_down'}).get_text())
            except:
                rush_1d = 0
            try:
                rush_long = int(row.find_next(
                    'td', attrs={'data-stat': 'rush_long'}).get_text())
            except:
                rush_long = 0
            try:
                rec = int(row.find_next(
                    'td', attrs={'data-stat': 'rec'}).get_text())
            except:
                rec = 0
            try:
                rec_tgt = int(row.find_next(
                    'td', attrs={'data-stat': 'targets'}).get_text())
            except:
                rec_tgt = 0
            try:
                rec_yd = int(row.find_next(
                    'td', attrs={'data-stat': 'rec_yds'}).get_text())
            except:
                rec_yd = 0
            try:
                rec_td = int(row.find_next(
                    'td', attrs={'data-stat': 'rec_td'}).get_text())
            except:
                rec_td = 0
            try:
                rec_1d = int(row.find_next(
                    'td', attrs={'data-stat': 'rec_first_down'}).get_text())
            except:
                rec_1d = 0
            try:
                rec_long = int(row.find_next(
                    'td', attrs={'data-stat': 'rec_long'}).get_text())
            except:
                rec_long = 0
            row_stats = {
                'rush_att': rush_att,
                'rush_yd': rush_yd,
                'rush_td': rush_td,
                'rush_1d': rush_1d,
                'rush_long': rush_long,
                'rec': rec,
                'rec_tgt': rec_tgt,
                'rec_yd': rec_yd,
                'rec_td': rec_td,
                'rec_1d': rec_1d,
                'rec_long': rec_long
            }
            if awards is not None:
                row_stats['awards'] = awards
            if av is not None:
                row_stats['pfr_av'] = av
            season_entry.update(row_stats)
    season_df = pd.concat(
        [season_df, pd.DataFrame.from_records(season_entries)], ignore_index=True)
    return player_df, season_df


def move_column_inplace(df, col, pos):
    col = df.pop(col)
    df.insert(pos, col.name, col)


def build_game_id(row):
    date_str = str(row.date).replace('-', '')
    if row.home:
        home_tm = row.team
        away_tm = row.opp
    else:
        home_tm = row.opp
        away_tm = row.team
    return f'{date_str}{row.player}{away_tm}{home_tm}'


def calc_fantasy_points(row):
    return row.rec*1.0 + row.pass_yd*0.04 + sum([row.rush_yd, row.rec_yd])*0.1 + sum([row.pass_td, row.rush_td, row.rec_td])*6


def get_soup(url: str, sleep: float or int = 3):
    time.sleep(sleep)
    try:
        print(f'scraping {url}')
        html = urlopen(url)
        soup = BeautifulSoup(html, features="lxml")
    except:  # pause and retry the request
        time.sleep(sleep)
        html = urlopen(url)
        soup = BeautifulSoup(html, features="lxml")
    return soup


def get_season_games(year: int, team: str = None):
    games = 16 if year < 2021 else 17
    if year == 2022 and team in ('buf', 'cin'):
        games = 16
    return games
