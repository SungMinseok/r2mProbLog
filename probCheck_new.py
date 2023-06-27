import pandas as pd
import time
import os
import gc
import re
from tqdm import tqdm
from openpyxl import load_workbook
import numpy as np

resultBasicDir = f"./result"
if not os.path.isdir(resultBasicDir) :
    os.mkdir(resultBasicDir)

#resultDir = f"./result/{time.strftime('%y%m%d_%H%M%S')}"
resultDir = f"./result/{time.strftime('%y%m%d')}"
if not os.path.isdir(resultDir) :
    os.mkdir(resultDir)


resultName = f"{resultDir}/result_{time.strftime('%H%M%S')}.xlsx"
reportName = f"{resultDir}/report_{time.strftime('%H%M%S')}.csv"

#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■#
'''인게임 로그데이터 처리'''

ingame_file = "R2MProbabilityTestHistory_20230626_20230627.csv"#인게임에서 추출한 확률 로그
df_log = pd.read_csv(ingame_file)
df_log["etc_json"] = df_log["etc_json"].str.replace("}","]")


#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■#
'''csv 데이터파일 처리'''


def getCsvFile(fileName):
    global df_item
    global df_tran
    global df_serv
    global df_skill
    global df_engraveAbility
    global df_engraveSlain
    global df_prob
    global df_probInfo

    df_temp = pd.read_csv(fileName)
    #df_temp = df_temp.reset_index(drop=True)
    #df_temp = df_temp.set_index("mID")

    if "item" in fileName :
        df_item = df_temp.copy()
        df_item["mName"] = df_item["mName"].str.replace(" ", "")

    elif "transform" in fileName :
        df_tran = df_temp.copy()
    elif "servant" in fileName :
        df_serv = df_temp.copy()
    elif "skill" in fileName :
        df_skill = df_temp.copy()
    elif "engraveAbility" in fileName :
        df_engraveAbility = df_temp.copy()
    elif "engraveSlain" in fileName :
        df_engraveSlain = df_temp.copy()
    elif "probInfo" in fileName :
        df_probInfo = df_temp.copy()
        #df_probInfo = df_probInfo.astype({'0': 'int64', '1': 'int64'})

    elif "prob" in fileName :
        df_prob = df_temp.copy()

    print(f"success, get csv file : {fileName}")


getCsvFile(f"./data/item.csv")
getCsvFile(f"./data/transform.csv")
getCsvFile(f"./data/servant.csv")
getCsvFile(f"./data/skillList.csv")
getCsvFile(f"./data/engraveAbilityType.csv")
getCsvFile(f"./data/engraveSlainType.csv")

getCsvFile(f"./prob/prob.csv")
getCsvFile(f"./probInfo.csv") #id연결용


#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■#

'''리포트생성'''
df_report = pd.DataFrame(columns=["guide_name", "result", "etc", "mean_error"])

def 리포트추출(guide_name, result, desc, mean_error = -1) :
    global df_report
    df_report = df_report.append({"guide_name": guide_name, "result": result, "etc": desc, "mean_error" : mean_error}, ignore_index=True)

    # DataFrame을 텍스트 파일로 내보내기
    df_report.to_csv(reportName, index=False, encoding="utf-8-sig")
    df_filtered = None





#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■#
'''확률정보 처리'''

info_name = "23년7월"#검증일자 시트명(확률 참조 정보가 들어있다.)
df_info = pd.read_excel("확률정보.xlsx",engine="openpyxl",sheet_name=info_name)

df_info = df_info.fillna(0)
df_info["web_no"] = df_info["web_no"].astype(int)
df_info["table_no"] = df_info["table_no"].astype(int)
df_info["arg_0"] = df_info["arg_0"].astype(int)
df_info["arg_1"] = df_info["arg_1"].astype(int)
df_info["prob_no"] = df_info["prob_no"].astype(int)
df_info["execute"] = df_info["execute"].astype(int)

#■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■#



# "확률가이드.xlsx"의 모든 시트를 df_guide에 저장
guide_file = "확률가이드.xlsx"#커뮤니티 내 확률 가이드
guide_file = "webProb.xlsx"#커뮤니티 내 확률 가이드
xls = pd.ExcelFile(guide_file)
df_guide = {}
for sheet_id in xls.sheet_names:
    df_guide[sheet_id] = xls.parse(sheet_id)

