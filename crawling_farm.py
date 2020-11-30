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
        for game_no in range(1, 7):
            score_url = date_url + str(game_no).zfill(2) + '/score'
            start_url = score_url + '?index=0110100'

            url_status = check_url(score_url)
            if url_status[0]:
                break
            elif url_status[1]:
                continue
            else:
                fetch_game_html(start_url)


#  再帰的に試合のHTMLを取得する
def fetch_game_html(url):
    time.sleep(0.5)
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


#  404 or ファームの試合なら(True, False)
#  そのゲームのdirが存在する or ノーゲームなら(False, True)
#  その他は(False, False)を返す
def check_url(url):
    if crawling.check_dir_exists(url):
        return False, True

    time.sleep(0.5)
    result = requests.get(url)

    if result.status_code == 404:
        return True, False

    elif crawling.judge_no_game(result.text):
        return False, True

    elif not crawling.judge_farm(result.text):
        return True, False

    else:
        return False, False
