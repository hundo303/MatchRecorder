import glob
import os
from bs4 import BeautifulSoup
import re


def exists_next_page(html_dir):
    index_number = int(html_dir[-12:-5])
    index_number += 1

    html_dir = html_dir[:-12] + str(index_number) + html_dir[-5:]

    return os.path.exists(html_dir)


#  1球ごとの投球内容のリストを内包した、1打席の投球内容のリストを返す
#  1球ごとの投球内容は[打席での球数, 試合での球数, 球種, 球速, 結果]
def take_ball_list(html):
    one_pitch_list = []

    soup = BeautifulSoup(html, 'html.parser')
    tr_list = soup.select('#pitchesDetail > section:nth-child(2) > table:nth-child(3) > tbody > tr')
    for tr in tr_list:
        td_list = tr.select('td')
        pitch_number_in_at_bat = td_list[0].span.get_text()
        pitch_number_in_game = td_list[1].get_text()
        type_of_pitch = td_list[2].get_text()
        pitch_speed = td_list[3].get_text()
        pitch_result = re.sub(r'\s', '', td_list[4].get_text())

        one_pitch_list.append([pitch_number_in_at_bat,
                               pitch_number_in_game,
                               type_of_pitch,
                               pitch_speed,
                               pitch_result])

    return one_pitch_list


with open(r'D:/prog/MatchRecorder/HTML/2020061901/0110100.html', encoding='utf-8') as f:
    result = take_ball_list(f)
    for data in result:
        print(data)
