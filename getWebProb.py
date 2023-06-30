import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time


nation = "KR"
#nation = "TW"

"""
url_list 를 참조하여, 해당 링크에 있는 모든 확률 고지표를 A_i 시트에 저장함.
"""

# url 리스트
if nation == "KR":
    #23년1분기
    url_list = [940, 941, 942, 943, 944, 945, 947, 1423, 946, 948, 949, 950, 951, 1404, 952, 953, 955, 1338, 1405, 954, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 1418, 1419, 1420, 1421, 974, 975, 1283, 1326, 976]
    #23년2분기
    url_list = [940, 941, 942, 943, 944, 945, 947, 1423, 946, 948, 949, 950, 951, 1404, 952, 953, 955, 1338, 1405, 954, 956, 957, 958, 959, 960, 961, 1510, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 1509, 1418, 1419, 1420, 1421, 974, 975, 1283, 1326, 976]

elif nation == "TW":
    #23년2분기
    url_list = [203,204,222,228,236,237,242,252,262,280,205,206,238,239,240,241,243,251,254,281,224,225,310,231,232,233,234,309,235,256,257,258,259,260,261,288,289,290,291,292,293,298,299,303,301,302,304,305,306,307,308]




# 엑셀 파일 생성
writer = pd.ExcelWriter(f"webProb_{nation}_{time.strftime('%y%m%d_%H%M%S')}.xlsx")

totalTableCount = 0
for url in tqdm(url_list):
    urlPage = str(url)
    # url 생성
    if nation == "KR" :
        url = f'https://r2m.webzen.co.kr/gameinfo/guide/detail/{url}'#kr
    elif nation =="TW":
        url = f'https://r2m.webzen.com.tw/gameinfo/guide/detail/{url}'#tw

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
        df = df.astype(str).apply(lambda x: x.str.replace('\xa0', ' '))
        #df = df.replace(' ',' ')
        #df = df.drop(0, axis=0)
        if int(urlPage) >= 962 and int(urlPage) <= 973 :
            df.to_excel(writer, sheet_name=f'{urlPage}_{i}', index=False, header=True)

        else : 
            df.to_excel(writer, sheet_name=f'{urlPage}_{i}', index=False, header=False)

        totalTableCount += 1


# 엑셀 파일 저장
writer.save()
print(totalTableCount)
