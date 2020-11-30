import os
import glob
from bs4 import BeautifulSoup
import scrayping as sp


#  次のページがあるかを確認する
def exists_next_page(html_dir):
    index_number = int(html_dir[-12:-5])
    index_number += 1

    html_dir = html_dir[:-12] + str(index_number) + html_dir[-5:]

    return os.path.exists(html_dir)


def main_kari():
    files = glob.glob(os.getcwd() + '\\HTML\\*\\*').sort()
    for file in files:
        with open(file, encoding='utf-8') as f:
            soup_main = BeautifulSoup(f, 'html.parser')
            top_or_bottom_main = int(f.name[-10])


def make_data_list(soup, top_or_bottom):
    date = sp.take_date(soup)
    match_player_data = sp.take_match_player_data(soup, top_or_bottom)
    pitch_list = sp.pitch_list
    coordinate_list = sp.take_coordinate_list(soup)
    catcher_name = sp.take_catcher_name(soup, top_or_bottom)
    out = sp.judge_out(soup)
    plate_appearances = sp.take_plate_appearances(soup)
    match_batter_number = sp.take_match_batter_number(soup, top_or_bottom)
    defense = sp.take_defense(soup, top_or_bottom)
    result_at_bat = sp.take_result_at_bat(soup)
    runner = sp.take_runner(soup)

    data_list = (date[0], date[1], )


def judge_next_state(pitch_list, result_at_bat):

    pitch_result = pitch_list[-1][4]
    if ('見逃し' or '空振り' or 'ボール' or 'ファウル') in pitch_result:
        if ('代打' or '続投') in result_at_bat:
            return 3
        else:
            return 2
    else:
        return 1
