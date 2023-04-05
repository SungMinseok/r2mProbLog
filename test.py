# import re
# # text = "+0 → +1"
# # print(re.search(r"^[^→]+", text).group())



# text = "+3 파괴의 가면"
# changeText = re.sub(r'\+\d+\s*', '', text)
# print(changeText)

# match = re.search(r'\+\d+', text)
# if match:
#     result = match.group()
#     print(result)
# else:
#     print("No match")
# match = re.search(r'\d+', text)
# if match:
#     result = match.group()
#     print(result)
# else:
#     print("No match")


# import pandas as pd

# # csv 파일 경로 리스트
# csv_files = ['file1.csv', 'file2.csv', 'file3.csv']

# # 데이터프레임으로 합치기
# df = pd.concat([pd.read_csv(f, index_col=None) for f in csv_files])

# # 엑셀 파일로 저장
# df.to_excel('merged.xlsx', index=False)
import pandas as pd

csv_path = './최종모음/각인.csv'
xlsx_path = 'example.xlsx'

df = pd.read_csv(csv_path)
df.to_excel(xlsx_path, index=False)
pandas를 사용하지말고 각 csv파일의 내용을 복사해서 xlsx파일의 각시트에 복사해 넣는 파이썬 코드