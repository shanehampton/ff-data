import json
import re
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen

from constants import SCRAPE_PLAYER_COUNT


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
