import os
import pandas as pd

def merge_csv_to_excel():
    # 현재 폴더 내의 csv 파일 리스트를 가져옴
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]

    # csv 파일을 순회하며 데이터를 병합
    writer = pd.ExcelWriter('merged.xlsx', engine='xlsxwriter')
    for csv_file in csv_files:
        sheet_name = csv_file.split('.')[0]
        df = pd.read_csv(csv_file)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    # 작성한 엑셀 파일 저장
    writer.save()
