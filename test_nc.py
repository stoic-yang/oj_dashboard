import requests
from bs4 import BeautifulSoup
res = requests.get('https://ac.nowcoder.com/acm/contest/profile/82654', headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(res.text, 'html.parser')
print('状态码:', res.status_code)
states = soup.find_all('div', class_='state-num')
for state in states:
    print(state.text.strip())
