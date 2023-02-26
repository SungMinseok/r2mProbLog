# import requests
# from bs4 import BeautifulSoup
# import re

# url = "https://r2m.webzen.co.kr/gameinfo/guide/detail/445"
# response = requests.get(url)
# soup = BeautifulSoup(response.content, 'html.parser')


# #numList = [int]
# for link in soup.find_all('a'):
#     curLink = link.get('href')

#     print(curLink)

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

url = "https://r2m.webzen.co.kr/gameinfo/guide/detail/445"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

for link in tqdm(soup.find_all('a')):
    curLink = link.get('href')
    if curLink.startswith("https://r2m.webzen.co.kr/gameinfo/guide/detail/"):
        numList = [int(s) for s in curLink.split("/") if s.isdigit()]
        if len(numList) > 0:
            print(f"{curLink} ({link.text})")