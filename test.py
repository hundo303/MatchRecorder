import requests
from bs4 import BeautifulSoup
import os
import time
import re


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


def get_next_url(html):
    if check_finish(html):
        return None

    soup = BeautifulSoup(html, 'html.parser')
    p = soup.find('a', id='btn_next')
    url_dir = p.get('href')

    url = 'https://baseball.yahoo.co.jp' + url_dir

    return url


def check_finish(html):
    soup = BeautifulSoup(html, 'html.parser')
    div_tag = soup.find('div', id='detail_footer_leftbox')
    status_text = div_tag.p.get_text()

    if status_text == '試合終了':
        return True
    else:
        return False


fetch_game_html('https://baseball.yahoo.co.jp/npb/game/2020102901/score?index=0110100')
