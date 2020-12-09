import requests
import os
import re
import time
import crawling


#  指定したyearの指定した範囲の日付のHTMLをとってきてくれる
#  ゲームごとにdirを作ってその中にゲームのHTMLを保存する
#  dirが既に存在すると取ってこない
#  (year=2020, opening_date='01-01', ending_date='12-31')みたいに渡してほしい
def crawling_farm(year, opening_date, ending_date):
    opening_month = int(opening_date.split('-')[0])
    opening_day = int(opening_date.split('-')[1])
    ending_month = int(ending_date.split('-')[0])
    ending_day = int(ending_date.split('-')[1])

    date_url_list = crawling.make_date_url_list(year, opening_month, opening_day, ending_month, ending_day)

    fetch_day(date_url_list)


#  listにある日の試合をとる
def fetch_day(date_url_list):
    for date_url in date_url_list:
        for game_no in range(1, 13):
            score_url = date_url + str(game_no).zfill(2) + '/score'
            start_url = score_url + '?index=0110100'

            if check_dire_exists_farm(score_url):
                continue

            url_status = check_url(score_url)
            if url_status[0]:
                break
            elif url_status[1]:
                continue
            else:
                fetch_game_html(start_url)


#  再帰的に試合のHTMLを取得する
def fetch_game_html(url):
    time.sleep(1)
    result = requests.get(url)

    #  404ならエラーを返す
    if result.status_code == 404:
        return Exception('Error:status_code404')

    #  日付+ゲーム番号(例:2020061901)のディレクトリ名
    game_no_str = re.search('\d{10}', url).group()
    gameDir = os.getcwd() + fr'\HTML_farm\{game_no_str}'
    #  そのディレクトリ無かったら作る
    if not os.path.exists(gameDir):
        os.mkdir(gameDir)

    index = url[-7:]
    #  HTMLファイルの保存
    with open(gameDir + fr'\{index}.html', 'w', encoding='utf-8') as f:
        f.write(result.text)
        print('Done')

    next_url = crawling.get_next_url(result.text)

    if next_url is None:
        return

    fetch_game_html(next_url)


def check_url(url):
    time.sleep(1)
    result = requests.get(url)

    if result.status_code == 404:
        return True, False

    elif crawling.judge_no_game(result.text):
        return False, True

    elif not crawling.judge_farm(result.text):
        return False, True

    else:
        return False, False


def check_dire_exists_farm(url):
    game_no_str = re.search('\d{10}', url).group()
    game_dir = os.getcwd() + f'\\HTML\\{game_no_str}'
    game_dir_farm = os.getcwd() + f'\\HTML_farm\\{game_no_str}'

    return os.path.exists(game_dir) or os.path.exists(game_dir_farm)


#  2軍の試合の出場成績を取ってくる
def crawling_game_stats_farm(year, opening_date='01-01', ending_date='12-31'):
    opening_month = int(opening_date.split('-')[0])
    opening_day = int(opening_date.split('-')[1])
    ending_month = int(ending_date.split('-')[0])
    ending_day = int(ending_date.split('-')[1])

    date_url_list = crawling.make_date_url_list(year, opening_month, opening_day, ending_month, ending_day)
    fetch_day_stats_farm(date_url_list)


#  上関数で使用
def fetch_day_stats_farm(date_url_list):
    for date_url in date_url_list:
        for game_no in range(1, 13):
            score_url = date_url + str(game_no).zfill(2) + '/score'
            stats_url = date_url + str(game_no).zfill(2) + '/stats'

            if check_dir_exists_stats_farm(score_url):
                continue

            url_status = check_url_stats(score_url)
            if url_status[0]:
                break
            elif url_status[1]:
                continue
            else:
                time.sleep(0.5)
                result = requests.get(stats_url)

                save_dir = os.getcwd() + fr'\HTML_game_stats_farm\{stats_url[-16:-6]}.html'
                with open(save_dir, 'w', encoding='utf-8') as f:
                    f.write(result.text)
                    print('Done')


#  出場成績用のURLチェック関数
#  crawling_game_statsで使用
def check_url_stats(url):
    time.sleep(1)
    result = requests.get(url)

    if result.status_code == 404:
        return True, False

    elif crawling.judge_no_game(result.text):
        return False, True

    elif not crawling.judge_farm(result.text):
        return False, True

    else:
        return False, False


#  上関数で使用
def check_dir_exists_stats_farm(url):
    game_no_str = re.search('\d{10}', url).group()
    gameDir = os.getcwd() + f'\\HTML_game_stats\\{game_no_str}.html'
    gameDir_farm = os.getcwd() + f'\\HTML_game_stats_farm\\{game_no_str}.html'
    return os.path.exists(gameDir) or os.path.exists(gameDir_farm)
