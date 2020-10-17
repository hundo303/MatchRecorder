import requests
import os
import re
import time


#  URLの日付の部分まで作る
#  openingMonth/Dayは開幕日
#  endingMonth/Dayは終了日
def makeDateUrlList(year, openingMonth, openingDay, endingMonth, endingDay):
    #  1~12月の最後の日(閏年は非考慮)
    lastDaysList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    rootUrl = 'https://baseball.yahoo.co.jp/npb/game/'
    dateUrlList = []
    lastDaysList[endingMonth - 1] = endingDay

    for month in range(openingMonth, endingMonth + 1):
        #  基本は1だけど開始月だけは開始日
        startDay = 1
        if month == openingMonth:
            startDay = openingDay
        #  URL作ってるのはここ
        for day in range(startDay, lastDaysList[month - 1] + 1):
            dateNoStr = str(year) + str(month).zfill(2) + str(day).zfill(2)
            dateUrl = rootUrl + dateNoStr
            #  既にHTMLが存在してる日はリストに追加しない
            if not os.path.exists(os.getcwd() + f'\\HTML\\{dateNoStr}'):
                dateUrlList.append(dateUrl)

    return dateUrlList


#  動きが保証できない
#  あとクローリングの間の時間入れてないから動かすとまずい
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

