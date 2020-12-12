import os
import glob
from bs4 import BeautifulSoup
import scrayping as sp
import sqlite3

#  通常、打席途中での代打は「2ストライクから代打の場合を除いて、打席終了時の打者の行為として扱う」が
#  このシステムでは2ストライクでの交代でも打席終了時の打者の記録として扱う。
#  また打席途中の投手交代は「ボール先行からの登板以外は救援投手の責任とする」が
#  このシステムではボール先行からの登板であっても救援投手の責任として扱う。
#  よって多少の誤差が発生するのでごめんなさい


def write_player_profile():
    #  dbファイルの取り込み
    cnn = sqlite3.connect('baseball.db')
    c = cnn.cursor()

    #  テーブルが無い場合はテーブルを作成
    c.execute('CREATE TABLE IF NOT EXISTS player('
              'id integer NOT NULL UNIQUE ,'
              'team text NOT NULL,'
              'name text NOT NULL,'
              'uniform_number integer NOT NULL,'
              'position text NOT NULL, '
              'date_of_birth date, '
              'height integer, '
              'weight integer, '
              'throw_arm text, '
              'batting_arm text, '
              'draft_year integer, '
              'draft_rank text, '
              'total_year integer)')

    #  htmlファイルを取得
    files = glob.glob(os.getcwd() + r'\HTML_player\*\*')

    #  htmlファイルをループで回す
    for file in files:
        #  チームの選手一覧は除外
        if 'B.html' in file or 'P.html' in file:
            continue

        #  ファイル名からIDを取得
        player_id = int(os.path.basename(file).replace('.html', ''))

        #  ディレクトリ名からチーム名を取得
        team_name_list = {1: '巨人', 2: 'ヤクルト', 3: 'DeNA', 4: '中日', 5: '阪神', 6: '広島',
                          7: '西武', 8: '日本ハム', 9: 'ロッテ', 11: 'オリックス', 12: 'ソフトバンク', 376: '楽天'}
        team_number = int(os.path.basename(os.path.dirname(file)))
        team = team_name_list[team_number]

        #  dbファイルへの書き込み
        with open(file, encoding='utf=8') as f:
            soup = BeautifulSoup(f, 'html.parser')

            #  take_player_profileのタプルにidとteamを加えて最終的なタプルを作成
            profile_tuple = sp.take_player_profile(soup)
            profile_tuple = (player_id, team) + profile_tuple

            c.execute('INSERT INTO player VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      profile_tuple)

    cnn.commit()
    cnn.close()


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


if __name__ == '__main__':
    write_player_profile()
