import glob
import os
from bs4 import BeautifulSoup


def get_span():
    count = 0

    score_list = ['ゴロ', 'フライ', 'ライナー', '三振', 'ヒット',
                  '本塁打', '併殺', '四球', '死球', '安打',
                  '二塁打', '三塁打', '犠飛', '犠打', 'エラー',
                  '継投', '代打', '申告敬遠', '試合終了', '代走',
                  '守備', 'ボール', '空振り', '見逃し', 'スリーバント',
                  'けん制', 'ボーク', 'バント', '野選', '振り逃げ',
                  '2塁打', '3塁打', '打撃妨害']

    files = glob.glob(os.getcwd() + '\\HTML\\*\\*')
    for file in files:
        print(type(file))
        with open(file, encoding='utf-8') as html:
            soup = BeautifulSoup(html, 'html.parser')
            tag = soup.find('div', id='result')

            if tag.span is None:
                print(file)
                print('none')
                print('\n')
                continue

            result_text = tag.span.get_text()

            if not any(score_name in result_text for score_name in score_list):
                print(file)
                print(result_text)
                print('\n')
                continue

    print(f'カウント:{count}')
