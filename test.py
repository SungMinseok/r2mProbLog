import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# url 리스트
url_list = [940, 941, 942, 943, 944, 945, 947, 1423, 946, 948, 949, 950, 951, 1404, 952, 953, 955, 1338, 1405, 954, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 1418, 1419, 1420, 1421, 974, 975, 1283, 1326, 976
]

# 엑셀 파일 생성
writer = pd.ExcelWriter('webProb.xlsx')

for url in tqdm(url_list):
    urlPage = str(url)
    # url 생성
    url = f'https://r2m.webzen.co.kr/gameinfo/guide/detail/{url}'

    # requests 모듈을 사용하여 해당 페이지에 GET 요청을 보냄
    response = requests.get(url)

    # BeautifulSoup 모듈을 사용하여 HTML을 파싱
    soup = BeautifulSoup(response.content, 'html.parser')

    # HTML에서 모든 테이블 요소를 찾음
    tables = soup.find_all('table')

    # 시트명 설정
    sheet_name = str(url)

    # pandas 모듈을 사용하여 테이블을 DataFrame으로 변환하여 시트에 저장
    for i, table in enumerate(tables):
        df = pd.read_html(str(table))[0]
        # if i == 0:
        #     df.to_excel(writer, index=False)
        # else:
        df = df.replace('확률(%)','확률')
        df.to_excel(writer, sheet_name=f'{urlPage}_{i}', index=False, columns=None)

# 엑셀 파일 저장
writer.save()
