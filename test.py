import requests
from bs4 import BeautifulSoup
import os
import time
import re


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

    if status_text == 'ノーゲーム':
        return True
    else:
        return False


#  試合が2軍戦だとTrueを返す
def judge_farm(html):
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find('th', class_ = 'bb-splitsTable__head bb-splitsTable__head--bench')
    if tag is None:
        return True
    else:
        return False


#  そのゲームのdirが存在したらTrueを返す
def check_dir_exists(url):
    game_no_str = re.search('\d{10}', url).group()
    gameDir = os.getcwd() + f'\\HTML\\{game_no_str}'
    return os.path.exists(gameDir)


print(check_url('https://baseball.yahoo.co.jp/npb/game/2020070904/score'))
