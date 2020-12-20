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


def main_kari():
    files = glob.glob(os.getcwd() + r'\HTML\*\*')
    #  files = [os.getcwd() + r'\HTML\2020062105\0710400.html']
    start_num = 0
    id_at_bat = 1

    cnn = sqlite3.connect('baseball_test.db')
    c = cnn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS game_data('
              'id_at_bat INTEGER NOT NULL,'
              'pitcher_id INTEGER NOT NULL,'
              'pircher_left INTEGER NOT NULL,'
              'batter_id INTEGER  NOT NULL,'
              'batter_left INTEGER NOT NULL,'
              'in_box_count INTEGER NOT NULL,'
              'match_number_times INTEGER NOT NULL,'
              'c TEXT NOT NULL,'
              'first TEXT NOT NULL,'
              'second TEXT NOT NULL,'
              'third TEXT NOT NULL,'
              'ss TEXT NOT NULL,'
              'lf TEXT NOT NULL,'
              'cf TEXT NOT NULL,'
              'rf TEXT NOT NULL,'
              'first_runner TEXT,'
              'second_runner TEXT,'
              'third_runner TEXT,'
              'number_pitch_at_bat INTEGER NOT NULL,'
              'number_pitch_game INTEGER NOT NULL,'
              'ball_type TEXT NOT NULL,'
              'speed INTEGER,'
              'ball_result TEXT NOT NULL,'
              'ball_count INTEGER NOT NULL,'
              'strike_count INTEGER NOT NULL,'
              'top_coordinate INTEGER NOT NULL,'
              'left_coordinate INTEGER NOT NULL,'
              'steal TEXT,'
              'steam_non_pitch INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS data_at_bat('
              'id_at_bat INTEGER NOT NULL UNIQUE,'
              'inning INTEGER NOT NULL,'
              'date DATE NOT NULL,'
              'day_week TEXT NOT NULL,'
              'out INTEGER NOT NULL,'
              'rbi INTEGER NOT NULL,'
              'result_big TEXT NOT NULL,'
              'result_small TEXT NOT NULL,'
              'intentional_walk NOT NULL)')
    cnn.commit()
    cnn.close()
    cnn = sqlite3.connect('baseball_test.db')

    for file in files:
        print(file)
        write_steal = None
        steal_non_pitch = None
        intentional_walk = False
        inning = file[-11]

        with open(file, encoding='utf-8') as f:
            top_or_bottom = int(f.name[-10])
            soup = BeautifulSoup(f, 'html.parser')

            if '申告敬遠' in sp.take_result_at_bat(soup)[0]:
                intentional_walk = True

            elif sp.judge_no_pitch(soup) or sp.judge_non_butter(soup):
                continue

            pitch_data_list = make_pitch_data_list(soup, top_or_bottom)
            data_at_bat = make_data_at_bat(soup)

            if not pitch_data_list:
                write_data_at_bat(cnn, data_at_bat, intentional_walk, id_at_bat, inning)
                start_num = 0
                id_at_bat += 1
                continue

            for steal in ('盗塁成功', '盗塁失敗'):
                if steal in data_at_bat['result_small'] and not '盗塁成功率' in data_at_bat['result_small']:
                    write_steal = steal
                    steal_non_pitch = False
                    if steal in pitch_data_list[-1]['ball_result']:
                        steal_non_pitch = True

            if any(four_result in pitch_data_list[-1]['ball_result'] for four_result in ('見逃し', '空振り', 'ボール', 'ファウル')):
                if intentional_walk:
                    write_data_at_bat(cnn, data_at_bat, intentional_walk, id_at_bat, inning)
                    start_num = 0
                    id_at_bat += 1
                else:
                    write_game_data(cnn, start_num, pitch_data_list, write_steal, steal_non_pitch, id_at_bat)
                    start_num = len(pitch_data_list)

            else:
                write_game_data(cnn, start_num, pitch_data_list, write_steal, steal_non_pitch, id_at_bat)
                write_data_at_bat(cnn, data_at_bat, intentional_walk, id_at_bat, inning)
                start_num = 0
                id_at_bat += 1


