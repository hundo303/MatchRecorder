import glob
import os
from bs4 import BeautifulSoup
import re


def exists_next_page(html_dir):
    index_number = int(html_dir[-12:-5])
    index_number += 1

    html_dir = html_dir[:-12] + str(index_number) + html_dir[-5:]

    return os.path.exists(html_dir)


#  1球ごとの投球内容のリストを内包した、1打席の投球内容のリストを返す
#  1球ごとの投球内容は[打席での球数, 試合での球数, 球種, 球速, 結果]
def take_pitch_list(soup):
    one_pitch_list = []

    tr_list = soup.select('#pitchesDetail > section:nth-child(2) > table:nth-child(3) > tbody > tr')
    for tr in tr_list:
        td_list = tr.select('td')
        pitch_number_in_at_bat = td_list[0].span.get_text()
        pitch_number_in_game = td_list[1].get_text()
        type_of_pitch = td_list[2].get_text()
        pitch_speed = td_list[3].get_text()
        pitch_result = re.sub(r'\s', '', td_list[4].get_text())

        one_pitch_list.append([pitch_number_in_at_bat,
                               pitch_number_in_game,
                               type_of_pitch,
                               pitch_speed,
                               pitch_result])

    return one_pitch_list


def take_date(soup):
    date_text = soup.select_one('#gm_menu > section > header > h1 > a').get_text()
    date_split = date_text.split('（')
    date = date_split[0]
    day_week = date_split[1].replace('）', '')

    return [date, day_week]


def take_match_player_data(soup):
    div_pitcher = soup.select_one('#pitcherL > div.card')
    div_batter = soup.select_one('#batter')

    pitcher_data = get_player_data(div_pitcher)
    batter_data = get_player_data(div_batter)

    return pitcher_data, batter_data


def get_player_data(div):
    team_number_str = div.get('class')[1]

    tr_nm_box = div.select_one('table > tbody > tr > '
                               'td:nth-child(2) > table > '
                               'tbody > tr.nm_box')

    name = tr_nm_box.select_one('td.nm > a').get_text()

    uniform_number_str = tr_nm_box.select_one('td.nm > span').get_text()
    uniform_number = int(uniform_number_str.replace('#', ''))

    dominant_hand = tr_nm_box.select_one('td.dominantHand').get_text()
    left_hand = dominant_hand == '左投' or dominant_hand == '左打'

    return name, uniform_number, left_hand, team_number_str


def judge_team(team_str):
    if team_str == 'team1':
        return '巨人'


if __name__ == '__main__':
    with open(r'D:/prog/MatchRecorder/HTML/2020061901/0110100.html', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        print(take_match_player_data(soup))