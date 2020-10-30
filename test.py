import requests
from bs4 import BeautifulSoup
import os


def get_next_url(html):
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

def judge_farm(html):
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find('th', class_ = 'bb-splitsTable__head bb-splitsTable__head--bench')
    if tag is None:
        return True
    else:
        return False

result = requests.get('https://baseball.yahoo.co.jp/npb/game/2020102907/score?index=0110100')

print(judge_farm(result.text))