# 각 시트마다 어떤 함수를 실행하면서 시트명을 저장
for sheet_id, df_sheet in tqdm(df_guide.items()):
    # 여기에 원하는 함수를 실행하는 코드 작성
    # 시트명은 sheet_name 변수를 사용하여 참조할 수 있음
    #print("Processing sheet:", sheet_name)
    string = sheet_id

    # "_"를 기준으로 문자열 분리
    parts = string.split("_")
    web_no = int(parts[0])  # "940"
    table_no = int(parts[1])  # "0"

    # 값을 찾을 조건 설정
    condition = (df_info["web_no"] == web_no) & (df_info["table_no"] == table_no)



    try:

        # executeCheck = df_info.loc[condition, ["execute"]].values[0]
        # if executeCheck == 0 :
        #     continue

        sheet_name = df_info.loc[condition, ["guide_name"]].values[0][0]



        # 조건에 해당하는 행에서 "arg_0" 열의 값을 가져오기# 조건에 해당하는 행에서 "arg_0" 열과 "arg_1" 열의 값을 리스트로 저장할 변수 초기화
        execute_list = []
        arg_0_list = []
        arg_1_list = []
        prob_no_list = []
        ref_list = []

        #log_condition = None

        # 조건을 만족하는 행 추출 및 값 저장
        for index, row in df_info.loc[condition, ["execute","arg_0", "arg_1", "prob_no", "ref"]].iterrows():
            execute_list.append(row["execute"])
            arg_0_list.append(row["arg_0"])
            arg_1_list.append(row["arg_1"])
            prob_no_list.append(row["prob_no"])
            ref_list.append(row["ref"])


###◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇##
        '''반복'''
        #region
        for i in range(0, len(arg_0_list)):
            '''execute = 1인 행만 검사함'''
            executeCheck = execute_list[i]
            if executeCheck == 0 :
                continue


            '''진짜실행부'''
            # 개별적으로 처리할 작업 수행
            arg_0 = arg_0_list[i]
            arg_1 = arg_1_list[i]
            prob_no = prob_no_list[i]
            ref_list = ref_list[i]


            '''Flow

            df_sheet : 확률 가이드 중 현재 시트

            [1]df_log에서 해당 조건에 맞는 로그만 빼서 df_filtered로 저장
            [2]DATA CSV 파일에서 필요한 정보 가져와서 df_sheet 오른쪽 열에 붙임
            [3]확률 찾아서 df_sheet 오른쪽 열에 붙임
            [4]오차 계산해서 df_sheet 오른쪽 열에 붙임
            [5]리포트 기입(pass/fail/fail사유)
            [6]결과 파일 내보내기

            '''



            '''[1]########################################################################################'''
                
            if prob_no == 1 \
                or prob_no == 2 \
                or prob_no == 3 \
                :
                
                #로그 데이터에서 해당 조건에 맞는 로그만 임시 저장 > df_filtered
                log_condition = (df_log["probability_type"] == prob_no) & (df_log["item_no"] == arg_0) 

            elif prob_no == 14 \
                or prob_no == 16 \
                :

                log_condition = (df_log["probability_type"] == prob_no) & \
                            (df_log["item_no"] == arg_0) & \
                            (df_log["etc_json"].str.contains(f'"RedrawGroupNo":({arg_1}])'))

            elif prob_no == 15 \
                or prob_no == 17 \
                :

                log_condition = (df_log["probability_type"] == prob_no) & \
                            (df_log["item_no"] == arg_0) & \
                            (df_log["item_sub_no"] == arg_1)
                            #(df_log["etc_json"].str.contains(fr'"RedrawGroupNo":({arg_1}\})'))


           
            df_filtered = df_log.loc[log_condition]

            if df_filtered.empty : 
                print(f'확률정보내 arg에 맞는 로그가 없습니다.: {sheet_id}')
                리포트추출(sheet_name,"Fail",f'확률정보의 arg에 맞는 로그가 없습니다.(뽑기시스템 정보 isNotice = False 의심) : {sheet_id}')
                continue
                
                #print(df_filtered)
            '''[2]########################################################################################'''
                
            if prob_no == 1 \
                or prob_no == 2 \
                or prob_no == 3 \
                or prob_no == 14 \
                or prob_no == 15 \
                or prob_no == 16 \
                or prob_no == 17 \
                :
                
                # df_sheet의 길이만큼 반복하여 "이름" 열의 값과 일치하는 "mID" 값을 가져와서 리스트에 저장
                if ref_list == "tran":
                    id_values = [df_tran.loc[df_tran["mName"] == name, "mID"].values[0] for name in df_sheet["이름"]]
                elif ref_list == "serv":
                    id_values = [df_serv.loc[df_serv["mName"] == name, "mID"].values[0] for name in df_sheet["이름"]]
                elif ref_list == "item":
                    try: 
                        target_prob_colname = "이름"
                        df_sheet[target_prob_colname] = df_sheet[target_prob_colname].str.replace(" ", "")
                        id_values = [df_item.loc[df_item["mName"] == name, "mID"].values[0] for name in df_sheet[target_prob_colname]]
                    except :
                        target_prob_colname = "아이템 명"
                        df_sheet[target_prob_colname] = df_sheet[target_prob_colname].str.replace(" ", "")
                        id_values = [df_item.loc[df_item["mName"] == name, "mID"].values[0] for name in df_sheet[target_prob_colname]]
                # "ID" 열 추가
                df_sheet["ID"] = id_values


            '''[3]########################################################################################'''
                
            if prob_no == 1 \
                or prob_no == 2 \
                or prob_no == 3 \
                :
                
                
                try:
                    prob_values = [df_filtered.loc[df_filtered["result_item_no"] == id, "probability"].values[0] for id in df_sheet["ID"]]
                    df_sheet["인게임 확률(%)"] = prob_values
                except Exception as e:
                    print(f'확률가이드 내 아이템명과 실제 획득 아이템명이 다르거나, 가이드 표 연결이 잘못됐습니다. : {sheet_id} ({e})')
                    리포트추출(sheet_name,"Fail",f'확률가이드 내 아이템명과 실제 획득 아이템명이 다르거나, 가이드 표 연결이 잘못됐습니다. : {sheet_id} ({e})')
                    continue

            elif prob_no == 14 \
                or prob_no == 15 \
                or prob_no == 16 \
                or prob_no == 17 \
                :
                
                
                try:
                    prob_values = [df_filtered.loc[df_filtered["result_item_no"] == id, "probability"].values[0] if id != arg_0 else 0 for id in df_sheet["ID"]]
            
                    df_sheet["인게임 확률(%)"] = prob_values
                except Exception as e:
                    print(f'확률가이드 내 아이템명과 실제 획득 아이템명이 다르거나, 가이드 표 연결이 잘못됐습니다. : {sheet_id} ({e})')
                    리포트추출(sheet_name,"Fail",f'확률가이드 내 아이템명과 실제 획득 아이템명이 다르거나, 가이드 표 연결이 잘못됐습니다. : {sheet_id} ({e})')
                    continue




            '''[4]########################################################################################'''

            if prob_no == 1 \
                or prob_no == 2 \
                or prob_no == 3 \
                :
                # DataFrame에서 "확률"과 "인게임 확률(%)" 열을 가져옵니다.

                확률 = df_sheet["확률"]

            elif prob_no == 14 \
                or prob_no == 15 \
                or prob_no == 16 \
                or prob_no == 17 \
                :

                교체대상카드확률 = df_sheet.loc[df_sheet["ID"] == arg_0, "확률"].values[0]
                대상제외총확률 = df_sheet["확률"].sum() - 교체대상카드확률
                df_sheet['대상제외확률'] = round(df_sheet['확률']  * 100 / 대상제외총확률 ,4)
                df_sheet.loc[df_sheet["ID"] == arg_0, "대상제외확률"] = 0
                
                확률 = df_sheet["대상제외확률"]



            인게임_확률 = df_sheet["인게임 확률(%)"]

            # 오차를 계산하여 새로운 열 "오차(%)"을 추가합니다.
            오차 = (확률 - 인게임_확률) / 확률
            df_sheet["오차(%)"] = np.where(오차.isna(), np.nan, np.round(np.abs(오차) * 100,4))




            df_sheet = df_sheet.reset_index(drop=True)




            '''[5]########################################################################################'''

            result = ""
            etc = ""

            if prob_no == 1 \
                or prob_no == 2 \
                or prob_no == 3 \
                :

                if len(df_sheet) == len(df_filtered):
                    result = "Pass"
                else :
                    result = "Fail"

            #교체는 하나 차이
            elif prob_no == 14 \
                or prob_no == 15 \
                or prob_no == 16 \
                or prob_no == 17 \
                :
                
                if len(df_sheet) == len(df_filtered) + 1: 
                    result = "Pass"
                else :
                    result = "Fail"

            오차_평균 = df_sheet["오차(%)"].mean().round(4)
            리포트추출(sheet_name,result,etc,오차_평균)
            # #etc = f"Etc {i+1}"
            # df_report = df_report.append({"guide_name": guide_name, "result": result, "etc": etc}, ignore_index=True)

            # # DataFrame을 텍스트 파일로 내보내기
            # df_report.to_csv(reportName, index=False, encoding="utf-8-sig")
            # df_filtered = None

            '''[6]########################################################################################'''
            #outputName = f"{resultDir}/result.xlsx"
            # 엑셀 파일이 이미 존재하는지 확인
            try:
                # 기존 엑셀 파일 열기
                book = load_workbook(resultName)
                writer = pd.ExcelWriter(resultName, engine="openpyxl")
                writer.book = book

                # DataFrame을 기존 파일에 추가
                df_sheet.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()

            except FileNotFoundError:
                # 새로운 엑셀 파일 생성하여 DataFrame 저장
                df_sheet.to_excel(resultName, sheet_name=sheet_name, index=False)





        #endregion
###◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇##


    except IndexError as e: 
        if executeCheck == 0 :
                continue
        print(f'확률정보.xlsx에 등록되지 않은 고지표가 있습니다. : {sheet_id} ({e})')

