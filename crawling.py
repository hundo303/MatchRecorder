import requests
import os
import re
from bs4 import BeautifulSoup
import time


#  URLの日付の部分まで作る
#  openingMonth/Dayは開幕日
#  endingMonth/Dayは終了日
def make_date_url_list(year, openingMonth, openingDay, endingMonth, endingDay):
    #  1~12月の最後の日(閏年は非考慮)
    lastDaysList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    rootUrl = 'https://baseball.yahoo.co.jp/npb/game/'
    date_url_list = []
    lastDaysList[endingMonth - 1] = endingDay

    for month in range(openingMonth, endingMonth + 1):
        #  基本は1だけど開始月だけは開始日
        startDay = 1
        if month == openingMonth:
            startDay = openingDay

        #  URL作ってるのはここ
        for day in range(startDay, lastDaysList[month - 1] + 1):
            dateNoStr = str(year) + str(month).zfill(2) + str(day).zfill(2)
            date_url = rootUrl + dateNoStr
            date_url_list.append(date_url)

    return date_url_list


#  その日の試合をとる
def fetch_day(date_url_list):
    #  その試合のhtmlを取ってくるかの諸々のチェックするための関数がほしい
    for date_url in date_url_list:
        for game_no in range(0, 7):
            start_url = date_url + str(game_no).zfill(2) + '/score?index=0110100'

            url_status = check_url(start_url)
            if url_status[0]:
                break
            elif url_status[1]:
                 continue
            else:
                fetch_game_html(start_url)

#  再帰的に試合のHTMLを取得する
def fetch_game_html(url):
    result = requests.get(url)

    #  404ならエラーを返す
    if result.status_code == 404:
        return Exception('Error:status_code404')

    #  日付+ゲーム番号(例:2020061901)のディレクトリ名
    game_no_str = re.search('\d{10}', url).group()
    gameDir = os.getcwd() + f'\\HTML\\{game_no_str}'
    #  そのディレクトリ無かったら作る
    if os.path.exists(gameDir):
        os.mkdir(gameDir)

    #  HTMLファイルの保存
    with open(gameDir + f'\\{game_no_str}.html', 'w', encoding='utf-8') as f:
        f.write(result.text)
        print('Done')

    next_url = get_next_url(result.text)

    if next_url is None:
        return

    fetch_game_html(next_url)


#  html投げると次のURL返ってくる
def get_next_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    p = soup.find('a', id='btn_next')
    url_dir = p.get('href')

    if check_finish(html):
        return None

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
#  そのゲームのdirが存在するなら(False, True)
#  その他は(False, False)を返す
def check_url(url):
    result = requests.get(url)
    if result.status_code == 404:
        return True, False

    elif judge_farm(result.text):
        return True, False

    elif check_dir_exists(url):
        return False, True

    else:
        return False, False


#  試合が2軍戦だとTrueを返す
def judge_farm(html):
    return True


#  そのゲームのdirが存在したらTrueを返す
def check_dir_exists():
    return True


#  動きが保証できない
#  以下はゴミ
'''
def crawling(dateUrlList):
    gameFlag = False
    inningFlag = False
    batterFlag = False

    #  多重ループの最下層以外のif文はある程度無視でおｋ
    #  dateURLをリストから引きだすループ
    for dateUrl in dateUrlList:
        #  その日のゲームナンバーのループ
        for gameNo in range(1, 7):
            if gameFlag:
                gameFlag = False
                break
            #  イニングのループ
            for inning in range(1, 13):
                if inningFlag:
                    inningFlag = False
                    break
                #  表裏のループ
                for topBottom in range(1, 3):
                    #  バッターのループ
                    for batterNo in range(1, 15):
                        if batterFlag:
                            batterFlag = False
                            break
                        #  そのイニングのアクションのループ
                        for action in range(0, 10):
                            #  ディレイ入れてfetchHTMLを使ってリクエストを送る
                            time.sleep(0.1)
                            result, gameFlag, inningFlag, batterFlag = fetchHtml(dateUrl, gameNo, inning, topBottom,
                                                                                 batterNo, action)
                            if result.status_code == 404:
                                break


def fetchHtml(dateUrl, gameNo, inning, topBottom, batterNo, action):
    gameFlag = False
    inningFlag = False
    batterFlag = False

    #  URL作ってリクエスト送ってる
    indexNoStr = str(inning).zfill(2) + str(topBottom) + str(batterNo).zfill(2) + str(action).zfill(2)
    url = dateUrl + str(gameNo).zfill(2) + '/score?index=' + indexNoStr
    result = requests.get(url)

    #  日付+ゲームナンバーが名前のディレクトリを作ってる
    gameUrlStr = dateUrl + str(gameNo).zfill(2)
    gameSearch = re.search('\d{10}', gameUrlStr)
    gameNoStr = gameSearch.group()
    gameDir = os.getcwd() + f'\\HTML\\{gameNoStr}'

    #  ステータスコードが200の場合
    if result.status_code == 200:
        os.mkdir(gameDir)
        #  HTMLファイルの保存
        with open(gameDir + f'\\{indexNoStr}.html', 'w', encoding='utf-8') as f:
            f.write(result.text)
            print('Done')

    #  ステータスコードが404の場合
    elif result.status_code == 404:
        if action == 0:
            if batterNo == 1:
                if inning == 1:
                    gameFlag = True
                inningFlag = True
            batterFlag = True

    #  ステータスコードが200でも404でもない場合
    else:
        print('StatusCodeError')

    return result, gameFlag, inningFlag, batterFlag
'''
