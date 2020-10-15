import requests
import os
import re

#  URLの日付の部分まで作る
#  openingMonth/Dayは開幕日
#  endingMonth/Dayは終了日
def makeDateUrlList(year, openingMonth, openingDay, endingMonth, endingDay):
    #  1~12月の最後の日(閏年は非考慮)
    lastDaysList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    rootUrl = 'https://baseball.yahoo.co.jp/npb/game/'
    dateUrlList = []
    lastDaysList[endingMonth - 1] = endingDay

    for month in range(openingMonth, endingMonth):
        #  基本は1だけど開始月だけは開始日
        startDay = 1
        if month == openingMonth:
            startDay = openingDay
        #  URL作ってるのはここ
        for day in range(startDay, lastDaysList[month - 1]):
            dayNoStr = str(year) + str(month).zfill(2) + str(day).zfill(2)
            dateUrl = rootUrl + dayNoStr
            dateUrlList.append(dateUrl)

    return dateUrlList


def crawling():
    gameFlag = False
    inningFlag = False
    batterFlag = False

    dateUrlList = makeDateUrlList(year=2020, openingMonth=6, openingDay=19, endingMonth=10, endingDay=28)

    #  多重ループの最下層以外のif文はある程度無視でおｋ
    #  dateURLをリストから引きだすループ
    for dateUrl in dateUrlList:
        #  その日のゲームナンバーのループ
        for gameNo in range(1, 6):
            if gameFlag == True:
                gameFlag = False
                break
            #  イニングのループ
            for inning in range(1, 12):
                if inningFlag == True:
                    inningFlag = False
                    break
                #  表裏のループ
                for topBottom in range(1, 2):
                    for batterNo in range(1, 15):
                        if batterFlag == True:
                            batterFlag = False
                            break
                        #  そのイニングのアクションのループ
                        for action in range(0, 10):
                            result = fetchHtml(dateUrl, gameNo, inning, topBottom, batterNo, action)
                            if result.status_code == 404:
                                if action == 0:
                                    if batterNo == 0:
                                        if inning == 0:
                                            gameFlag = True
                                        inningFlag = True
                                    batterFlag = True
                                break



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
