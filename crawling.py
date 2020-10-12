def makeDayUrl(year):
    daysList = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    dayUrllList = []
    rootUrl = 'https://baseball.yahoo.co.jp/npb/game/'

    for month in range(1, 12):
        for day in range(1, daysList[month - 1]):
            dayUrl = f'{rootUrl}{year}{str(month).zfill(2)}{str(day).zfill(2)}'
            dayUrllList.append(dayUrl)

    return dayUrllList
'''
def makeGameUrl(dayUrl):
    for gameNo in range(1, 6):
        for inning in range(1, 12):
            for topBottom in range(1, 2):
                for batterNo in range(1, 15):
                    for action in range(1, 10):
                        url = dayUrl +


def crawling():
    dayUrl = makeDayUrl(2020)
'''

print(makeDayUrl(2020))