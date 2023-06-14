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

ingame_file = "R2MProbabilityTestHistory_20230613_20230614.csv"#인게임에서 추출한 확률 로그
df_log = pd.read_csv(ingame_file)


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

'''리포트생성'''
df_report = pd.DataFrame(columns=["guide_name", "result", "etc"])


# "확률가이드.xlsx"의 모든 시트를 df_guide에 저장
guide_file = "확률가이드.xlsx"#커뮤니티 내 확률 가이드
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
            1.df_log에서 해당 조건에 맞는 로그만 임시 저장 > df_filtered
            2.
            
            
            '''

            if prob_no == 1:


                #로그 데이터에서 해당 조건에 맞는 로그만 임시 저장 > df_filtered
                log_condition = (df_log["probability_type"] == prob_no) & (df_log["item_no"] == arg_0) 
                df_filtered = df_log.loc[log_condition]
                #print(df_filtered)

                
                # df_sheet의 길이만큼 반복하여 "이름" 열의 값과 일치하는 "mID" 값을 가져와서 리스트에 저장
                if ref_list == "tran":
                    id_values = [df_tran.loc[df_tran["mName"] == name, "mID"].values[0] for name in df_sheet["이름"]]
                elif ref_list == "serv":
                    id_values = [df_serv.loc[df_serv["mName"] == name, "mID"].values[0] for name in df_sheet["이름"]]
                elif ref_list == "item":
                    id_values = [df_item.loc[df_item["mName"] == name, "mID"].values[0] for name in df_sheet["이름"]]
                # "ID" 열 추가
                df_sheet["ID"] = id_values

                # 결과 출력
                #print(df_sheet)

                #result_condition = (df_log["result_item_no"] == prob_no) & (df_log["item_no"] == arg_0) 


                prob_values = [df_filtered.loc[df_filtered["result_item_no"] == id, "probability"].values[0] for id in df_sheet["ID"]]
                df_sheet["인게임 확률(%)"] = prob_values




                # DataFrame에서 "확률"과 "인게임 확률(%)" 열을 가져옵니다.
                확률 = df_sheet["확률"]
                인게임_확률 = df_sheet["인게임 확률(%)"]

                # 오차를 계산하여 새로운 열 "오차(%)"을 추가합니다.
                오차 = (확률 - 인게임_확률) / 확률
                df_sheet["오차(%)"] = np.where(오차.isna(), np.nan, np.round(np.abs(오차) * 100,4))






                df_sheet = df_sheet.reset_index(drop=True)




            '''파일 내보내기'''

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


            # 새로운 DataFrame 생성

            # 반복문을 통해 데이터 추가

            guide_name = f"{sheet_name}"
            result = ""
            etc = ""

            # "확률"과 "인게임 확률(%)"의 총합을 계산합니다.
            확률_총합 = 확률.sum()
            인게임_확률_총합 = 인게임_확률.sum()

            # "result" 열을 생성하고 조건에 따라 값을 설정합니다.
            try: 
                if 인게임_확률_총합 < 99.99999 :
                    result = "Fail"
                    etc = "고지표 내 항목 누락의심"
                # elif 인게임_확률_총합 < 99.99999 :
                #     result = "Fail"
                #     etc = "고지표 내 항목 누락의심"
                else :
                    result = "Pass"
            except:
                result = "Fail"
                etc = "알 수 없음"

            #etc = f"Etc {i+1}"
            df_report = df_report.append({"guide_name": guide_name, "result": result, "etc": etc}, ignore_index=True)

            # DataFrame을 텍스트 파일로 내보내기
            df_report.to_csv(reportName, index=False, encoding="utf-8-sig")




            df_filtered = None

        #endregion
###◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇◇##


    except IndexError as e: 
        if executeCheck == 0 :
                continue
        print(f'확률정보.xlsx에 등록되지 않은 고지표가 있습니다. : {sheet_id} ({e})')


# info_file = "probTarget.csv"

# # while not os.path.isfile(file_name) :
# #     try : 
# #         global df, df_target
# #         #file_name = input("확률테스트결과문서명 입력(.csv 제외) : ")
# #         file_name = "R2MProbabilityTestHistory_20230613_20230614"
# #         if file_name == "" :
# #             #file_name = "R2MProbabilityTestHistory_20221219_20230120.csv"#R2MProbabilityTestHistory_20230126_20230127
# #             file_name = "R2MProbabilityTestHistory_20230404_20230404.csv"#R2MProbabilityTestHistory_20230126_20230127
# #         else :
# #             file_name = f'{file_name}.csv'
# #         df = pd.read_csv(file_name)
# #         df_target = pd.read_csv(info_file)
# #         df_target = df_target.set_index("mType")
# #     except FileNotFoundError: 
# #         print("파일 없음...")
# #         #time.sleep(2)

# def getCsvFile(file_name):
#     global df_item
#     global df_tran
#     global df_serv
#     global df_skill
#     global df_engraveAbility
#     global df_engraveSlain
#     global df_prob
#     global df_probInfo

#     df_temp = pd.read_csv(file_name)
#     df_temp = df_temp.reset_index(drop=True)
#     df_temp = df_temp.set_index("mID")

#     if "item" in file_name :
#         df_item = df_temp.copy()
#     elif "transform" in file_name :
#         df_tran = df_temp.copy()
#     elif "servant" in file_name :
#         df_serv = df_temp.copy()
#     elif "skill" in file_name :
#         df_skill = df_temp.copy()
#     elif "engraveAbility" in file_name :
#         df_engraveAbility = df_temp.copy()
#     elif "engraveSlain" in file_name :
#         df_engraveSlain = df_temp.copy()
#     elif "probInfo" in file_name :
#         df_probInfo = df_temp.copy()
#         #df_probInfo = df_probInfo.astype({'0': 'int64', '1': 'int64'})

#     elif "prob" in file_name :
#         df_prob = df_temp.copy()

#     print(f"success, get csv file : {file_name}")


# getCsvFile(f"./data/item.csv")
# getCsvFile(f"./data/transform.csv")
# getCsvFile(f"./data/servant.csv")
# getCsvFile(f"./data/skillList.csv")
# getCsvFile(f"./data/engraveAbilityType.csv")
# getCsvFile(f"./data/engraveSlainType.csv")

# getCsvFile(f"./prob/prob.csv")
# getCsvFile(f"./probInfo.csv") #id연결용


# df_webProb_path = f"./webProb.xlsx"
# #df_webProb = pd.read_excel(df_webProb_path)

# def compare_prob2(refPage : str, df_before : pd.DataFrame, probID : int,  inOrder = False, targetColName = "이름", refColName = "확률" ,args = []):
#     """확률비교 by getWebProb.py,예외처리 A-2 : targetColName 변경 필요

#     Arg:
#         refPage : 확률고지표 시트명

#     """
    
    
#     sheet_name = f'{refPage}'#942_0
#     df_ref = pd.read_excel(df_webProb_path, sheet_name=sheet_name, engine="openpyxl")
#     #print (df_ref.columns.tolist())

#     #print(df_ref)
#     #print(df_before)
#     df_after = df_before.copy()
#     df_after = df_after.reset_index(drop=True)

#     if probID == 11 : #각인확률검사
#         df_ref = df_ref.replace('-','0')
#         df_ref = df_ref.replace('-','0')
#         #df_ref.iloc[2:, 4] = df_ref.iloc[2:, 4].astype(float)
#         #df_ref.iloc[2:, 7] = df_ref.iloc[2:, 7].astype(float)
#         #df_after.iloc[:, 7] = df_after.iloc[:, 7].astype(float)

#         for i in range(len(df_after)):
#             #print(df_after.loc[i,"probability_category"])
#             scrollType = int(df_after.loc[i,"item_sub_no"])#일반/축복각인
#             optionName = df_after.loc[i,"probability_category"]
#             slainName = df_after.loc[i,"mSlainTypeName"]
#             abilityName = df_after.loc[i,"mAbilityTypeName"]
#             statLevel = (df_after.loc[i,"mStatLevel"])

#             #print(f'{scrollType} {optionName} {slainName} {abilityName} {statLevel}')

#             expectedProb = 0
#             #try: 
#             if scrollType == 700:
#                 try : 
                    
#                     df_ref.iloc[2:, 4] = df_ref.iloc[2:, 4].astype(float)
#                     #df_ref.iloc[2:, 7] = df_ref.iloc[2:, 7].astype(float)
#                     df_after.iloc[:, 7] = df_after.iloc[:, 7].astype(float)
#                     expectedProb = df_ref.loc[(df_ref[0] == optionName)
#                                             &(df_ref[1] == slainName)
#                                             &(df_ref[2] == abilityName)
#                                             &(df_ref[4] == statLevel)
#                                             , 5].iloc[0]
#                 except : #방어구 확률 고지표 양식이 다름
#                     try : 
#                         df_ref.iloc[2:, 5] = df_ref.iloc[2:, 5].astype(float)
#                         #df_ref.iloc[2:, 7] = df_ref.iloc[2:, 7].astype(float)
#                         df_after.iloc[:, 7] = df_after.iloc[:, 7].astype(float)
#                         expectedProb = df_ref.loc[(df_ref[10] == optionName)
#                                                 &(df_ref[2] == slainName)
#                                                 &(df_ref[3] == abilityName)
#                                                 &(df_ref[5] == statLevel)
#                                                 , 6].iloc[0]
#                     except : 
#                         continue
#                 # expectedProb = df_ref.loc[(df_ref[0] == optionName)
#                 #                         , 5].iloc[0]
#             elif scrollType == 701:
#                 try : 
#                     #df_ref.iloc[2:, 4] = df_ref.iloc[2:, 4].astype(float)
#                     df_ref.iloc[2:, 7] = df_ref.iloc[2:, 7].astype(float)
#                     df_after.iloc[:, 7] = df_after.iloc[:, 7].astype(float)
#                     expectedProb = df_ref.loc[(df_ref[0] == optionName)
#                                             &(df_ref[1] == slainName)
#                                             &(df_ref[2] == abilityName)
#                                             &(df_ref[7] == statLevel)
#                                             , 8].iloc[0]
#                 except : #방어구 확률 고지표 양식이 다름
#                     try : 
#                         #df_ref.iloc[2:, 4] = df_ref.iloc[2:, 4].astype(float)
#                         df_ref.iloc[2:, 8] = df_ref.iloc[2:, 8].astype(float)
#                         df_after.iloc[:, 7] = df_after.iloc[:, 7].astype(float)
#                         expectedProb = df_ref.loc[(df_ref[10] == optionName)
#                                                 &(df_ref[2] == slainName)
#                                                 &(df_ref[3] == abilityName)
#                                                 &(df_ref[8] == statLevel)
#                                                 , 9].iloc[0]
#                     except : #전리품 고지표
#                         try : 
#                             #df_ref.iloc[2:, 4] = df_ref.iloc[2:, 4].astype(float)
#                             df_ref.iloc[1:, 5] = df_ref.iloc[1:, 5].astype(float)
#                             df_after.iloc[:, 7] = df_after.iloc[:, 7].astype(float)
#                             optionName = re.search(r'\d+단계', optionName).group()


#                             expectedProb = df_ref.loc[(df_ref[1] == optionName)
#                                                     &(df_ref[2] == slainName)
#                                                     &(df_ref[3] == abilityName)
#                                                     &(df_ref[5] == statLevel)
#                                                     , 6].iloc[0]
#                         except :
#                             continue
#             #except :
#             #    expectedProb = 0
#             #print(expectedProb)
            
#             try :
#                 df_after.loc[i,"mExpectedProb"] = float(expectedProb)
#             except Exception as e: 
#                 print(e)

#         #print(df_after[i])
#         try :
#             df_after["mExpectedProb"] = df_after["mExpectedProb"].replace('','0')
#             df_after["mExpectedProb"]=df_after["mExpectedProb"].astype(float)
#             df_after["probability"]=df_after["probability"].astype(float)
#             df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)
#         except Exception as e: 
#             print(e)

#         #print(df_after)

#     elif probID == 5 : #제작 확률참조 두개 열

#         for i in range(len(df_after)):
#             itemName = df_after.loc[i,"mName"]
#             getType = int(df_after.loc[i,"item_sub_no"])

#             if getType == 1 :
#                 refColName = "제작 성공 확률(%)"
#             elif getType == 2 :
#                 refColName = "대성공 확률(%)"
            

#             try : 
#                 basicProb =  df_ref.loc[df_ref[targetColName] == itemName, "제작 성공 확률(%)"].iloc[0]
#                 if basicProb == "-" :
#                     basicProb = 0
#                 expectedProb = df_ref.loc[df_ref[targetColName] == itemName, refColName].iloc[0]

#                 if getType == 2:
#                     expectedProb = float(expectedProb) * float(basicProb) * 0.01

#                 df_after.loc[i,"mExpectedProb"] = expectedProb
#             except IndexError:
#                 print(f'{probID}|{itemName}')
#                 emptyProbList.append(f'{probID}|{itemName}')
#                 df_after.loc[i,"mExpectedProb"] = -1
#                 #df_after.loc[i,"mProbDiff"] = ""
#         df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)


#     elif probID == 6 : #스킬 예외(확률표의 열 두개 > 한개로 합쳐야됨)

#         for i in range(len(df_after)):
#             #print(i)
#             skillName = df_after.loc[i,"mName"]
#             level = df_after.loc[i,"mLevel"]
#             levelAfter = f'{level} → {int(level)+1}'
#             prob = df_after.loc[i,"probability"]



#             # if "트리플" in skillName and "4 → 5" in levelAfter :
#             #     skillName = skillName.replace('트리플', "쿼드러플")

#             #print(skillName,level,prob)
#             try : 
#                 try :
#                     expectedProb = df_ref.loc[(df_ref["스킬 이름"] == skillName)&(df_ref["강화 단계"] == levelAfter), "확률"].iloc[0]
#                 except:
#                     skillName = skillName.replace('트리플', "쿼드러플")
#                     expectedProb = df_ref.loc[(df_ref["스킬 이름"] == skillName)&(df_ref["강화 단계"] == levelAfter), "확률"].iloc[0]

#                 df_after.loc[i,"mExpectedProb"] = expectedProb
#                 probDiff = round(abs(expectedProb - prob)/expectedProb*100,4)
#                 #print(skillName,level,prob,expectedProb,probDiff)
#                 df_after.loc[i,"mProbDiff"] = probDiff
#             except Exception as e:
#                 print(f'{e},{probID}|{skillName}')
#                 emptyProbList.append(f'{probID}|{skillName}')
#                 df_after.loc[i,"mExpectedProb"] = ""
#                 df_after.loc[i,"mProbDiff"] = ""
    
#     elif probID == 7 : #???

#         for i in range(len(df_after)):
#             beforeName = df_after.loc[i,"beforeName"]
#             afterName =  df_after.loc[i,"afterName"]

#             try:
#                 expectedProb = df_ref.loc[(df_ref["이름"] == beforeName)&(df_ref["교환결과"] == afterName), "확률"].iloc[0]

#                 df_after.loc[i,"mExpectedProb"] = expectedProb

#                 df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)
#             except IndexError:
#                 print(f'{probID}|{itemName}')
#                 emptyProbList.append(f'{probID}|{itemName}')
#                 df_after.loc[i,"mExpectedProb"] = ""
#                 df_after.loc[i,"mProbDiff"] = ""

#     elif probID == 8 or probID == 9: #강화 (일반, 포인트)

#         for i in range(len(df_after)):
#             beforeName = df_after.loc[i,"mName"]
#             name =  re.sub(r'\+\d+\s*', '', beforeName)
#             level = re.search(r'\d+', beforeName).group()
#             level = f'+{level} → +{int(level)+1}'

#             _refColName = "일반 확률(%)"
#             if probID == 9 :
#                 _refColName = "강화 포인트 사용 확률(%)"


#             try:
#                 expectedProb = df_ref.loc[(df_ref["이름"] == name)&(df_ref["강화 단계"] == level), _refColName].iloc[0]

#                 df_after.loc[i,"mExpectedProb"] = expectedProb
#                 df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)
            
#             except IndexError:
#                 print(f'{probID}|{itemName}')
#                 emptyProbList.append(f'{probID}|{itemName}')
#                 df_after.loc[i,"mExpectedProb"] = ""
#                 df_after.loc[i,"mProbDiff"] = ""

#     elif inOrder: ##검색없이 로그 순서대로 : 4

#         for i in range(len(df_after)):
#             #itemName = df_after.loc[i,"mName"]
#             expectedProb = df_ref.loc[i, '확률']
#             df_after.loc[i,"mExpectedProb"] = expectedProb
#             df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)

#     else : ## 원본의 mName 열만 필요.

#         for i in range(len(df_after)):
#             try : 
#                 try : 
#                     itemName = df_after.loc[i,"mName"]
#                 except :
#                     itemName = df_after.loc[i,"mResultName"]

#                 if probID == 14 or probID == 15: #교체 확률 환산용
#                     rootID = int(args)
#                     rootItemName = df_tran.loc[rootID,"mName"]
#                 elif probID == 16 or probID == 17 : #교체 확률 환산용
#                     rootID = int(args)
#                     rootItemName = df_serv.loc[rootID,"mName"]
#             except : 
#                 emptyLogList.append(f'{probID}|{itemName}')
#                 continue
            
            
#             if probID == 14 or probID == 15 or probID == 16 or probID == 17 : #교체 확률 환산용
#                 #print("1")
#                 rootProb = df_ref.loc[(df_ref['이름'] == rootItemName), '확률'].iloc[0]
#                 #print("1")
#                 #if refPage ==
#                 try: 
#                     df_ref.iloc[1:, 2] = df_ref.iloc[1:, 2].astype(float)
#                 except:
#                     try:
#                         df_ref.iloc[1:, 3] = df_ref.iloc[1:, 3].astype(float)
#                     except:
#                         print("do nothing")
#                         #df_ref.iloc[1:, 5] = df_ref.iloc[1:, 5].astype(float)

#                 #df_ref.iloc[1:, 4] = df_ref.iloc[1:, 4].astype(float)

#                 fixedTotalProb = df_ref['확률'].sum() - rootProb
#                 #print("1")
#                 #try:
#                 df_ref['확률'] = round(df_ref['확률']  * 100 / fixedTotalProb ,4)
#                 #except Exception as e:
#                 #    print(e)
#                 #    continue
#                 #print("1")

#             """
#             ※예외처리A
#             확률고지표에서 itemName을 못 찾을 경우, 
#             case 1: itemName이 없을 수 있음.
#             """
#             try :
#                 expectedProb = df_ref.loc[df_ref[targetColName] == itemName, refColName].iloc[0]
#                 #prob = 
#                 df_after.loc[i,"mExpectedProb"] = expectedProb
#                 #df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)
#                 #df_after.loc[i,"mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)
#             except Exception as e:
#                 print(e)
#                 errorStr = f'{probID=} {refPage=} {itemName=}'
#                 print(errorStr)
#                 emptyProbList.append(errorStr)
#                 df_after.loc[i,"mExpectedProb"] = -1
#                 #df_after.loc[i,"mProbDiff"] = #"=ABS(OFFSET($A$1,ROW()-1,COLUMN()-3)-OFFSET($A$1,ROW()-1,COLUMN()-2))/OFFSET($A$1,ROW()-1,COLUMN()-2)*100"

#                 continue

#             #중단점
#         df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)
        

#     del df_ref
#     gc.collect()


#     return df_after


# def makeCsv(outputName : str, title : str, df : pd.DataFrame):
#     """
#     확률 표 별로 상단에 title이 입력되도록 구분짓게 함.
#     \noutputName : 결과물 파일명
#     \ntitle : 표 상단 제목
#     \ndf : 해당 데이터 프레임
#     """
#     with open(outputName, mode='a', encoding='utf-8-sig', newline='') as f:
#         #if f.tell() != 0:
#         f.write(f'\n{title}\n')
#         df.to_csv(f, sep=',', index=False, header=True)

# def getWebID(target, mID = [int]):
#     """
    
#     target : probInfo 에서 찾을 값

#     mID : 입력 시, 행 고정(리스트)
    
#     """
#     gachaID = target
#     #print(gachaID)
#     if len(mID) == 0 : #전체에서 검색
#         colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
#         row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
#         title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
#         webID = f"{row}_{str(colNum).split('.')[0]}"
    
#     else : #해당 행에서 검색
#         webID = mID[0]
#         for id in mID :
#             #print(id)
#             try :
#                 colNum =  df_probInfo.columns[df_probInfo.loc[df_probInfo.index==id].eq(gachaID).any()][0]
#                 webID = f"{id}_{str(colNum).split('.')[0]}"
#             except :
#                 continue

#     return webID

# def check_gacha():#probtest 1
#     """뽑기
    
#     probTarget 입력 필요
#     """
#     startTime = time.time()

#     probID = 1

#     outputName = f"{resultDir}/뽑기.csv"
#     xlsxName = f"{resultDir}/뽑기.xlsx"

#     global df

#     curDf = df[df["probability_type"] == probID]
#     curDf = curDf.copy()
#     curDf['groupID'] = curDf['etc_json'].str.extract(r'(\d+)')
#     targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')
#     if not targetList[0].isnumeric() :
#         print("target is null... activate all test...")
        
#         #첫번째 숫자 추출
#         curDf['groupID'] = curDf.etc_json.str.extract(r'(\d+)')
#         #두번째 숫자 추출
#         #curDf['etc_json'] = curDf['etc_json'].str.extract(r'^\D*\d+\D+(\d+)')
        
        
#         df_temp = curDf.drop_duplicates(subset='etc_json')
#         df_temp = df_temp.drop_duplicates(subset='item_no')
#         targetList = df_temp['item_no'].astype('int')
#         groupList = df_temp['groupID'].astype('int')
#         del df_temp
#         gc.collect()

#     print("check_gacha...")

#     for target in tqdm(targetList) :

#         a = curDf[curDf["item_no"] == int(target)]
#         a = a.reset_index(drop=True)

#         a["mName"] =""
#         a["mTime"]=""

#         if len(a) == 0 :
#             emptyLogList.append(f'{probID}|{target}')

#         for i in range(len(a)):
#             before = a.loc[i,"result_item_no"]

#             targetType = int(a.loc[i,"probability_category"])
#             info_file = ""

#             #print("\nA1")
#             if targetType == 0 :
#                 df_temp = df_item.copy()
#                 info_file = "item"
#             elif targetType == 1:
#                 df_temp = df_tran.copy()
#                 info_file = "transform"
#             elif targetType == 2:
#                 df_temp = df_serv.copy()
#                 info_file = "servant"

#             try :
#                 after = df_temp.loc[before,"mName"]
#                 #print(after)
#                 a.loc[i,"mName"] = after

#             #카드 정렬용
#             #if targetType == 1 or targetType == 2 :
#                 rarity = df_temp.loc[before,"mRarity"]
#                 a.loc[i,"mRarity"] = rarity

#                 if targetType == 1 :
#                     tempGroupID = df_temp.loc[before,"order"]
#                     a.loc[i,"order"] = tempGroupID


#             except :
#                 emptyDataList.append('\n'+f"no data in {info_file}list ID:{before}|{after} ")
#                 a.loc[i,"mName"] = ""
#             a = a.sort_values(by=["mRarity","groupID","mRarity"])
#             #print("\nA2")

#             #시간표기용
#             a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
#             del df_temp
#             gc.collect()


#         b=a[["item_no","groupID","mName","test_result_count","probability"]].copy()
#         title = ""
#         try : 
#             gachaID = target
#             #print(gachaID)
#             colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
#             row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
#             title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
#             webID = f'{row}_{colNum}'
#             b=compare_prob2(webID,b,probID).copy()
#         except :
#             emptyProbList.append(f"{probID}|{target}|{title}|{row}|{colNum}")

#         # gachaID = int(target)
#         # #print(gachaID)
#         # colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
#         # row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
#         # title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
#         # webID = f'{row}_{colNum}'
#         # b=compare_prob2(webID,b).copy()

        
#         b.rename(columns={
#             'mTime':'수행시각'
#         ,'item_no':'뽑기ID'
#         ,'groupID':'그룹ID'
#         ,'mName':'아이템명'
#         ,'test_result_count':'뽑기횟수'
#         ,'probability':'뽑기확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)
#         #b.columns = ['수행시각','뽑기ID','아이템명','뽑기횟수','뽑기확률(%)','기대확률(%)','오차(%)']

#         # if not os.path.exists(outputName):

#         #     #b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         #     b.
#         # else:
#         #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
#         #totalResult = pd.concat([totalResult,pd.Series(name="")], ignore_index=True)
#         #totalResult = pd.concat([totalResult,b], ignore_index=True)

#         makeCsv(outputName, title, b)

#         sheetName = "gacha"
#         _mode = ''

#         if not os.path.exists(xlsxName):
#             _mode = 'w'
#         else:
#             _mode = 'a'

# #region 엑셀 시트 분리
#         # with pd.ExcelWriter(xlsxName, mode=_mode, engine='openpyxl') as writer:
#         #     print(_mode)
#         #     if writer.sheets:
#         #         startrow = writer.sheets[f'{sheetName}'].max_row
#         #     else:
#         #         startrow = 0
#         #     if startrow != 0:
#         #         startrow += 1
#         #     b.to_excel(writer, sheet_name=f'{sheetName}', startrow=startrow, index=False, header=True)
#         # # with pd.ExcelWriter(outputName, mode='a', engine='openpyxl') as writer:
#         # #     b.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
#         # #     writer.sheets['Sheet1'].column_dimensions['A'].width = 50 # 예시로 A열 너비 조정

#         #     # 빈 행 추가
#         #     writer.sheets[f'{sheetName}'].cell(row=startrow+2, column=1).value = ""

# #endregion

#         # with pd.ExcelWriter(outputName, mode='a', engine='openpyxl') as writer:
#         #     b.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
#         #     writer.sheets['Sheet1'].column_dimensions['A'].width = 50 # 예시로 A열 너비 조정



#         del a,b
#         gc.collect()


#     #del a
#     #gc.collect()
#         #print(f'success, target ID : {target}')


#     # totalResult.to_excel(xlsxName, # directory and file name to write

#     #         sheet_name = 'gacha', 

#     #         na_rep = 'NaN', 

#     #         float_format = "%.4f", 

#     #         header = True, 

#     #         #columns = ["group", "value_1", "value_2"], # if header is False

#     #         index = False, 

#     #         #index_label = "id", 

#     #         startrow = 0, 

#     #         startcol = 0, 

#     #         #engine = 'xlsxwriter', 

#     #         #freeze_panes = (2, 0)

#     #         ) 
#         #print(f'run-time : {time.time()-startTime:.4f} sec')
#     #print(f'{emptyDataList=}')



#     print(f'check_gacha() total-run-time : {time.time()-startTime:.4f} sec')

# def check_combine_card(type : int):#probtest 2,3 (type 2: 변신, 3: 서번트)
#     startTime = time.time()

#     probID = type

#     combineTypeName = ""
#     if type == 2 :
#         combineTypeName = "변신"
#     elif type == 3 :
#         combineTypeName = "서번트"

#     outputName = f"{resultDir}/{combineTypeName}교체.csv"
#     targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')

#     print("check_combine_card")
#     for target in tqdm(targetList) :
#         global df

#         a = df[df["probability_type"] == probID]
#         a = a[a["item_no"] == int(target)]
#         a = a.reset_index(drop=True)
#         #print(a)

#         a["mName"] =""
#         a["mRarity"] =""
#         a["mTime"]=""

#         for i in range(len(a)):
#             before = a.loc[i,"result_item_no"]

#             targetType = int(a.loc[i,"probability_category"])

#             if targetType == 1:
#                 df_temp = df_tran.copy()
#             elif targetType == 2:
#                 df_temp = df_serv.copy()

#             try : 
#                 after = df_temp.loc[before,"mName"]
#                 a.loc[i,"mName"] = after
#             except : 
#                 emptyDataList.append('\n'+f"no data in {combineTypeName}list ID:{before} ")
#                 a.loc[i,"mName"] = ""
#                 continue

#             #카드 정렬용
#             if targetType == 1 or targetType == 2 :
#                 rarity = df_temp.loc[before,"mRarity"]
#                 a.loc[i,"mRarity"] = rarity

#             a = a.sort_values(by=["mRarity","result_item_no"])

#             #시간표기용
#             a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
#             del df_temp
#             gc.collect()


#         b=a[["mName","test_result_count","probability"]]


#         if type == 2 :
#             b= compare_prob2(f"942_{target}",b,probID).copy()
#             #combineTypeName = "변신"
#         elif type == 3 :
#             b= compare_prob2(f"950_{target}",b,probID).copy()
#             #combineTypeName = "서번트"

#         # try : 
#         #     gachaID = int(target)
#         #     #print(gachaID)
#         #     colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
#         #     row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
#         #     title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
#         #     webID = f'{row}_{colNum}'
#         #     b=compare_prob2(webID,b).copy()
#         # except :
#         #    emptyProbList.append(f"{probID}|{target}|{title}|{row}|{colNum}")
        
#         #인덱스 > 합성종류 표기
#         # b= b.replace({"item_no":0},"일반합성")
#         # b= b.replace({'item_no':1},"고급합성")
#         # b= b.replace({'item_no':2},"희귀합성")
#         # b= b.replace({'item_no':3},"영웅합성")
#         # b= b.replace({'item_no':4},"전설합성")

#         title = ""
#         targetRarity = int(a.loc[0,"item_no"])
#         if targetRarity == 0 :
#             title = "일반 교체"
#         elif targetRarity == 1 :
#             title = "고급 교체"
#         elif targetRarity == 2 :
#             title = "희귀 교체"
#         elif targetRarity == 3 :
#             title = "영웅 교체"
#         elif targetRarity == 4 :
#             title = "전설 교체"


#         b.rename(columns={
#             'mTime':'수행시각'
#         ,'item_no':'합성종류'
#         ,'mName':'아이템명'
#         ,'test_result_count':'뽑기횟수'
#         ,'probability':'뽑기확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)

#         # if not os.path.exists(outputName):

#         #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         # else:
#         #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
            

#         makeCsv(outputName,title,b)
#         del a,b
#         gc.collect()

#         #print(f'success, target ID : {target}')


#         #print(f'run-time : {time.time()-startTime:.4f} sec')
#     print(f'check_gacha() total-run-time : {time.time()-startTime:.4f} sec')

# def check_combine_mat():#probtest 4
#     startTime = time.time()

#     probID = 4

#     outputName = f"{resultDir}/매터리얼합성.csv"

#     global df

#     a = df[df["probability_type"] == 4]
#     a = a[a["result_item_no"] == 1] #합성성공:1, 합성실패:0
#     a = a.reset_index(drop=True)

#     a["mName"] =""

#     for i in tqdm(range(len(a))):

#         before = a.loc[i,"item_no"]

#         after = df_item.loc[before,"mName"]
#         a.loc[i,"mName"] = after

#         a = a.sort_values(by=["item_no"])   


#     b= compare_prob2("958_0",a,probID,True).copy()


#     b=b[["mName","test_result_count","probability","mExpectedProb","mProbDiff"]]
#     #b=a[["mTime","mName","test_result_count","probability"]]
#     b.rename(columns={
#     #,'item_no':'합성등급'
#     'mName':'합성대상'
#     ,'test_result_count':'합성성공횟수'
#     ,'probability':'합성성공확률(%)'
#     ,'mExpectedProb':'기대확률(%)'
#     ,'mProbDiff':'오차(%)'
#     }, inplace = True)

#     # title = ""
#     # rarity = int(rarity)
#     # if rarity == 0 :
#     #     title = "일반 교체"
#     # elif rarity == 1 :
#     #     title = "고급 교체"
#     # elif rarity == 2 :
#     #     title = "희귀 교체"
#     # elif rarity == 3 :
#     #     title = "영웅 교체"
#     # elif rarity == 4 :
#     #     title = "전설 교체"

#     # if not os.path.exists(outputName):
#     #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#     # else:
#     #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    
#     makeCsv(outputName,"noname",b)

#     del a,b
#     gc.collect()

#     print(f'check_combine_mat() total-run-time : {time.time()-startTime:.4f} sec')

# def check_craft():#probtest 5
#     """제작확률
    
#     타겟 리스트 : 전체로그에서 뽑아옴, 별도 입력 필요 없음
    
#     """
#     startTime = time.time()
#     probID = 5

#     outputName = f"{resultDir}/제작.csv"

#     #targetList = str(df_target.loc[5,"mArg0"]).split(sep=';')
#     global df
#     targetTemp = df[df["probability_type"] == 5]#.drop_duplicates(subset='result_item_no')

#     #targetList = set(df.loc[df["probability_type"] == 5,'result_item_no'].drop_duplicates(subset='etc_json').to_list())
#     targetList = targetTemp['result_item_no'].drop_duplicates().to_list()

#     del targetTemp
#     gc.collect()

#         #df_temp = curDf.drop_duplicates(subset='etc_json')

#     #print(targetList)

#     print("***check_craft")

#     curDf = df[df["probability_type"] == 5]

#     for target in tqdm(targetList) :

#         #print(f'try target ID : {target}')
#         a = curDf[curDf["result_item_no"] == int(target)]
#         #a = a[a["item_sub_no"] == target] #합성성공:1, 합성실패:0
#         #print(a)

#         a = a.sort_values(by=["item_sub_no"],ascending=False)
#         a = a.reset_index(drop=True)
        
#         #print(a)

#         a["mName"]=""
#         #a["mTime"]=""
#         a["mCraftType"]=""
#         a["mRarity"]=""
#         #a["mSuccessCount"]=""
#         #a["mSuccessRate"]=""
#         #a["mGreatSuccessCount"]=""
#         #a["mGreatSuccessRate"]=""

#         #greatSuccessCountIndex = -1
#         #successCountIndex = -1
#         greatSuccessCount = 0
#         successCount = 0
#         for i in range(len(a)):
#             mCraftType = a.loc[i,"item_sub_no"]

#             if mCraftType == 0 :
#                 a = a.drop(a.index[i])
#                 continue #실패는 제외

#             before = a.loc[i,"result_item_no"]
#             #before1 = a.loc[i,"result_item_no"]

#             try: 
#                 after = df_item.loc[before,"mName"]
#                 after1 = df_item.loc[before,"mRarity"]
#                 a.loc[i,"mName"] = after
#                 a.loc[i,"mRarity"] = after1
#             except : 
#                 emptyDataList.append('\n'+f"no data in item list ID:{before} ")
#                 a.loc[i,"mName"] = before
#                 a.loc[i,"mRarity"] = ""
#                 continue
#             #a = a.sort_values(by=["item_no"])   


#             if mCraftType == 2 :
#                 greatSuccessCount = int(a.loc[i,"test_result_count"])
#             elif mCraftType == 1 :
#                 successCount = int(a.loc[i,"test_result_count"]) + greatSuccessCount
#                 a.loc[i,"test_result_count"] = successCount

#         #print(a)
#         #전체 확률 표기
#         a["mProb"]=""
#         for i in range(len(a)):
#             tempProb0 = float(a.loc[i,"test_result_count"])*0.0001
#             #tempProb1 = float(b.loc[i,"mGreatSuccessCount"])*0.001
#             a.loc[i,"mProb"] = f"{tempProb0:.4f}"
#             #b.loc[i,"mGreatSuccessRate"] = f"{tempProb1:.4f}"
#         #print(a)
#         b = compare_prob2("975_0",a,probID,False,targetColName="아이템 이름",refColName="제작 성공 확률(%)")
#         #b= compare_prob(probID,a).copy()

#         #b=a[["mTime","mName","probability","mSuccessRate","mGreatSuccessCount","mGreatSuccessRate"]]
#         b = b.reset_index(drop=True)

#         #print(b)
#         #print("B")
#         b=b[["mName","item_sub_no","test_result_count","mProb","mExpectedProb","mProbDiff"]]

#         b= b.replace({"item_sub_no":1},"일반성공")
#         b= b.replace({"item_sub_no":2},"대성공")

            
#         b.rename(columns={
#             'mTime':'수행시각'
#         #,'item_no':'합성등급'
#         ,'mName':'아이템명'
#         ,'item_sub_no':'성공타입'
#         ,'test_result_count':'성공횟수'
#         ,'mProb':'성공확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)

#         if not os.path.exists(outputName):
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         else:
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

#         del a, b
#         gc.collect()
#     del curDf
#     gc.collect()

#     print(f'check_craft() total-run-time : {time.time()-startTime:.4f} sec')

# def check_skill():#probtest 6 (인자 불필요)
#     """스킬강화 확률
    
#     Target:
#         probTarget.csv 입력 불필요

#     ProbInfo:
#         probInfo.csv 입력 불필요
#     """
#     startTime = time.time()

#     probID = 6

#     outputName = f"{resultDir}/스킬강화.csv"

#     global df

#     a = df[df["probability_type"] == probID]
#     a = a[a["result_item_no"] == 1]
#     a = a.reset_index(drop=True)

#     a["mName"]=""
#     a["mLevel"]=""
#     a["mSuccessCount"]=""
#     a["mSuccessRate"]=""
#     a["order"]=0


#     for i in range(len(a)):

#         try :
#             before = a.loc[i,"item_no"]
#             level = df_skill.loc[before,"level"]
#             skillName = df_skill.loc[before,"skillName"]
#             order = df_skill.loc[before,"order"]
#             a.loc[i,"mLevel"] = level
#             a.loc[i,"mName"] = skillName
#             a.loc[i,"order"] = int(order)
#         except :
#             print("no ID")
            
#     b=a[["order","mName","mLevel","test_result_count","probability"]]
#     b = b.reset_index(drop=True)
    
#     b = b.sort_values(by=["order"])

#     b=compare_prob2("1283_0",b,probID)

#     b=b[["mName","mLevel","test_result_count","probability","mExpectedProb","mProbDiff"]]

#     b.rename(columns={
#         'mTime':'수행시각'
#     ,'item_no':'스킬ID'
#     ,'mName':'강화대상'
#     ,'mLevel':'강화대상레벨'
#     ,'test_result_count':'강화성공횟수'
#     ,'probability':'강화성공확률(%)'
#     ,'mExpectedProb':'기대확률(%)'
#     ,'mProbDiff':'오차(%)'
#     }, inplace = True)

#     makeCsv(outputName,"스킬강화",b)

#     del a,b
#     gc.collect()

#     print(f'check_craft() total-run-time : {time.time()-startTime:.4f} sec')

# def check_change_mat():#probtest 7
#     """매테교체
    
#     probInfo 입력 불필요
#     probTarget 입력 필요
#     """
    
#     startTime = time.time()
#     probID = 7

#     outputName = f"{resultDir}/매터리얼교환.csv"
#     #gachaID = input("변신 뽑기 ID 입력 > ")
#     #print(df_target.loc[1,"mArg0"])
#     targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')

#     #c=pd.DataFrame(columns=["mTime","item_no","mRarity","mName","test_result_count"])
    
#     for target in targetList :
#         eachStartTime = time.time()
        
#         global df
#         #print(f'try target ID : {target}')

#         a = df[df["probability_type"] == probID]
#         #print(a)
#         a = a[a["item_no"] == int(target)]
#         a = a.head(4)
#         a = a.reset_index(drop=True)

#         a["beforeName"] =""
#         a["afterName"] =""
#         a["mRarity"]=""

#         for i in range(len(a)):
#             before0 = a.loc[i,"item_no"]
#             before1 = a.loc[i,"result_item_no"]

#             after0 = df_item.loc[before0,"mName"]
#             after1 = df_item.loc[before1,"mName"]

#             #a.loc[i,"mName"] = f'{after0}>{after1}'
#             a.loc[i,"beforeName"] = after0
#             a.loc[i,"afterName"] = after1

#             # #정렬
#             rarity = df_item.loc[before0,"mRarity"]
#             a.loc[i,"mRarity"] = rarity
#             # a = a.sort_values(by=["mRarity","result_item_no"])

#             #시간표기용
#             #a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            

#         b=a[["item_no","mRarity","beforeName","afterName","test_result_count","probability"]]
#        # b=a[["mTime","item_no","mRarity","mName","test_result_count","probability","mExpectedProb","mProbDiff"]]
#         #b["mProb"]=""
#         # for i in range(len(b)):
#         #     tempProb = float(b.loc[i,"test_result_count"])*0.001
#         #     b.loc[i,"mProb"] = f"{tempProb:.4f}"
#         #b = compare_prob(probID,b)

#         #webID = getWebID(rarity, [957])
#         b = compare_prob2(f'957_{rarity}',b,probID)
#         b=b[["beforeName","afterName","test_result_count","probability","mExpectedProb","mProbDiff"]]
            
#         b.rename(columns={
#             'mTime':'수행시각'
#         ,'item_no':'매터리얼교환내용'
#         #,'mName':'아이템명'
#         ,'test_result_count':'뽑기횟수'
#         ,'probability':'뽑기확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)
    

#         title = ""
#         rarity = int(rarity)
#         if rarity == 0 :
#             title = "일반 교체"
#         elif rarity == 1 :
#             title = "고급 교체"
#         elif rarity == 2 :
#             title = "희귀 교체"
#         elif rarity == 3 :
#             title = "영웅 교체"
#         elif rarity == 4 :
#             title = "전설 교체"
#         elif rarity == 5 :
#             title = "초월 교체"


#         makeCsv(outputName,title,b)
        

#         del a
#         gc.collect()

#         #print(f'success, target ID : {target}')


#         #print(f'run-time : {time.time()-eachStartTime:.4f} sec')

#     # print(c)
#     # c = c.sort_values(by=["mRarity","item_no"])

#     # if not os.path.exists(outputName):

#     #     c.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#     # else:
#     #     c.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        
#     # del c
#     # gc.collect()
    
#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_reinforce_item():
#     """아이템 강화(전리품 강화 2023-04-05)

#     probTarget 입력 불필요
#     probInfo 입력 불필요 : 961_0 고정

#     """
#     startTime = time.time()

#     probID = 8

#     outputName = f"{resultDir}/아이템강화(포인트미사용).csv"

#     global df

#     a = df[df["probability_type"] == probID]
#     a = a[(a["result_item_no"]-a["item_sub_no"] == 1)]
#     #a = a[a["item_sub_no"] == target] #합성성공:1, 합성실패:0
#     a = a.reset_index(drop=True)
#     #print(a)

#     a["mName"]=""
#     a["mTime"]=""
#     a["mSuccessCount"]=""
#     a["mSuccessRate"]=""
#     a["mOrder"]=0

#     for i in range(len(a)):

#         try :
#             before = a.loc[i,"item_no"]
#             after = df_item.loc[before,"mName"]
#             a.loc[i,"mName"] = after
#         except :
#             print("no ID")


#         #시간표기용
#         a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
#     b=a[["mTime","item_no","mName","test_result_count","probability"]]
#     b = b.reset_index(drop=True)

#     b = compare_prob2("961_0",b,probID)

#     #b = compare_prob(probID,b)
#     b=b[["mName","test_result_count","probability",'mExpectedProb','mProbDiff']]

#     b.rename(columns={
#     'mTime':'수행시각'
#     #,'item_no':'아이템ID'
#     ,'mName':'강화대상'
#     ,'test_result_count':'강화성공횟수'
#     ,'probability':'강화성공확률(%)'
#     ,'mExpectedProb':'기대확률(%)'
#     ,'mProbDiff':'오차(%)'
#     }, inplace = True)


#     if not os.path.exists(outputName):
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#     else:
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

#     del a,b
#     gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_reinforce_item_point():#probtest 9 (인자 불필요)
#     startTime = time.time()

#     probID = 9

#     outputName = f"{resultDir}/아이템강화(포인트사용).csv"

#     global df

#     a = df[df["probability_type"] == probID]
#     a = a[(a["result_item_no"]-a["item_sub_no"] == 1)]
#     #a = a[a["item_sub_no"] == target] #합성성공:1, 합성실패:0
#     a = a.reset_index(drop=True)
#     #print(a)

#     a["mName"]=""
#     a["mTime"]=""
#     a["mSuccessCount"]=""
#     #a["mSuccessRate"]=""
#     a["mOrder"]=0

#     for i in range(len(a)):

#         try :
#             before = a.loc[i,"item_no"]
#             after = df_item.loc[before,"mName"]
#             a.loc[i,"mName"] = after
#         except :
#             print("no ID")


#         #시간표기용
#         a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
#     b=a[["mTime","item_no","mName","test_result_count","probability"]]
#     b = b.reset_index(drop=True)

#     b = compare_prob2("961_0",b,probID)

#     b=b[["mName","test_result_count","probability",'mExpectedProb','mProbDiff']]
#     b.rename(columns={
#     'mTime':'수행시각'
#     #,'item_no':'아이템ID'
#     ,'mName':'강화대상'
#     ,'test_result_count':'강화성공횟수'
#     ,'probability':'강화성공확률(%)'
#     ,'mExpectedProb':'기대확률(%)'
#     ,'mProbDiff':'오차(%)'
#     }, inplace = True)

#     if not os.path.exists(outputName):
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#     else:
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

#     del a,b
#     gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_soul():#probtest 10 (인자 불필요)
#     """영혼부여
    
#     probTarget 입력 불필요
#     """
#     startTime = time.time()

#     probID = 10

#     outputName = f"{resultDir}/영혼부여.csv"

#     global df

#     a = df[(df["probability_type"] == probID) & (df["result_item_no"] == 1)]
#     #a = a[a["result_item_no"] == 1]
#     #a = a[a["item_sub_no"] == target] #합성성공:1, 합성실패:0
#     a = a.reset_index(drop=True)
#     #print(a)

#     a["mItemName"]=""
#     a["mScrollName"]=""
#     a["mTime"]=""
#     a["mSuccessCount"]=""
#     a["mRarity"]=""
#     #a["mSuccessRate"]=""

#     for i in range(len(a)):

#         try :
#             before0 = a.loc[i,"item_no"]
#             before1 = a.loc[i,"item_sub_no"]
            
#             after0 = df_item.loc[before0,"mName"]
#             after1 = df_item.loc[before1,"mName"]
#             rarity = df_item.loc[before0,"mRarity"]

#             a.loc[i,"mItemName"] = after0
#             a.loc[i,"mScrollName"] = after1
#             a.loc[i,"mRarity"] = rarity
#         except :
#             print("no ID")


#         #시간표기용
#         a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
#     b=a[["mTime","item_no","item_sub_no","mRarity","mItemName","mScrollName","test_result_count","probability"]]
#     b = b.reset_index(drop=True)

#     #b=compare_prob(probID,b)

#     b.rename(columns={
#     'mTime':'수행시각'
#     #,'item_no':'아이템ID'
#     ,'mItemName':'영혼부여대상무기'
#     ,'mScrollName':'영혼석명'
#     ,'test_result_count':'영혼부여성공횟수'
#     ,'probability':'영혼부여성공확률(%)'
#     ,'mExpectedProb':'기대확률(%)'
#     ,'mProbDiff':'오차(%)'
#     }, inplace = True)

#     if not os.path.exists(outputName):
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#     else:
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

#     del a,b
#     gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_spot_tran():#probtest 12 (인자 불필요)
#     startTime = time.time()

#     probID = 12

#     outputName = f"{resultDir}/변신성장.csv"

#     global df

#     a = df[(df["probability_type"] == probID)&(df["result_item_no"] == 1)]
#     a = a.reset_index(drop=True)

#     a["mTime"]=""
#     a["mSuccessCount"]=""
#     #a["mSuccessRate"]=""

#     for i in range(len(a)):

#         # try :
#         #     before0 = a.loc[i,"item_no"]
#         #     before1 = a.loc[i,"item_sub_no"]
#         #     after0 = df_item.loc[before0,"mName"]
#         #     after1 = df_item.loc[before1,"mName"]
#         #     a.loc[i,"mItemName"] = after0
#         #     a.loc[i,"mScrollName"] = after1
#         # except :
#         #     print("no ID")


#         #시간표기용
#         a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
#     b=a[["mTime","probability_category","item_no","test_result_count","probability"]]
#     b = b.sort_values(by=["probability_category","item_no"])
#     b = b.reset_index(drop=True)
    
#     #b = compare_prob(probID,b)


#     b= b.replace({"probability_category":1},"유게네스의 휘장")
#     b= b.replace({"probability_category":2},"벨제뷔트의 휘장")
#     b= b.replace({"probability_category":3},"헤라켄의 휘장")
#     b= b.replace({"probability_category":4},"가이아스의 휘장")
#     b= b.replace({"probability_category":5},"유피테르의 휘장")
#     #전체 확률 표기
#     # for i in range(len(b)):
#     #     tempProb0 = float(b.loc[i,"test_result_count"])*0.001
#     #     b.loc[i,"mSuccessRate"] = f"{tempProb0:.4f}"
    

#     b.rename(columns={
#     'mTime':'수행시각'
#     ,'item_no':'강화성공횟수'
#     ,'probability_category':'휘장명'
#     ,'item_no':'강화대상단계'
#     ,'probability':'강화성공확률(%)'
#     ,'mExpectedProb':'기대확률(%)'
#     ,'mProbDiff':'오차(%)'
#     }, inplace = True)

#     if not os.path.exists(outputName):
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#     else:
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

#     del a,b
#     gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_spot_serv():#probtest 13 (인자 불필요)
#     startTime = time.time()

#     probID = 13

#     outputName = f"{resultDir}/서번트성장.csv"

#     global df

#     a = df[(df["probability_type"] == probID)&(df["result_item_no"] == 1)]
#     a = a.reset_index(drop=True)

#     a["mTime"]=""
#     a["mSuccessCount"]=""
#     #a["mSuccessRate"]=""

#     for i in range(len(a)):

#         #시간표기용
#         a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
#     b=a[["mTime","probability_category","item_no","test_result_count","probability"]]
#     b = b.sort_values(by=["probability_category","item_no"])
#     b = b.reset_index(drop=True)

#     #b = compare_prob(probID,b)

#     b= b.replace({"probability_category":1},"유게네스의 휘장")
#     b= b.replace({"probability_category":2},"벨제뷔트의 휘장")
#     b= b.replace({"probability_category":3},"헤라켄의 휘장")
#     b= b.replace({"probability_category":4},"가이아스의 휘장")
#     b= b.replace({"probability_category":5},"유피테르의 휘장")
#     #전체 확률 표기
#     # for i in range(len(b)):
#     #     tempProb0 = float(b.loc[i,"test_result_count"])*0.001
#     #     b.loc[i,"mSuccessRate"] = f"{tempProb0:.4f}"
    

#     b.rename(columns={
#     'mTime':'수행시각'
#     ,'item_no':'강화성공횟수'
#     ,'probability_category':'휘장명'
#     ,'item_no':'강화대상단계'
#     ,'probability':'뽑기확률(%)'
#     ,'mExpectedProb':'기대확률(%)'
#     ,'mProbDiff':'오차(%)'
#     }, inplace = True)

#     if not os.path.exists(outputName):
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#     else:
#         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

#     del a,b
#     gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_redraw_gacha(probID : int):#probtest 14,16 (인자 2 필요)
#     """교체(뽑기로 획득)
    
#     probID 14=변신, 16=서번트
#     """
#     startTime = time.time()

#     probName = ""
#     if probID == 14:
#         probName = "변신"
#     elif probID == 16:
#         probName = "서번트"

#     outputName = f"{resultDir}/{probName}교체(뽑기).csv"

#     targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')

#     for target in tqdm(targetList) :
#         cardID, redrawGroupNo    = target.split(sep='|')
#         #print(f'try extract target... [cardID:{cardID}, redrawGroupNo:{redrawGroupNo}]')
#         #print(probTestNo,cardID, redrawGroupNo)

#         global df
#         a = df[(df["probability_type"] == probID)&(df["item_no"] == int(cardID))]
#         a = a.reset_index(drop=True)
#         #print(a)

#         a["mOriginName"]=""
#         a["mResultName"]=""
#         a["mRedrawGroupNo"]=""
#         a["mGroupID"]=""

#         for i in range(len(a)):

#             #etc_json에서 추출
#             tempStr = a.loc[i,"etc_json"]
#             tempGet0 = re.search('RedrawGroupNo":(.+?)}', tempStr).group(1)
#             a.loc[i,"mRedrawGroupNo"] = tempGet0

#         a = a[(a["mRedrawGroupNo"] == redrawGroupNo)]
#         a = a.reset_index(drop=True)

#         if len(a) == 0 :
#             print(f'no data... {cardID}|{redrawGroupNo}')
#             emptyLogList.append(f'{cardID}|{redrawGroupNo}')
#             continue

#         for i in range(len(a)):
#             if probID == 14 :
#                 df_redraw = df_tran.copy()
#             else :
#                 df_redraw = df_serv.copy()
            
#             #try:
#                 #카드명 적용

#             try : 
#                 before0 = a.loc[i,"item_no"]
#                 before1 = a.loc[i,"result_item_no"]
#                 after0 = df_redraw.loc[before0,"mName"]
#                 after1 = df_redraw.loc[before1,"mName"]
#                 a.loc[i,"mOriginName"] = after0
#                 a.loc[i,"mName"] = after1

#                 #카드 정렬용
#                 rarity = df_redraw.loc[before1,"mRarity"]
#                 a.loc[i,"mRarity"] = rarity
#                 a = a.sort_values(by=["mRarity","result_item_no"])

#                 if probID == 14:
#                     tempGroupID = df_redraw.loc[before1,"order"]
#                     a.loc[i,"mGroupID"] = tempGroupID

#                 a = a.sort_values(by=["mRarity","mGroupID","mRarity"])

#             except :
#                 emptyDataList.append('\n'+f"no data in {probName}list ID:{before1} ")
#                 a.loc[i,"mName"] = ""

#         b=a[["mOriginName","mRedrawGroupNo","mName","test_result_count","probability"]]
#         b = b.reset_index(drop=True)

#         #webID = 0 
#         if probID == 14 :
#             rowID = [943,942]
            
#         elif probID == 16:
#             rowID = [951,950]
#         webID = getWebID(target, rowID)
#         b = compare_prob2(webID, b, probID, args = cardID)

#         #b = compare_prob(probID, b, redrawGroupNo, after0)
#         b.rename(columns={
#         'mTime':'수행시각'
#         #,'item_no':'아이템ID'
#         ,'mOriginName':'교체대상카드명'
#         ,'mRedrawGroupNo':'교체그룹ID'
#         ,'mName':'교체된 카드명'
#         ,'test_result_count':'뽑기횟수'
#         ,'probability':'뽑기확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)


#         # if not os.path.exists(outputName):
#         #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         # else:
#         #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        
        
#         makeCsv(outputName,target,b)

#         del a,b
#         gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_redraw_combine(probID):#probtest 15, 17 (인자 2 필요)
#     startTime = time.time()

#     #probID = 15
#     if probID == 15:
#         probName = "변신"
#     elif probID == 17:
#         probName = "서번트"


#     #outputName = f"{resultDir}/변신교체(합성획득)_{time.strftime('%y%m%d_%H%M%S')}.csv"
#     outputName = f"{resultDir}/{probName}교체(교체).csv"

#     targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')
#     #targetList = targetList_before.split(sep='|')

#     for target in tqdm(targetList) :
#         cardID, rarity = target.split(sep='|')
#         #print(f'try extract target... [cardID:{cardID}, rarity:{rarity}]')
#         #print(probTestNo,cardID, redrawGroupNo)

#         global df
#         a = df[(df["probability_type"] == probID)&(df["item_no"] == int(cardID))&(df["item_sub_no"] == int(rarity))]
#         a = a.reset_index(drop=True)
#         #print(a)

#         #a["mTime"]=""
#         a["mOriginRarity"]=""
#         a["mOriginName"]=""
#         a["mResultName"]=""

#         if len(a) == 0 :
#             print(f'no data... {cardID}|{rarity}')

#         for i in range(len(a)):
#             try:
#                 if probID == 15 :
#                     df_redraw = df_tran.copy()
#                 else :
#                     df_redraw = df_serv.copy()
#                 #카드명 적용
#                 before0 = a.loc[i,"item_no"]
#                 before1 = a.loc[i,"result_item_no"]
#                 after0 = df_redraw.loc[before0,"mName"]
#                 after1 = df_redraw.loc[before1,"mName"]
#                 a.loc[i,"mOriginName"] = after0
#                 a.loc[i,"mResultName"] = after1

#                 #카드 정렬용
#                 tempRarity = df_redraw.loc[before1,"mRarity"]
#                 a.loc[i,"mRarity"] = tempRarity
#                 a = a.sort_values(by=["mRarity","result_item_no"])

#             except :
#                 print(f"data 업데이트 요망... Type:변신,ID:{before0}or{before1} 누락")
#                 a.loc[i,"mOriginName"] = "BLANK"
#                 a.loc[i,"mResultName"] = "BLANK"

#             #시간표기용
#             #a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
#         b=a[["mOriginName","mResultName","test_result_count","probability"]]
#         b = b.reset_index(drop=True)
#         #print(b)

#         if probID == 15 :
#             rowID = [943]
            
#         elif probID == 17:
#             rowID = [951]
#         webID = getWebID(target, rowID)
#         b = compare_prob2(webID, b, probID,args = cardID)

        
#         # b= b.replace({"item_sub_no":2},"희귀합성")
#         # b= b.replace({"item_sub_no":3},"영웅합성")
#         # b= b.replace({"item_sub_no":4},"전설합성")

#         # title = ""
#         # rarity = int(rarity)
#         # if rarity == 0 :
#         #     title = "일반 교체"
#         # elif rarity == 1 :
#         #     title = "고급 교체"
#         # elif rarity == 2 :
#         #     title = "희귀 교체"
#         # elif rarity == 3 :
#         #     title = "영웅 교체"
#         # elif rarity == 4 :
#         #     title = "전설 교체"

        
#         b.rename(columns={
#         #'mTime':'수행시각'
#         #,'item_no':'아이템ID'
#         'mOriginName':'교체대상카드명'
#         ,'mRedrawGroupNo':'합성종류'
#         ,'mResultName':'교체된 카드명'
#         ,'test_result_count':'뽑기횟수'
#         ,'probability':'뽑기확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)

#         # if not os.path.exists(outputName):
#         #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         # else:
#         #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

#         makeCsv(outputName, target, b)

#         del a,b
#         gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_redraw_serv_gacha():#probtest 16 (인자 2 필요)
#     startTime = time.time()

#     probTestNo = 16

#     outputName = f"{resultDir}/서번트교체(뽑기획득)결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

#     targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')
#     #targetList = targetList_before.split(sep='|')

#     for target in targetList :
#         cardID, redrawGroupNo = target.split(sep='|')
#         print(f'try extract target... [cardID:{cardID}, redrawGroupNo:{redrawGroupNo}]')
#         #print(probTestNo,cardID, redrawGroupNo)

#         global df
#         a = df[(df["probability_type"] == probTestNo)&(df["item_no"] == int(cardID))]
#         a = a.reset_index(drop=True)
#         #print(a)

#         a["mTime"]=""
#         a["mOriginName"]=""
#         a["mResultName"]=""
#         a["mRedrawGroupNo"]=""

#         if len(a) == 0 :
#             print(f'no data... {cardID}|{redrawGroupNo}')
#         for i in range(len(a)):

#             #etc_json에서 추출
#             tempStr = a.loc[i,"etc_json"]
#             tempGet0 = re.search('RedrawGroupNo":(.+?)}', tempStr).group(1)
#             a.loc[i,"mRedrawGroupNo"] = tempGet0

#         a = a[(a["mRedrawGroupNo"] == redrawGroupNo)]
#         a = a.reset_index(drop=True)

#         for i in range(len(a)):
#             try:
#                 #카드명 적용
#                 before0 = a.loc[i,"item_no"]
#                 before1 = a.loc[i,"result_item_no"]
#                 after0 = df_serv.loc[before0,"mName"]
#                 after1 = df_serv.loc[before1,"mName"]
#                 a.loc[i,"mOriginName"] = after0
#                 a.loc[i,"mResultName"] = after1

#                 #카드 정렬용
#                 rarity = df_serv.loc[before1,"mRarity"]
#                 a.loc[i,"mRarity"] = rarity
#                 a = a.sort_values(by=["mRarity","result_item_no"])

#             except :
#                 print(f"data 업데이트 요망... Type:서번트,ID:{before0}or{before1} 누락")
#                 a.loc[i,"mOriginName"] = "BLANK"
#                 a.loc[i,"mResultName"] = "BLANK"
#             #시간표기용
#             a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
#         b=a[["mTime","mOriginName","mRedrawGroupNo","mResultName","test_result_count","probability"]]
#         b = b.reset_index(drop=True)

        
#         b.rename(columns={
#         'mTime':'수행시각'
#         #,'item_no':'아이템ID'
#         ,'mOriginName':'교체대상카드명'
#         ,'mRedrawGroupNo':'교체그룹ID'
#         ,'mResultName':'교체된 카드명'
#         ,'test_result_count':'봅기횟수'
#         ,'probability':'뽑기확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)


#         if not os.path.exists(outputName):
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         else:
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

#         del a,b
#         gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_redraw_serv_combine():#probtest 17 (인자 2 필요)
#     startTime = time.time()

#     probTestNo = 17

#     outputName = f"{resultDir}/서번트교체(합성획득)결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

#     targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')
#     #targetList = targetList_before.split(sep='|')

#     for target in targetList :
#         cardID, rarity = target.split(sep='|')
#         print(f'try extract target... [cardID:{cardID}, rarity:{rarity}]')
#         #print(probTestNo,cardID, redrawGroupNo)

#         global df
#         a = df[(df["probability_type"] == probTestNo)&(df["item_no"] == int(cardID))&(df["item_sub_no"] == int(rarity))]
#         a = a.reset_index(drop=True)
#         #print(a)

#         a["mTime"]=""
#         a["mOriginRarity"]=""
#         a["mOriginName"]=""
#         a["mResultName"]=""
#         #a["mRedrawGroupNo"]=""

#         # for i in range(len(a)):

#         #     #etc_json에서 추출
#         #     tempStr = a.loc[i,"etc_json"]
#         #     tempGet0 = re.search('Rarity":(.+?)}', tempStr).group(1)
#         #     a.loc[i,"mOriginRarity"] = tempGet0

#         # a = a[(a["mOriginRarity"] == rarity)]
#         # a = a.reset_index(drop=True)

#         for i in range(len(a)):
#             try:
#                 #카드명 적용
#                 before0 = a.loc[i,"item_no"]
#                 before1 = a.loc[i,"result_item_no"]
#                 after0 = df_serv.loc[before0,"mName"]
#                 after1 = df_serv.loc[before1,"mName"]
#                 a.loc[i,"mOriginName"] = after0
#                 a.loc[i,"mResultName"] = after1

#                 #카드 정렬용
#                 tempRarity = df_serv.loc[before1,"mRarity"]
#                 a.loc[i,"mRarity"] = tempRarity
#                 a = a.sort_values(by=["mRarity","result_item_no"])
#             except:
#                 print(f"data 업데이트 요망... Type:서번트,ID:{before0}or{before1} 누락")
#                 a.loc[i,"mOriginName"] = "BLANK"
#                 a.loc[i,"mResultName"] = "BLANK"
#             #시간표기용
#             a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
#         b=a[["mTime","item_no","mOriginName","item_sub_no","result_item_no","mResultName","test_result_count","probability"]]
#         b = b.reset_index(drop=True)

        
#         b= b.replace({"item_sub_no":2},"희귀합성")
#         b= b.replace({"item_sub_no":3},"영웅합성")
#         b= b.replace({"item_sub_no":4},"전설합성")

#         b.rename(columns={
#         'mTime':'수행시각'
#         #,'item_no':'아이템ID'
#         ,'mOriginName':'교체대상카드명'
#         ,'mRedrawGroupNo':'합성종류'
#         ,'mResultName':'교체된 카드명'
#         ,'test_result_count':'뽑기횟수'
#         ,'probability':'뽑기확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)

#         if not os.path.exists(outputName):
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         else:
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

#         del a,b
#         gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_reinforce_slot():#probtest 18 (인자 필요)
#     """슬롯강화
    
#     probTarget 입력 필요 : 0 = 장비, 2 = 매터리얼
#     """
#     startTime = time.time()

#     probTestNo = 18

#     outputName = f"{resultDir}/슬롯강화.csv"

#     targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')
#     #targetList = targetList_before.split(sep='|')

#     for target in targetList :
#         print(f'try extract target... [typeNo:{target}]')
#         #print(probTestNo,cardID, redrawGroupNo)

#         global df
#         a = df[(df["probability_type"] == probTestNo)&(df["probability_category"] == int(target))&(df["result_item_no"] == 1)]
#         a = a.reset_index(drop=True)
#         #print(a)

#         a["mTime"]=""
#         a["mStep"]=""

#         for i in range(len(a)):

#             #etc_json에서 추출
#             tempStr = a.loc[i,"etc_json"]
#             tempGet0 = re.search('Step":(.+?),', tempStr).group(1)
#             a.loc[i,"mStep"] = int(tempGet0) + 1

#         # a = a[(a["mOriginRarity"] == rarity)]
#         # a = a.reset_index(drop=True)

#         for i in range(len(a)):

#             #시간표기용
#             a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
#         b=a[["mTime","probability_category","item_no","item_sub_no","mStep","test_result_count","probability"]]
#         b = b.reset_index(drop=True)



#         b.loc[((b.probability_category == 0) & (b.item_no == 0)), "item_no"] = "무기"
#         b.loc[((b.probability_category == 0) & (b.item_no == 1)), "item_no"] = "투구"
#         b.loc[((b.probability_category == 0) & (b.item_no == 2)), "item_no"] = "갑옷"
#         b.loc[((b.probability_category == 0) & (b.item_no == 4)), "item_no"] = "신발"
#         b.loc[((b.probability_category == 0) & (b.item_no == 7)), "item_no"] = "반지I"
#         b.loc[((b.probability_category == 0) & (b.item_no == 8)), "item_no"] = "반지II"
#         b.loc[((b.probability_category == 0) & (b.item_no == 9)), "item_no"] = "목걸이"
#         b.loc[((b.probability_category == 0) & (b.item_no == 10)), "item_no"] = "벨트"
        
#         b.loc[((b.probability_category == 2) & (b.item_no == 0)), "item_no"] = "숙련"
#         b.loc[((b.probability_category == 2) & (b.item_no == 1)), "item_no"] = "영혼"
#         b.loc[((b.probability_category == 2) & (b.item_no == 2)), "item_no"] = "수호"
#         b.loc[((b.probability_category == 2) & (b.item_no == 3)), "item_no"] = "파괴"
#         b.loc[((b.probability_category == 2) & (b.item_no == 4)), "item_no"] = "생명"
        
#         b= b.replace({"probability_category":0},"장비슬롯")
#         b= b.replace({"probability_category":2},"매터리얼슬롯")
        
#         b= b.replace({"item_sub_no":0},"일반")
#         b= b.replace({"item_sub_no":1},"고급")
#         b= b.replace({"item_sub_no":2},"희귀")
#         b= b.replace({"item_sub_no":3},"영웅")
#         b= b.replace({"item_sub_no":4},"전설")
#         b= b.replace({"item_sub_no":5},"초월")
#         #df = df.convert_objects(convert_numeric=True)

#         #b=b.convert_objects("mStep",convert_numeric=True)
#         #b["mStep"] = int(b["mStep"]) + 1
#         b.rename(columns={
#         'mTime':'수행시각'
#         ,'probability_category':'슬롯타입'
#         ,'item_no':'슬롯명'
#         ,'item_sub_no':'등급'
#         ,'mStep':'단계'
#         ,'test_result_count':'강화성공횟수'
#         ,'probability':'강화성공확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)

#         if not os.path.exists(outputName):
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         else:
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

#         del a,b
#         gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_reinforce_slot_ancient():#probtest 19 (인자 필요)
    
#     """슬롯강화(고대주문서)
    
#     probTarget 입력 필요 : 0 = 장비, 2 = 매터리얼
#     """
#     startTime = time.time()

#     probTestNo = 19

#     outputName = f"{resultDir}/슬롯강화(고대주문서).csv"

#     targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')
#     #targetList = targetList_before.split(sep='|')

#     for target in targetList :
#         print(f'try extract target... [typeNo:{target}]')
#         #print(probTestNo,cardID, redrawGroupNo)

#         global df
#         a = df[(df["probability_type"] == probTestNo)&(df["probability_category"] == int(target))&(df["result_item_no"] == 1)]
#         a = a.reset_index(drop=True)
#         #print(a)

#         a["mTime"]=""
#         a["mStep"]=""

#         for i in range(len(a)):

#             #etc_json에서 추출
#             tempStr = a.loc[i,"etc_json"]
#             tempGet0 = re.search('Step":(.+?),', tempStr).group(1)
#             a.loc[i,"mStep"] = int(tempGet0) + 1

#         # a = a[(a["mOriginRarity"] == rarity)]
#         # a = a.reset_index(drop=True)

#         for i in range(len(a)):

#             #시간표기용
#             a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
#         b=a[["mTime","probability_category","item_no","item_sub_no","mStep","test_result_count","probability"]]
#         b = b.reset_index(drop=True)



#         b.loc[((b.probability_category == 0) & (b.item_no == 0)), "item_no"] = "무기"
#         b.loc[((b.probability_category == 0) & (b.item_no == 1)), "item_no"] = "투구"
#         b.loc[((b.probability_category == 0) & (b.item_no == 2)), "item_no"] = "갑옷"
#         b.loc[((b.probability_category == 0) & (b.item_no == 4)), "item_no"] = "신발"
#         b.loc[((b.probability_category == 0) & (b.item_no == 7)), "item_no"] = "반지I"
#         b.loc[((b.probability_category == 0) & (b.item_no == 8)), "item_no"] = "반지II"
#         b.loc[((b.probability_category == 0) & (b.item_no == 9)), "item_no"] = "목걸이"
#         b.loc[((b.probability_category == 0) & (b.item_no == 10)), "item_no"] = "벨트"
        
#         b.loc[((b.probability_category == 2) & (b.item_no == 0)), "item_no"] = "숙련"
#         b.loc[((b.probability_category == 2) & (b.item_no == 1)), "item_no"] = "영혼"
#         b.loc[((b.probability_category == 2) & (b.item_no == 2)), "item_no"] = "수호"
#         b.loc[((b.probability_category == 2) & (b.item_no == 3)), "item_no"] = "파괴"
#         b.loc[((b.probability_category == 2) & (b.item_no == 4)), "item_no"] = "생명"
        
#         b= b.replace({"probability_category":0},"장비슬롯")
#         b= b.replace({"probability_category":2},"매터리얼슬롯")
        
#         b= b.replace({"item_sub_no":0},"일반")
#         b= b.replace({"item_sub_no":1},"고급")
#         b= b.replace({"item_sub_no":2},"희귀")
#         b= b.replace({"item_sub_no":3},"영웅")
#         b= b.replace({"item_sub_no":4},"전설")
#         b= b.replace({"item_sub_no":5},"초월")
#         #df = df.convert_objects(convert_numeric=True)

#         #b=b.convert_objects("mStep",convert_numeric=True)
#         #b["mStep"] = int(b["mStep"]) + 1

#         b.rename(columns={
#         'mTime':'수행시각'
#         ,'probability_category':'슬롯타입'
#         ,'item_no':'슬롯명'
#         ,'item_sub_no':'등급'
#         ,'mStep':'단계'
#         ,'test_result_count':'뽑기횟수'
#         ,'probability':'뽑기확률(%)'
#         ,'mExpectedProb':'기대확률(%)'
#         ,'mProbDiff':'오차(%)'
#         }, inplace = True)

#         if not os.path.exists(outputName):
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#         else:
#             b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

#         del a,b
#         gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_engrave():#probtest 11 (인자 필요)

#     """각인 확률
    
#     Target:
#         probTarget.csv 입력 필요 (type = 11)

#     ProbInfo:
#         probInfo.csv 입력 필요 (id = 962~973)
#     """

#     startTime = time.time()

#     probTestNo = 11

#     outputName = f"{resultDir}/각인.csv"

#     targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')

#     for target in targetList :
#         #print(f'extracting target... [itemID:{target}]')
#         #print(probTestNo,cardID, redrawGroupNo)

#         for j in range(0,2):

#             global df

#             if j == 0 :
#                 scrollID = 700
#             else : 
#                 scrollID = 701

#             a = df[(df["probability_type"] == probTestNo)&(df["item_no"] == int(target))&(df["item_sub_no"] == scrollID)]
#             a = a.reset_index(drop=True)
#             #print(a)

#             a["mTime"]=""
#             a["mItemName"]=""
#             a["mSlainType"]=""
#             a["mSlainTypeName"]=""
#             a["mAbilityType"]=""
#             a["mAbilityTypeName"]=""
#             a["mStatLevel"]=""
#             a["mNormalCount"]=""
#             a["mBlessCount"]=""
#             a["mStatName"]=""
#             a["mExpectedProb"]=""
#             a["mProbDiff"]=""
            

#             for i in tqdm(range(len(a))):
                
#                 """mSubType"""
#                 defaultTypeList = [2,80] #나이트단검,나이트대검,어쌔신단검 subType (공속 미포함)
#                 defaultTypeList1 = [8,4,78] #나이트단검,어쌔신단검 subType (공속 미포함)
#                 defaultTypeList2 = [14] #장갑(공속)  
#                 defaultTypeList3 = [15] #신발(이속)  
                
#                 #defaultTypeList1 = [10,11,6,9] #총,활,지팡이,스태프,투구 : 그냥 "2단계 옵션"
#                 #etc_json에서 추출
#                 tempStr = a.loc[i,"etc_json"]
#                 tempGet0 = re.search('SlaintType":(.+?),', tempStr).group(1)
#                 tempGet1 = re.search('AbilityType":(.+?)}', tempStr).group(1)
#                 a.loc[i,"mSlainType"] = int(tempGet0)
#                 a.loc[i,"mAbilityType"] = int(tempGet1)

#                 before0 = a.loc[i,"item_no"]
#                 after0 = df_item.loc[before0,"mName"]
#                 a.loc[i,"mItemName"] = after0

#                 before1 = a.loc[i,"mSlainType"]
#                 after1 = df_engraveSlain.loc[before1,"mName"]
#                 a.loc[i,"mSlainTypeName"] = after1

#                 before2 = a.loc[i,"mAbilityType"]
#                 after2 = df_engraveAbility.loc[before2,"mName"]
#                 a.loc[i,"mAbilityTypeName"] = after2

#                 statLevel = a.loc[i,"result_item_no"]                

#                 optionID = int( df_item.loc[df_item["mName"] == after0 , "mSubType"])
#                 if optionID in defaultTypeList :
#                     a=a.replace({"probability_category":0},"1단계 옵션")
#                     a=a.replace({"probability_category":1},"2단계 옵션(단검)")
#                     a=a.replace({"probability_category":2},"3단계 옵션")
#                     a=a.replace({"probability_category":3},"4단계 옵션")
#                     a=a.replace({"probability_category":4},"5단계 옵션")
#                 elif optionID in defaultTypeList1 :
#                     a=a.replace({"probability_category":0},"1단계 옵션")
#                     a=a.replace({"probability_category":1},"2단계 옵션(공격 속도)(단검 외)")
#                     a=a.replace({"probability_category":2},"3단계 옵션")
#                     a=a.replace({"probability_category":3},"4단계 옵션")
#                     a=a.replace({"probability_category":4},"5단계 옵션")
#                 elif optionID in defaultTypeList2 :
#                     a=a.replace({"probability_category":0},"1단계 옵션")
#                     a=a.replace({"probability_category":1},"2단계 옵션")
#                     a=a.replace({"probability_category":2},"3단계 옵션(공격 속도)")
#                     a=a.replace({"probability_category":3},"4단계 옵션")
#                     a=a.replace({"probability_category":4},"5단계 옵션")
#                 elif optionID in defaultTypeList3 :
#                     a=a.replace({"probability_category":0},"1단계 옵션")
#                     a=a.replace({"probability_category":1},"2단계 옵션")
#                     a=a.replace({"probability_category":2},"3단계 옵션(이동 속도)")
#                     a=a.replace({"probability_category":3},"4단계 옵션")
#                     a=a.replace({"probability_category":4},"5단계 옵션")
#                 else :
#                     a=a.replace({"probability_category":0},"1단계 옵션")
#                     a=a.replace({"probability_category":1},"2단계 옵션")
#                     a=a.replace({"probability_category":2},"3단계 옵션")
#                     a=a.replace({"probability_category":3},"4단계 옵션")
#                     a=a.replace({"probability_category":4},"5단계 옵션")

#                 #||일부 능력치 계수 보정■■■■■■■■■■■■■■■■■■■■■■■■■■■■■||#
#                 if int(statLevel) < 0 :
#                     statLevel = int(statLevel)*(-1)

#                 if "치명타 확률" in after2 :
#                     statLevel *= 0.5
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "최대 소지 무게" in after2 :
#                     statLevel *= 0.01
#                     statLevel = round(statLevel)
#                 elif "마나 소모 감소율" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "흡수 확률" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "흡수 확률" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "골드 획득량" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "경험치 획득량" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "아이템 드랍률" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "계약 효과 증가" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "포션 회복률" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'
#                 elif "공격 속도" in after2 :
#                     statLevel *= 0.1
#                     if statLevel < 0.8 :
#                         statLevel = f'{round(statLevel, 1)}'
#                     elif statLevel < 1.5 :
#                         statLevel = f'{round(statLevel, 1)+0.01}'
#                     elif statLevel < 1.8 :
#                         statLevel = f'{round(statLevel, 1)+0.02}'
#                     elif statLevel < 2 :
#                         statLevel = f'{round(statLevel, 1)+0.03}'
#                     else:
#                         statLevel = f'{round(statLevel, 1)+0.04}'
#                 elif "이동 속도" in after2 :
#                     numbers = [0.28, 0.57, 0.85, 1.14, 1.42, 1.71, 2.0, 2.28, 2.57, 2.85]
#                     statLevel = numbers[int(statLevel)-1]

#                 elif "경험치 획득" in after2 :
#                     statLevel *= 0.01
#                     statLevel = f'{round(statLevel, 2)}'

#                 #||■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■||#
#                 a.loc[i,"mStatLevel"] = statLevel


#                 if before1 != 0 :
#                     a.loc[i,"mStatName"] = f'[{after1}]{after2} +{statLevel}'
#                 else :
#                     a.loc[i,"mStatName"] = f'{after2} +{statLevel}'

        


#             # a = a[(a["mOriginRarity"] == rarity)]
#             # a = a.reset_index(drop=True)

                    
#             a = a.sort_values(by=["probability_category","item_sub_no","mAbilityType","mSlainType","result_item_no"])

#             b=a[["item_sub_no","mItemName","probability_category","mSlainTypeName","mAbilityTypeName","mStatLevel","mStatName","test_result_count","probability","mExpectedProb","mProbDiff"]]
#             #expectedProb = 0 일 경우 두번째에 item_no 뺴야함.
#             b = b.reset_index(drop=True)


#             colNum = -1           
#             row= -1
#             title = ""
#             #try : 
#             try : 
#                 gachaID = int(target)
#                 colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
#             except:
#                 gachaID = target
#                 colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
#             #print(gachaID)
#             row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
#             title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
#             webID = f"{row}_{str(colNum).split('.')[0]}"
#             b=compare_prob2(webID,b,11).copy()




#             """확률검증용"""
#             #b=b[["item_sub_no","mItemName","probability_category","mStatName","test_result_count","probability","mExpectedProb","mProbDiff"]]


#             """각인확인용(대만)"""
#             #b=b[["item_sub_no","mItemName","probability_category","mStatName","test_result_count","probability","mExpectedProb","mProbDiff"]]

#             #except :
#             #    emptyProbList.append(f"11|{target}|{title}|{row}|{colNum}")
            
#             b= b.replace({"probability_category":0},"1")
#             b= b.replace({"probability_category":1},"2")
#             b= b.replace({"probability_category":2},"3")
#             b= b.replace({"probability_category":3},"4")
#             b= b.replace({"probability_category":4},"5")

#             b= b.replace({"item_sub_no":700},"일반 각인")
#             b= b.replace({"item_sub_no":701},"축복 각인")
            
#             # b.rename(columns={
#             # 'mTime':'수행시각'
#             # #,'probability_category':'슬롯타입'
#             # #,'item_no':'슬롯명'
#             # ,'item_sub_no':'각인분류'
#             # ,'mItemName':'장비명'
#             # ,'probability_category':'옵션번호'
#             # ,'mSlainTypeName':'슬레인타입'
#             # ,'mAbilityTypeName':'능력치'
#             # ,'mStatLevel':'세부수치'
#             # ,'mStatName':'능력치명'
#             # ,'test_result_count':'뽑기횟수'
#             # ,'probability':'뽑기확률(%)'
#             # ,'mExpectedProb':'기대확률(%)'
#             # ,'mProbDiff':'오차(%)'
#             # }, inplace = True)
            
#             # if not os.path.exists(outputName):
#             #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#             # else:
#             #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
#             makeCsv(outputName,title,b)        

#             del a,b
#             gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# def check_redraw_tran_gacha_all():#probtest 14 (인자 불필요 - 전체)
#     startTime = time.time()

#     probID = 14

#     outputName = f"{resultDir}/변신교체(뽑기획득)결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

#     global df

#     df_temp = df[(df['probability_type']==probID)]
#     df_temp = df_temp.reset_index(drop=True)
#     print(df_temp)
#     df_temp['temp0'] = ""
#     for i in range(len(df_temp)):
#         print(f'{i}/{len(df_temp)}', end = '\r')
#         df_temp.loc[i,'temp0'] = df_temp.loc[i,'etc_json']
#     #df_temp['temp1'] = df_temp['etc_json']
#     #df_temp['temp0'] = df_temp['temp0'].str.replace('{"value":{"RedrawGroupNo":', '')
#     #df_temp['temp0'] = df_temp['temp0'].str.replace('}}', '')

#     df_temp1 = df_temp.drop_duplicates(subset='temp0')
#     #groupList = df_temp1['temp0'].astype('int')
#     #print(groupList)
#     #df_temp['temp0'] = df_temp['temp0'].str.replace('}}', '')
#     #df_temp = df_temp.replace('(.*){"value":{"RedrawGroupNo":(.*)', r'\1\2', regex=True)
#     #df_temp = df_temp.replace('(.*)}}(.*)', r'\1\2', regex=True)

#     #print(df_temp)
#     #targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')
#     #targetList = targetList_before.split(sep='|')

#     # for target in targetList :
#     #     cardID, redrawGroupNo = target.split(sep='|')
#     #     print(f'try extract target... [cardID:{cardID}, redrawGroupNo:{redrawGroupNo}]')
#     #     #print(probTestNo,cardID, redrawGroupNo)

#     #     global df
#     #     a = df[(df["probability_type"] == probID)&(df["item_no"] == int(cardID))]
#     #     a = a.reset_index(drop=True)
#     #     #print(a)

#     #     a["mTime"]=""
#     #     a["mOriginName"]=""
#     #     a["mResultName"]=""
#     #     a["mRedrawGroupNo"]=""
#     #     a["mGroupID"]=""

#     #     for i in range(len(a)):

#     #         #etc_json에서 추출
#     #         tempStr = a.loc[i,"etc_json"]
#     #         tempGet0 = re.search('RedrawGroupNo":(.+?)}', tempStr).group(1)
#     #         a.loc[i,"mRedrawGroupNo"] = tempGet0

#     #     a = a[(a["mRedrawGroupNo"] == redrawGroupNo)]
#     #     a = a.reset_index(drop=True)

#     #     for i in range(len(a)):
#     #         try:
#     #             #카드명 적용
#     #             before0 = a.loc[i,"item_no"]
#     #             before1 = a.loc[i,"result_item_no"]
#     #             after0 = df_tran.loc[before0,"mName"]
#     #             after1 = df_tran.loc[before1,"mName"]
#     #             a.loc[i,"mOriginName"] = after0
#     #             a.loc[i,"mResultName"] = after1

#     #             #카드 정렬용
#     #             rarity = df_tran.loc[before1,"mRarity"]
#     #             a.loc[i,"mRarity"] = rarity
#     #             a = a.sort_values(by=["mRarity","result_item_no"])

#     #             tempGroupID = df_tran.loc[before1,"mGroupID"]
#     #             a.loc[i,"mGroupID"] = tempGroupID

#     #         except :
#     #             print(f"data 업데이트 요망... Type:변신,ID:{before0}or{before1} 누락")
#     #             a.loc[i,"mOriginName"] = "BLANK"
#     #             a.loc[i,"mResultName"] = "BLANK"

#     #         a = a.sort_values(by=["mRarity","mGroupID","mRarity"])

#     #         #시간표기용
#     #         a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
#     #     b=a[["mTime","mOriginName","mRedrawGroupNo","mResultName","test_result_count","probability"]]
#     #     b = b.reset_index(drop=True)

#     #     b = compare_prob(probID, b, redrawGroupNo, after0)
#     #     b.rename(columns={
#     #     'mTime':'수행시각'
#     #     #,'item_no':'아이템ID'
#     #     ,'mOriginName':'교체대상카드명'
#     #     ,'mRedrawGroupNo':'교체그룹ID'
#     #     ,'mResultName':'교체된 카드명'
#     #     ,'test_result_count':'뽑기횟수'
#     #     ,'probability':'뽑기확률(%)'
#     #     ,'mExpectedProb':'기대확률(%)'
#     #     ,'mProbDiff':'오차(%)'
#     #     }, inplace = True)


#     #     if not os.path.exists(outputName):
#     #         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
#     #     else:
#     #         b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

#     #     del a,b
#     #     gc.collect()

#     print(f'total-run-time : {time.time()-startTime:.4f} sec')

# if __name__ == "__main__" : 
#     check_gacha()                      #230307 #230330 전리품뽑기 예외필요, 매터리얼뽑기 [일반] 띄어쓰기문제
#     # check_combine_card(2)              #230307
#     # check_combine_card(3)              #230307
#     # check_combine_mat()                #230307
#     # check_craft()                      #230307 >>>>>>>>>>>>2023-04-05 교체해야됨(고지표 이름 잘못됨, 백만개 > 천만개 )
#     # check_skill()                      #230403
#     # check_change_mat()                  #230404
#     # check_reinforce_item()              #230405
#     # check_reinforce_item_point()        #230405
#     # check_soul()   
#     # check_engrave()
#     # check_spot_tran()                   #변신/서번트합치자
#     # check_spot_serv()  
#     # check_redraw_gacha(14)             #230307
#     # check_redraw_combine(15)      #230320 5|3,5|4케이스 로그 누락(사방신 변신) > 아마 3월말에하면 될것으로 추측
#     # check_redraw_gacha(16)             #230317
#     # check_redraw_combine(17)      #230320
#     # check_reinforce_slot()
#     # check_reinforce_slot_ancient()
    
    
#     #input("press any key to exit...")
    
    
#     emptyStr = (f"로그 추가 필요 : {len(emptyLogList)}건"+"\n" + "\n".join(emptyLogList))
#     emptyStr += (f"\n데이터 추가 필요 : {len(emptyDataList)}건"+"\n" + "\n".join(emptyDataList))
#     emptyStr += (f"\n고지표 업데이트 필요 : {len(emptyProbList)}건"+"\n" + "\n".join(emptyProbList))
#     #check_redraw_tran_gacha_all()

#     emptyFileName = f"{resultDir}/emptyList.txt"
#     with open(emptyFileName, "a") as f:
#         f.write(emptyStr)