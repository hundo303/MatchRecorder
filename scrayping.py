import glob
import os
from bs4 import BeautifulSoup
import re

top_or_bottom = 1


#  次のページがあるかを確認する
def exists_next_page(html_dir):
    index_number = int(html_dir[-12:-5])
    index_number += 1

    html_dir = html_dir[:-12] + str(index_number) + html_dir[-5:]

    return os.path.exists(html_dir)


#  1球ごとの投球内容のリストを内包した、1打席の投球内容のリストを返す
#  1球ごとの投球内容は[打席での球数, 試合での球数, 球種, 球速, 結果, ストライクカウント, ボールカウント]
def take_pitch_list(soup):
    one_pitch_list = []
    strike_count = 0
    ball_count = 0

    tr_list = soup.select('#pitchesDetail > section:nth-child(2) > table:nth-child(3) > tbody > tr')
    for tr in tr_list:
        td_list = tr.select('td')
        pitch_result_class = td_list[0].span.get('class')[1]
        pitch_result_number = int(pitch_result_class[-1])

        pitch_number_in_at_bat = td_list[0].span.get_text()

        pitch_number_in_game = td_list[1].get_text()

        type_of_pitch = td_list[2].get_text()

        pitch_speed = td_list[3].get_text()

        pitch_result_text = re.sub(r'\s', '', td_list[4].get_text())

        one_pitch_list.append((pitch_number_in_at_bat,
                               pitch_number_in_game,
                               type_of_pitch,
                               pitch_speed,
                               pitch_result_text,
                               ball_count,
                               strike_count))

        strike_count, ball_count = take_count(pitch_result_number, strike_count, ball_count)

    return one_pitch_list


#  上関数で使用
def take_count(result, strike_count, ball_count):
    if result == 1:
        return strike_count + 1, ball_count

    elif result == 2:
        return strike_count, ball_count + 1

    else:
        return strike_count, ball_count


#  打席がアウトか判定する
def judge_out(soup):
    tr_list = soup.select('#pitchesDetail > section:nth-child(2) > table:nth-child(3) > tbody > tr')
    td_list = tr_list[-1].select('td')
    pitch_result_class = td_list[0].span.get('class')[1]
    pitch_result_number = int(pitch_result_class[-1])

    pitch_result_text = re.sub(r'\s', '', td_list[4].get_text())

    return pitch_result_number == 3 or '三振' in pitch_result_text


#  日付と曜日を取ってくる
def take_date(soup):
    date_text = soup.select_one('#gm_menu > section > header > h1 > a').get_text()
    date_split = date_text.split('（')
    date = date_split[0]
    day_week = date_split[1].replace('）', '')

    return date, day_week


#  対戦した2選手の情報を取ってくる
def take_match_player_data(soup):
    global top_or_bottom
    div_pitcher = None

    if top_or_bottom == 1:
        div_pitcher = soup.select_one('#pitcherL > div.card')
    elif top_or_bottom == 2:
        div_pitcher = soup.select_one('#pitcherR > div.card')

    div_batter = soup.select_one('#batter')

    pitcher_data = take_player_data(div_pitcher)
    batter_data = take_player_data(div_batter)

    return [pitcher_data, batter_data]


#  上の関数に使用
def take_player_data(div):
    team_number_str = div.get('class')[1]
    team_name = judge_team_name(team_number_str)

    tr_nm_box = div.select_one('table > tbody > tr > '
                               'td:nth-child(2) > table > '
                               'tbody > tr.nm_box')

    name = tr_nm_box.select_one('td.nm > a').get_text().replace(' ', '')

    uniform_number_str = tr_nm_box.select_one('td.nm > span').get_text()
    uniform_number = int(uniform_number_str.replace('#', ''))

    dominant_hand = tr_nm_box.select_one('td.dominantHand').get_text()
    left_hand = dominant_hand == '左投' or dominant_hand == '左打'

    return name, uniform_number, left_hand, team_name


# 上の関数に使用
def judge_team_name(team_str):
    team_name_list = {1: '巨人', 2: 'ヤクルト', 3: 'DeNA', 4: '中日', 5: '阪神', 6: '広島',
                      7: '西武', 8: '日本ハム', 9: 'ロッテ', 11: 'オリックス', 12: 'ソフトバンク', 376: '楽天'}
    team_number = int(team_str[4:])

    return team_name_list[team_number]


#  守備側のキャッチャーの名前を取得する
def take_catcher_name(soup):
    global top_or_bottom
    td_battery = None

    pitcher_name = take_match_player_data(soup)[0][0]

    if top_or_bottom == 1:
        td_battery = soup.select_one('#gm_memh > table:nth-child(4) > '
                                     'tbody:nth-child(1) > '
                                     'tr.bb-splitsTable__row > td')
    elif top_or_bottom == 2:
        td_battery = soup.select_one('#gm_mema > table:nth-child(4) > '
                                     'tbody:nth-child(1) > '
                                     'tr.bb-splitsTable__row > td')

    battery_pitcher_name = td_battery.select('a')[0].get_text()
    battery_catcher_name = td_battery.select('a')[1].get_text()
    if battery_pitcher_name in pitcher_name:
        return battery_catcher_name


#  その打者が何席数目かを取得する
def take_plate_appearances(soup):
    span_list = soup.select('#batt > tbody > tr > td:nth-child(2) > '
                            'table > tbody > tr:nth-child(2) > td > '
                            'table > tbody > tr:nth-child(2) > td > span')

    plate_appearances = len(span_list) + 1
    return plate_appearances


#  その投手が対戦した打者の数を取得する
def take_match_batter_number(soup):
    td = soup.select_one('#pitcherL > div.card.team1 > '
                         'table > tbody > tr > td:nth-child(2) > '
                         'table > tbody > tr.score > td:nth-child(2)')

    match_batter_number = td.get_text()

    return match_batter_number


def take_coordinate_list(soup):
    coordinate_list = []
    span_list = soup.select('#pitchesDetail > section:nth-child(2) > '
                            'table:nth-child(1) > tbody > tr > td > '
                            'div > span')

    for style_tag in span_list:
        style_text = style_tag.get('style')
        top_text = re.search(r'top:\d+', style_text).group()
        top = int(top_text.replace('top:', ''))
        left_text = re.search(r'left:\d+', style_text).group()
        left = int(left_text.replace('left:', ''))

        coordinate_list.append((top, left))

    return coordinate_list


if __name__ == '__main__':
    with open(r'D:/prog/MatchRecorder/HTML/2020061901/0110100.html', encoding='utf-8') as f:
        soup_main = BeautifulSoup(f, 'html.parser')

        top_or_bottom = int(f.name[-10])

        pitch_list = take_pitch_list(soup_main)

        for i, coordinate in enumerate(take_coordinate_list(soup_main)):
            pitch_list[i] += coordinate

        print('日付:', take_date(soup_main))
        print('対戦情報:', take_match_player_data(soup_main))
        print('ピッチリスト:', pitch_list)
        print('キャッチャー:', take_catcher_name(soup_main))
        print('アウト:', judge_out(soup_main))
        print('第何打席:', take_plate_appearances(soup_main))
        print('打者数:', take_match_batter_number(soup_main))
