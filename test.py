import requests
import re
import os

def fetchHtml(dateUrl, gameNo, inning, topBottom, batterNo, action):
    indexNoStr = str(inning).zfill(2) + str(topBottom) + str(batterNo).zfill(2) + str(action).zfill(2)
    url = dateUrl + str(gameNo).zfill(2) + '/score?index=' + indexNoStr
    result = requests.get(url)

    print(url)

    gameUrlStr = dateUrl + str(gameNo).zfill(2)
    gameSearch = re.search('\d{10}', gameUrlStr)
    gameNoStr = gameSearch.group()

    print(gameNoStr)

    gameDir = os.getcwd()+f'\\HTML\\{gameNoStr}'
    if result.status_code != 404:
        if not os.path.exists(gameDir):
            os.mkdir(gameDir)

        with open(gameDir+f'\\{indexNoStr}.html', 'w', encoding='utf-8') as f:
            f.write(result.text)
            print('Done')

    else:
        print('miss!')

    return result

fetchHtml('https://baseball.yahoo.co.jp/npb/game/20201012', 1, 1, 1, 1, 0)