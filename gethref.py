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
import re


nation = "KR"

if nation == "KR":
    #urlCode = "455"
    url = "https://r2m.webzen.co.kr/gameinfo/guide/detail/445"#kr
    url_core = "https://r2m.webzen.co.kr/gameinfo/guide/detail/"#kr
elif nation == "TW":
    #urlCode = "200"

    url = "https://r2m.webzen.com.tw/gameinfo/guide/detail/200"#tw
    url_core = f"https://r2m.webzen.com.tw/gameinfo/guide/detail/"



response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
total_link = []
total_count = 0

for link in tqdm(soup.find_all('a')):
    curLink = link.get('href')
    #if curLink.startswith("https://r2m.webzen.co.kr/gameinfo/guide/detail/"):
    if curLink.startswith(url_core):
        numList = [int(s) for s in curLink.split("/") if s.isdigit()]
        if len(numList) > 0:
            match = re.search(r'\d+$', curLink)
            if match:
                total_link.append(int(match.group()))
                total_count += 1
            #print(f"{curLink} ({link.text})")


print(total_link)
print(f'{total_count=}')
# links = [
#     "https://r2m.webzen.co.kr/gameinfo/guide/detail/974",
#     "https://r2m.webzen.co.kr/gameinfo/guide/detail/975",
#     "https://r2m.webzen.co.kr/gameinfo/guide/detail/1283"
# ]

# numbers = []
# for link in links:
#     match = re.search(r'\d+$', link)
#     if match:
#         numbers.append(int(match.group()))

# print(numbers)
