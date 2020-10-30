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


date_url_list = make_date_url_list(2020, 9, 28, 10, 29)
print(date_url_list)
