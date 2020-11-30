import requests
import os
import re
from bs4 import BeautifulSoup
import time


#  指定したyearの指定した範囲の日付のHTMLをとってきてくれる
#  ゲームごとにdirを作ってその中にゲームのHTMLを保存する
#  dirが既に存在すると取ってこない
#  (year=2020, opening_date='01-01', ending_date='12-31')みたいに渡してほしい
def crawling_season(year, opening_date, ending_date):
    opening_month = int(opening_date.split('-')[0])
    opening_day = int(opening_date.split('-')[1])
    ending_month = int(ending_date.split('-')[0])
    ending_day = int(ending_date.split('-')[1])

    date_url_list = make_date_url_list(year, opening_month, opening_day, ending_month, ending_day)

    fetch_day(date_url_list)


#  URLの日付の部分まで作る
#  openingMonth/Dayは開幕日
#  endingMonth/Dayは終了日
def make_date_url_list(year, opening_month, opening_day, ending_month, ending_day):
    #  1~12月の最後の日(閏年は非考慮)
    lastDaysList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    rootUrl = 'https://baseball.yahoo.co.jp/npb/game/'
    date_url_list = []
    lastDaysList[ending_month - 1] = ending_day

    for month in range(opening_month, ending_month + 1):
        #  基本は1だけど開始月だけは開始日
        startDay = 1
        if month == opening_month:
            startDay = opening_day

        #  URL作ってるのはここ
        for day in range(startDay, lastDaysList[month - 1] + 1):
            dateNoStr = str(year) + str(month).zfill(2) + str(day).zfill(2)
            date_url = rootUrl + dateNoStr
            date_url_list.append(date_url)

    return date_url_list


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
    gameDir = os.getcwd() + f'\\HTML\\{game_no_str}'
    #  そのディレクトリ無かったら作る
    if not os.path.exists(gameDir):
        os.mkdir(gameDir)

    index = url[-7:]
    #  HTMLファイルの保存
    with open(gameDir + f'\\{index}.html', 'w', encoding='utf-8') as f:
        f.write(result.text)
        print('Done')

    next_url = get_next_url(result.text)

    if next_url is None:
        return

    fetch_game_html(next_url)


#  html投げると次のURL返ってくる
#  試合終了だとNoneを返す
def get_next_url(html):
    if check_finish(html):
        return None

    soup = BeautifulSoup(html, 'html.parser')
    p = soup.find('a', id='btn_next')
    url_dir = p.get('href')

    url = 'https://baseball.yahoo.co.jp' + url_dir

    return url


#  投げたHTMLが試合終了のページだとTrueを還す
def check_finish(html):
    soup = BeautifulSoup(html, 'html.parser')
    div_tag = soup.find('div', id='detail_footer_leftbox')
    status_text = div_tag.p.get_text()

    if status_text == '試合終了':
        return True
    else:
        return False


#  404 or ファームの試合なら(True, False)
#  そのゲームのdirが存在する or ノーゲームなら(False, True)
#  その他は(False, False)を返す
def check_url(url):
    if check_dir_exists(url):
        return False, True

    time.sleep(0.5)
    result = requests.get(url)

    if result.status_code == 404:
        return True, False

    elif judge_no_game(result.text):
        return False, True

    elif judge_farm(result.text):
        return True, False

    else:
        return False, False


#  試合がノーゲームだとTrueを返す
def judge_no_game(html):
    soup = BeautifulSoup(html, 'html.parser')
    div_tag = soup.find('div', id='detail_footer_leftbox')
    status_text = div_tag.p.get_text()

    if status_text == 'ノーゲーム' or status_text == '試合中止':
        return True
    else:
        return False


#  試合が2軍戦だとTrueを返す
def judge_farm(html):
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find('th', class_='bb-splitsTable__head bb-splitsTable__head--bench')
    if tag is None:
        return True
    else:
        return False


#  そのゲームのdirが存在したらTrueを返す
def check_dir_exists(url):
    game_no_str = re.search('\d{10}', url).group()
    gameDir = os.getcwd() + f'\\HTML\\{game_no_str}'
    return os.path.exists(gameDir)


def take_player_list():
    team_number_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11', '12', '376']
    root_url = 'https://baseball.yahoo.co.jp/npb/teams/'
    root_dir = os.getcwd() + '\\HTML_player'

    for team_number in team_number_list:
        team_url = root_url + team_number + '/memberlist'
        p_url = team_url + '?kind=p'
        b_url = team_url + '?kind=b'
        time.sleep(0.5)
        p_result = requests.get(p_url)
        time.sleep(0.5)
        b_result = requests.get(b_url)

        os.makedirs(fr'{root_dir}\{team_number}', exist_ok=True)
        with open(fr'{root_dir}\{team_number}\P.html', 'w', encoding='utf-8') as f:
            f.write(p_result.text)
            print('Done')
        with open(fr'{root_dir}\{team_number}\B.html', 'w', encoding='utf-8') as f:
            f.write(b_result.text)
            print('Done')
