import requests

result = requests.get('https://baseball.yahoo.co.jp/npb/game/2020101601/score?index=0720300')

print(result.status_code)