def write_game_data(cnn, start_num, pitch_data_list, steal, steal_non_pitch, id_at_bat):
    #  start_numより後ろのみ書き込む
    save_data_list = pitch_data_list[start_num:]

    #  辞書型をタプルに変換
    #  stealとsteal_non_pitchを追加して最終的なタプルを作成
    for i in range(len(save_data_list)):
        save_data_list[i] = tuple(save_data_list[i].values())
        save_data_list[i] = (id_at_bat,) + save_data_list[i]
        save_data_list[i] += (steal, steal_non_pitch)

    c = cnn.cursor()

    c.executemany('INSERT INTO game_data VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  save_data_list)

    cnn.commit()


def write_data_at_bat(cnn, data_at_bat, intentional_walk, id_at_bat, inning):
    save_data = (id_at_bat, inning) + tuple(data_at_bat.values()) + (intentional_walk,)
    c = cnn.cursor()

    c.execute('INSERT INTO data_at_bat VALUES (?,?,?,?,?,?,?,?,?)', save_data)


def make_pitch_data_list(soup, top_or_bottom):
    pitch_data_list = []

    match_player_data = sp.take_match_player_data(soup, top_or_bottom)
    pitcher_id = match_player_data[0][0]
    pitcher_left = match_player_data[0][1]
    batter_id = match_player_data[1][0]
    batter_left = match_player_data[1][1]

    #  catcher_name = sp.take_catcher_name(soup, top_or_bottom)
    in_box_count = sp.take_plate_appearances(soup)
    match_batter_number_times = sp.take_match_batter_number(soup, top_or_bottom)

    defense = sp.take_defense(soup, top_or_bottom)

    c = defense['捕']
    first = defense['一']
    second = defense['二']
    third = defense['三']
    ss = defense['遊']
    lf = defense['左']
    cf = defense['中']
    rf = defense['右']

    runner = sp.take_runner(soup)
    first_runner = runner[1]
    second_runner = runner[2]
    third_runner = runner[3]

    pitch_list = sp.take_pitch_list(soup)
    coordinate_list = sp.take_coordinate_list(soup)

    for pitch_ball_data, coordinate in zip(pitch_list, coordinate_list):
        number_pitch_at_bat = pitch_ball_data[0]
        number_pitch_game = pitch_ball_data[1]
        ball_type = pitch_ball_data[2]
        speed = pitch_ball_data[3]
        ball_result = pitch_ball_data[4]
        ball_count = pitch_ball_data[5]
        strike_count = pitch_ball_data[6]
        top_coordinate = coordinate[0]
        left_coordinate = coordinate[1]

        pitch_data = {'pitcher_id': pitcher_id, 'pitcher_left': pitcher_left,
                      'batter_id': batter_id, 'batter_left': batter_left,
                      'in_box_count': in_box_count,
                      'match_batter_number_times': match_batter_number_times,
                      'c': c, 'first': first, 'second': second, 'third': third, 'ss': ss,
                      'lf': lf, 'cf': cf, 'rf': rf, 'first_runner': first_runner,
                      'second_runner': second_runner, 'third_runner': third_runner,
                      'number_pitch_at_bat': number_pitch_at_bat,
                      'number_pitch_game': number_pitch_game, 'ball_type': ball_type,
                      'speed': speed, 'ball_result': ball_result, 'ball_count': ball_count,
                      'strike_count': strike_count, 'top_coordinate': top_coordinate,
                      'left_coordinate': left_coordinate}

        pitch_data_list.append(pitch_data)

    return pitch_data_list


def make_data_at_bat(soup):
    date_list = sp.take_date(soup)
    date = date_list[0]
    day_week = date_list[1]

    out = sp.judge_out(soup)

    result_at_bat = sp.take_result_at_bat(soup)
    result_big = result_at_bat[0]
    result_small = result_at_bat[1]

    rbi = sp.take_rbi(result_big)

    data_at_bat = {'data': date, 'day_week': day_week, 'out': out, 'rbi': rbi,
                   'result_big': result_big, 'result_small': result_small}

    return data_at_bat


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
    '''
    start_num_main = 0
    with open(r'D:/prog/MatchRecorder/HTML/2020082501/0110100.html', encoding='utf-8') as f:
        soup_main = BeautifulSoup(f, 'html.parser')
        top_or_bottom_main = int(f.name[-10])

        pitch_data_list_main, data_at_bat_main = make_data_list(soup_main, top_or_bottom_main)

        save_data_list_main = pitch_data_list_main[start_num_main:]
        for i in range(len(save_data_list_main)):
            save_data_list_main[i] = tuple(save_data_list_main[i].values())

        print(len(save_data_list_main[0]))
#  ballリザルト読んで、盗塁成功か盗塁失敗があったらそれを返す関数
'''
    main_kari()
