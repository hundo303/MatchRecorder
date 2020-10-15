#  URLの日付の部分まで作る
#  openingMonth/Dayは開幕日
#  endingMonth/Dayは終了日
def makeDateUrlList(year, openingMonth, opneningDay, endingMonth, endingDay):
    #  1~12月の最後の日(閏年は非考慮)
    lastDaysList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    rootUrl = 'https://baseball.yahoo.co.jp/npb/game/'
    dateUrlList = []
    lastDaysList[endingMonth-1] = endingDay

    for month in range(openingMonth, endingMonth):
        #  基本は1だけど開始月だけは開始日
        startDay = 1
        if month == openingMonth:
            startDay = opneningDay
        #  URL作ってるのはここ
        for day in range(startDay, lastDaysList[month - 1]):
            dayNoStr = str(year) + str(month).zfill(2) + str(day).zfill(2)
            dateUrl = rootUrl + dayNoStr
            dateUrlList.append(dateUrl)

    return dateUrlList


def makeGameUrlList(dateUrl):
    urlList = []

    for gameNo in range(1, 6):
        for inning in range(1, 12):
            for topBottom in range(1, 2):
                for batterNo in range(1, 15):
                    for action in range(0, 10):
                        indexNoStr = str(inning).zfill(2) + str(topBottom) + str(batterNo).zfill(2) + str(action).zfill(2)
                        url = dateUrl + str(gameNo).zfill(2) + '/score?index=' + indexNoStr
                        urlList.append(url)

    return urlList


def crawing():
    dateUrlList = makeDateUrlList(year=2020, openingMonth=6, opneningDay=19, endingMonth=10, endingDay=28)
    print(dateUrlList)

    allUrlList = []

    for dateUrl in dateUrlList:
        gameUrlList = makeGameUrlList(dateUrl)
        allUrlList.append(gameUrlList)


    print(allUrlList[0][0])


crawing()