import pandas as pd
import time
import os
import gc
import re
from tqdm import tqdm


resultBasicDir = f"./result"
if not os.path.isdir(resultBasicDir) :
    os.mkdir(resultBasicDir)

resultDir = f"./result/{time.strftime('%y%m%d_%H%M%S')}"
if not os.path.isdir(resultDir) :
    os.mkdir(resultDir)


#fileName = input("확률테스트결과문서명 입력(.csv 제외) : ")
#global df, df_target

emptyLogList = []#로그누락
emptyDataList = []#데이터문서(변신,서번트,아이템 등) 누락
emptyProbList = []#확률문서 누락

fileName = ""
#fileName = "R2MProbabilityTestHistory_20221219_20230120.csv"

targetName = "probTarget.csv"

while not os.path.isfile(fileName) :
    try : 
        global df, df_target
        #fileName = input("확률테스트결과문서명 입력(.csv 제외) : ")
        fileName = "R2MProbabilityTestHistory_20230330_20230331"
        if fileName == "" :
            #fileName = "R2MProbabilityTestHistory_20221219_20230120.csv"#R2MProbabilityTestHistory_20230126_20230127
            fileName = "R2MProbabilityTestHistory_20230330_20230331.csv"#R2MProbabilityTestHistory_20230126_20230127
        else :
            fileName = f'{fileName}.csv'
        df = pd.read_csv(fileName)
        df_target = pd.read_csv(targetName)
        df_target = df_target.set_index("mType")
    except FileNotFoundError: 
        print("파일 없음...")
        #time.sleep(2)

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
    df_temp = df_temp.reset_index(drop=True)
    df_temp = df_temp.set_index("mID")

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


df_webProb_path = f"./webProb.xlsx"
#df_webProb = pd.read_excel(df_webProb_path)

def compare_prob2(refPage : str, df_before : pd.DataFrame, probID : int,  inOrder = False, targetColName = "이름", refColName = "확률" ,args = []):
    """
    확률비교 by getWebProb.py

    예외처리 A-2 : targetColName 변경 필요
    """
    
    
    sheet_name = f'{refPage}'#942_0
    df_ref = pd.read_excel(df_webProb_path, sheet_name=sheet_name, engine="openpyxl")
    #print (df_ref.columns.tolist())

    #print(df_ref)
    #print(df_before)
    df_after = df_before.copy()
    df_after = df_after.reset_index(drop=True)

    if probID == 11 : #각인확률검사
        df_ref = df_ref.replace('-','0')
        df_ref.iloc[2:, 4] = df_ref.iloc[2:, 4].astype(float)
        df_ref.iloc[2:, 7] = df_ref.iloc[2:, 7].astype(float)
        df_after.iloc[:, 7] = df_after.iloc[:, 7].astype(float)
        #df_after.iloc[2:, 7] = df_after.iloc[2:, 7].astype(float)

        for i in range(len(df_after)):
            print(df_after.loc[i,"probability_category"])
            scrollType = int(df_after.loc[i,"item_sub_no"])#일반/축복각인
            optionName = df_after.loc[i,"probability_category"]
            slainName = df_after.loc[i,"mSlainTypeName"]
            abilityName = df_after.loc[i,"mAbilityTypeName"]
            statLevel = (df_after.loc[i,"mStatLevel"])

            print(f'{scrollType} {optionName} {slainName} {abilityName} {statLevel}')

            expectedProb = 0

            #try: 
            if scrollType == 700:
                expectedProb = df_ref.loc[(df_ref[0] == optionName)
                                        &(df_ref[1] == slainName)
                                        &(df_ref[2] == abilityName)
                                        &(df_ref[4] == statLevel)
                                        , 5].iloc[0]
                # expectedProb = df_ref.loc[(df_ref[0] == optionName)
                #                         , 5].iloc[0]
            elif scrollType == 701:
                expectedProb = df_ref.loc[(df_ref[0] == optionName)
                                        &(df_ref[1] == slainName)
                                        &(df_ref[2] == abilityName)
                                        &(df_ref[7] == statLevel)
                                        , 8].iloc[0]
            #except :
            #    expectedProb = 0
            print(expectedProb)
            
            df_after.loc[i,"mExpectedProb"] = float(expectedProb)
            df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)

    elif probID == 5 : #확률참조 두개 열

        for i in range(len(df_after)):
            itemName = df_after.loc[i,"mName"]
            getType = int(df_after.loc[i,"item_sub_no"])

            if getType == 1 :
                refColName = "제작 성공 확률(%)"
            elif getType == 2 :
                refColName = "대성공 확률(%)"
            

            try : 
                basicProb =  df_ref.loc[df_ref[targetColName] == itemName, "제작 성공 확률(%)"].iloc[0]
                if basicProb == "-" :
                    basicProb = 0
                expectedProb = df_ref.loc[df_ref[targetColName] == itemName, refColName].iloc[0]

                if getType == 2:
                    expectedProb = float(expectedProb) * float(basicProb) * 0.01

                df_after.loc[i,"mExpectedProb"] = expectedProb
                df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)
            except IndexError:
                print(f'{probID}|{itemName}')
                emptyProbList.append(f'{probID}|{itemName}')
                df_after.loc[i,"mExpectedProb"] = ""
                df_after.loc[i,"mProbDiff"] = ""

    elif inOrder: ##검색없이 로그 순서대로 : 4

        for i in range(len(df_after)):
            #itemName = df_after.loc[i,"mName"]
            expectedProb = df_ref.loc[i, '확률']
            df_after.loc[i,"mExpectedProb"] = expectedProb
            df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)

    else : ## 원본의 mName 열만 필요.

        for i in range(len(df_after)):
            try : 
                try : 
                    itemName = df_after.loc[i,"mName"]
                except :
                    itemName = df_after.loc[i,"mResultName"]

                if probID == 14 or probID == 15: #교체뽑기 확률 환산용
                    rootID = int(args)
                    rootItemName = df_tran.loc[rootID,"mName"]
                elif probID == 16 or probID == 17 : #교체뽑기 확률 환산용
                    rootID = int(args)
                    rootItemName = df_serv.loc[rootID,"mName"]
            except : 
                emptyLogList.append(f'{probID}|{itemName}')
                continue
            
            
            if probID == 14 or probID == 15 or probID == 16 or probID == 17 : #교체뽑기 확률 환산용
                #print("1")
                rootProb = df_ref.loc[(df_ref['이름'] == rootItemName), '확률']
                #print("1")
                fixedTotalProb = df_ref['확률'].sum() - rootProb
                #print("1")
                df_ref['확률'] = round(df_ref['확률']  * 100 / fixedTotalProb[0] ,4)
                #print("1")

            """
            ※예외처리A
            확률고지표에서 itemName을 못 찾을 경우, 
            case 1: itemName이 없을 수 있음.
            """
            try :
                expectedProb = df_ref.loc[df_ref[targetColName] == itemName, refColName].iloc[0]
                df_after.loc[i,"mExpectedProb"] = expectedProb
                df_after["mProbDiff"] = round(abs(df_after["mExpectedProb"] - df_after["probability"])/df_after["mExpectedProb"]*100,4)
            except :
                emptyProbList.append(f'{probID}|{itemName}')
                df_after.loc[i,"mExpectedProb"] = ""
                df_after.loc[i,"mProbDiff"] = ""
            #중단점

    del df_ref
    gc.collect()


    return df_after


def makeCsv(outputName : str, title : str, df : pd.DataFrame):
    """
    확률 표 별로 상단에 title이 입력되도록 구분짓게 함.
    \noutputName : 결과물 파일명
    \ntitle : 표 상단 제목
    \ndf : 해당 데이터 프레임
    """
    with open(outputName, mode='a', encoding='utf-8-sig', newline='') as f:
        #if f.tell() != 0:
        f.write(f'\n{title}\n')
        df.to_csv(f, sep=',', index=False, header=True)

def getWebID(target, mID = [int]):
    gachaID = target
    #print(gachaID)
    if len(mID) == 0 : #전체에서 검색
        colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
        row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
        title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
        webID = f"{row}_{str(colNum).split('.')[0]}"
    
    else : #해당 행에서 검색
        webID = mID[0]
        for id in mID :
            #print(id)
            try :
                colNum =  df_probInfo.columns[df_probInfo.loc[df_probInfo.index==id].eq(gachaID).any()][0]
                webID = f"{id}_{str(colNum).split('.')[0]}"
            except :
                continue

    return webID

def check_gacha():#probtest 1
    startTime = time.time()

    probID = 1

    outputName = f"{resultDir}/뽑기_{time.strftime('%y%m%d_%H%M%S')}.csv"
    xlsxName = f"{resultDir}/뽑기_{time.strftime('%y%m%d_%H%M%S')}.xlsx"

    global df

    curDf = df[df["probability_type"] == probID]
    curDf = curDf.copy()
    curDf['groupID'] = curDf['etc_json'].str.extract(r'(\d+)')
    targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')
    if not targetList[0].isnumeric() :
        print("target is null... activate all test...")
        
        #첫번째 숫자 추출
        curDf['groupID'] = curDf.etc_json.str.extract(r'(\d+)')
        #두번째 숫자 추출
        #curDf['etc_json'] = curDf['etc_json'].str.extract(r'^\D*\d+\D+(\d+)')
        
        
        df_temp = curDf.drop_duplicates(subset='etc_json')
        df_temp = df_temp.drop_duplicates(subset='item_no')
        targetList = df_temp['item_no'].astype('int')
        groupList = df_temp['groupID'].astype('int')
        del df_temp
        gc.collect()

    print("check_gacha...")

    for target in tqdm(targetList) :

        a = curDf[curDf["item_no"] == int(target)]
        a = a.reset_index(drop=True)

        a["mName"] =""
        a["mTime"]=""

        if len(a) == 0 :
            emptyLogList.append(f'{probID}|{target}')

        for i in range(len(a)):
            before = a.loc[i,"result_item_no"]

            targetType = int(a.loc[i,"probability_category"])
            targetName = ""

            #print("\nA1")
            if targetType == 0 :
                df_temp = df_item.copy()
                targetName = "item"
            elif targetType == 1:
                df_temp = df_tran.copy()
                targetName = "transform"
            elif targetType == 2:
                df_temp = df_serv.copy()
                targetName = "servant"

            try :
                after = df_temp.loc[before,"mName"]
                #print(after)
                a.loc[i,"mName"] = after

            #카드 정렬용
            #if targetType == 1 or targetType == 2 :
                rarity = df_temp.loc[before,"mRarity"]
                a.loc[i,"mRarity"] = rarity

                if targetType == 1 :
                    tempGroupID = df_temp.loc[before,"order"]
                    a.loc[i,"order"] = tempGroupID


            except :
                emptyDataList.append('\n'+f"no data in {targetName}list ID:{before}|{after} ")
                a.loc[i,"mName"] = ""
            a = a.sort_values(by=["mRarity","groupID","mRarity"])
            #print("\nA2")

            #시간표기용
            a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
            del df_temp
            gc.collect()


        b=a[["item_no","groupID","mName","test_result_count","probability"]].copy()
        title = ""
        try : 
            gachaID = target
            #print(gachaID)
            colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
            row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
            title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
            webID = f'{row}_{colNum}'
            b=compare_prob2(webID,b,probID).copy()
        except :
            emptyProbList.append(f"{probID}|{target}|{title}|{row}|{colNum}")

        # gachaID = int(target)
        # #print(gachaID)
        # colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
        # row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
        # title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
        # webID = f'{row}_{colNum}'
        # b=compare_prob2(webID,b).copy()

        
        b.rename(columns={
            'mTime':'수행시각'
        ,'item_no':'뽑기ID'
        ,'groupID':'그룹ID'
        ,'mName':'아이템명'
        ,'test_result_count':'뽑기횟수'
        ,'probability':'뽑기확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)
        #b.columns = ['수행시각','뽑기ID','아이템명','뽑기횟수','뽑기확률(%)','기대확률(%)','오차(%)']

        # if not os.path.exists(outputName):

        #     #b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        #     b.
        # else:
        #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        #totalResult = pd.concat([totalResult,pd.Series(name="")], ignore_index=True)
        #totalResult = pd.concat([totalResult,b], ignore_index=True)

        makeCsv(outputName, title, b)

        sheetName = "gacha"
        _mode = ''

        if not os.path.exists(xlsxName):
            _mode = 'w'
        else:
            _mode = 'a'

#region 엑셀 시트 분리
        # with pd.ExcelWriter(xlsxName, mode=_mode, engine='openpyxl') as writer:
        #     print(_mode)
        #     if writer.sheets:
        #         startrow = writer.sheets[f'{sheetName}'].max_row
        #     else:
        #         startrow = 0
        #     if startrow != 0:
        #         startrow += 1
        #     b.to_excel(writer, sheet_name=f'{sheetName}', startrow=startrow, index=False, header=True)
        # # with pd.ExcelWriter(outputName, mode='a', engine='openpyxl') as writer:
        # #     b.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
        # #     writer.sheets['Sheet1'].column_dimensions['A'].width = 50 # 예시로 A열 너비 조정

        #     # 빈 행 추가
        #     writer.sheets[f'{sheetName}'].cell(row=startrow+2, column=1).value = ""

#endregion

        # with pd.ExcelWriter(outputName, mode='a', engine='openpyxl') as writer:
        #     b.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
        #     writer.sheets['Sheet1'].column_dimensions['A'].width = 50 # 예시로 A열 너비 조정



        del a,b
        gc.collect()


    #del a
    #gc.collect()
        #print(f'success, target ID : {target}')


    # totalResult.to_excel(xlsxName, # directory and file name to write

    #         sheet_name = 'gacha', 

    #         na_rep = 'NaN', 

    #         float_format = "%.4f", 

    #         header = True, 

    #         #columns = ["group", "value_1", "value_2"], # if header is False

    #         index = False, 

    #         #index_label = "id", 

    #         startrow = 0, 

    #         startcol = 0, 

    #         #engine = 'xlsxwriter', 

    #         #freeze_panes = (2, 0)

    #         ) 
        #print(f'run-time : {time.time()-startTime:.4f} sec')
    #print(f'{emptyDataList=}')



    print(f'check_gacha() total-run-time : {time.time()-startTime:.4f} sec')

def check_combine_card(type : int):#probtest 2,3 (type 2: 변신, 3: 서번트)
    startTime = time.time()

    probID = type

    combineTypeName = ""
    if type == 2 :
        combineTypeName = "변신"
    elif type == 3 :
        combineTypeName = "서번트"

    outputName = f"{resultDir}/{combineTypeName}합성_{time.strftime('%y%m%d_%H%M%S')}.csv"
    targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')

    print("check_combine_card")
    for target in tqdm(targetList) :
        global df

        a = df[df["probability_type"] == probID]
        a = a[a["item_no"] == int(target)]
        a = a.reset_index(drop=True)
        #print(a)

        a["mName"] =""
        a["mRarity"] =""
        a["mTime"]=""

        for i in range(len(a)):
            before = a.loc[i,"result_item_no"]

            targetType = int(a.loc[i,"probability_category"])

            if targetType == 1:
                df_temp = df_tran.copy()
            elif targetType == 2:
                df_temp = df_serv.copy()

            try : 
                after = df_temp.loc[before,"mName"]
                a.loc[i,"mName"] = after
            except : 
                emptyDataList.append('\n'+f"no data in {combineTypeName}list ID:{before} ")
                a.loc[i,"mName"] = ""
                continue

            #카드 정렬용
            if targetType == 1 or targetType == 2 :
                rarity = df_temp.loc[before,"mRarity"]
                a.loc[i,"mRarity"] = rarity

            a = a.sort_values(by=["mRarity","result_item_no"])

            #시간표기용
            a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
            del df_temp
            gc.collect()


        b=a[["mName","test_result_count","probability"]]


        if type == 2 :
            b= compare_prob2(f"942_{target}",b,probID).copy()
            #combineTypeName = "변신"
        elif type == 3 :
            b= compare_prob2(f"950_{target}",b,probID).copy()
            #combineTypeName = "서번트"

        # try : 
        #     gachaID = int(target)
        #     #print(gachaID)
        #     colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
        #     row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
        #     title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
        #     webID = f'{row}_{colNum}'
        #     b=compare_prob2(webID,b).copy()
        # except :
        #    emptyProbList.append(f"{probID}|{target}|{title}|{row}|{colNum}")
        
        #인덱스 > 합성종류 표기
        # b= b.replace({"item_no":0},"일반합성")
        # b= b.replace({'item_no':1},"고급합성")
        # b= b.replace({'item_no':2},"희귀합성")
        # b= b.replace({'item_no':3},"영웅합성")
        # b= b.replace({'item_no':4},"전설합성")

        title = ""
        targetRarity = int(a.loc[0,"item_no"])
        if targetRarity == 0 :
            title = "일반 합성"
        elif targetRarity == 1 :
            title = "고급 합성"
        elif targetRarity == 2 :
            title = "희귀 합성"
        elif targetRarity == 3 :
            title = "영웅 합성"
        elif targetRarity == 4 :
            title = "전설 합성"


        b.rename(columns={
            'mTime':'수행시각'
        ,'item_no':'합성종류'
        ,'mName':'아이템명'
        ,'test_result_count':'뽑기횟수'
        ,'probability':'뽑기확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)

        # if not os.path.exists(outputName):

        #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        # else:
        #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
            

        makeCsv(outputName,title,b)
        del a,b
        gc.collect()

        #print(f'success, target ID : {target}')


        #print(f'run-time : {time.time()-startTime:.4f} sec')
    print(f'check_gacha() total-run-time : {time.time()-startTime:.4f} sec')

def check_combine_mat():#probtest 4
    startTime = time.time()

    probID = 4

    outputName = f"{resultDir}/매테합성결과_{time.strftime('%y%m%d')}.csv"

    global df

    a = df[df["probability_type"] == 4]
    a = a[a["result_item_no"] == 1] #합성성공:1, 합성실패:0
    a = a.reset_index(drop=True)

    a["mName"] =""

    for i in tqdm(range(len(a))):

        before = a.loc[i,"item_no"]

        after = df_item.loc[before,"mName"]
        a.loc[i,"mName"] = after

        a = a.sort_values(by=["item_no"])   


    b= compare_prob2("958_0",a,probID,True).copy()


    b=b[["mName","test_result_count","probability","mExpectedProb","mProbDiff"]]
    #b=a[["mTime","mName","test_result_count","probability"]]
    b.rename(columns={
    #,'item_no':'합성등급'
    'mName':'합성대상'
    ,'test_result_count':'합성성공횟수'
    ,'probability':'합성성공확률(%)'
    ,'mExpectedProb':'기대확률(%)'
    ,'mProbDiff':'오차(%)'
    }, inplace = True)

    # if not os.path.exists(outputName):
    #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
    # else:
    #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    
    makeCsv()

    del a,b
    gc.collect()

    print(f'check_combine_mat() total-run-time : {time.time()-startTime:.4f} sec')

def check_craft():#probtest 5
    startTime = time.time()
    probID = 5

    outputName = f"{resultDir}/제작결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    targetList = str(df_target.loc[5,"mArg0"]).split(sep=';')

    print("***check_craft")

    for target in tqdm(targetList) :
        global df

        #print(f'try target ID : {target}')
        a = df[df["probability_type"] == 5]
        a = a[a["result_item_no"] == int(target)]
        #a = a[a["item_sub_no"] == target] #합성성공:1, 합성실패:0

        a = a.sort_values(by=["item_sub_no"],ascending=False)
        a = a.reset_index(drop=True)
        
        #print(a)

        a["mName"]=""
        a["mTime"]=""
        a["mCraftType"]=""
        a["mRarity"]=""
        #a["mSuccessCount"]=""
        #a["mSuccessRate"]=""
        #a["mGreatSuccessCount"]=""
        #a["mGreatSuccessRate"]=""

        #greatSuccessCountIndex = -1
        #successCountIndex = -1
        greatSuccessCount = 0
        successCount = 0
        for i in range(len(a)):
            mCraftType = a.loc[i,"item_sub_no"]

            if mCraftType == 0 :
                a = a.drop(a.index[i])
                continue #실패는 제외

            before = a.loc[i,"result_item_no"]
            #before1 = a.loc[i,"result_item_no"]

            after = df_item.loc[before,"mName"]
            after1 = df_item.loc[before,"mRarity"]
            a.loc[i,"mName"] = after
            a.loc[i,"mRarity"] = after1

            #a = a.sort_values(by=["item_no"])   


            if mCraftType == 2 :
                greatSuccessCount = int(a.loc[i,"test_result_count"])
            elif mCraftType == 1 :
                successCount = int(a.loc[i,"test_result_count"]) + greatSuccessCount
                a.loc[i,"test_result_count"] = successCount

            #시간표기용
            a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
        #print(a)
        #전체 확률 표기
        a["mProb"]=""
        for i in range(len(a)):
            tempProb0 = float(a.loc[i,"test_result_count"])*0.0001
            #tempProb1 = float(b.loc[i,"mGreatSuccessCount"])*0.001
            a.loc[i,"mProb"] = f"{tempProb0:.4f}"
            #b.loc[i,"mGreatSuccessRate"] = f"{tempProb1:.4f}"
        #print(a)
        b = compare_prob2("975_0",a,probID,False,targetColName="아이템 이름",refColName="제작 성공 확률(%)")
        #b= compare_prob(probID,a).copy()

        #b=a[["mTime","mName","probability","mSuccessRate","mGreatSuccessCount","mGreatSuccessRate"]]
        b = b.reset_index(drop=True)


        b=b[["mTime","mName","item_sub_no","test_result_count","mProb","mExpectedProb","mProbDiff"]]

        b= b.replace({"item_sub_no":1},"일반성공")
        b= b.replace({"item_sub_no":2},"대성공")

            
        b.rename(columns={
            'mTime':'수행시각'
        #,'item_no':'합성등급'
        ,'mName':'아이템명'
        ,'item_sub_no':'성공타입'
        ,'test_result_count':'성공횟수'
        ,'mProb':'성공확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)

        if not os.path.exists(outputName):
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        else:
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

        del a,b
        gc.collect()

    print(f'check_craft() total-run-time : {time.time()-startTime:.4f} sec')

def check_skill():#probtest 6 (인자 불필요)
    startTime = time.time()

    probTestNo = 6

    outputName = f"{resultDir}/스킬강화_{time.strftime('%y%m%d_%H%M%S')}.csv"

    global df

    a = df[df["probability_type"] == probTestNo]
    a = a[a["result_item_no"] == 1]
    a = a.reset_index(drop=True)

    a["mName"]=""
    a["mSuccessCount"]=""
    a["mSuccessRate"]=""
    a["mOrder"]=0

    for i in range(len(a)):

        try :
            before = a.loc[i,"item_no"]
            after = df_skill.loc[before,"mDesc"]
            a.loc[i,"mName"] = after
        except :
            print("no ID")
            
    b=a[["mTime","item_no","mName","test_result_count","probability"]]
    b = b.reset_index(drop=True)

    #b = compare_prob(6,b)

    #전체 확률 표기
    # #b["mProb"]=""
    # for i in range(len(b)):
    #     tempProb0 = float(b.loc[i,"test_result_count"])*0.001
    #     b.loc[i,"mSuccessRate"] = f"{tempProb0:.4f}"

        
    b.rename(columns={
        'mTime':'수행시각'
    ,'item_no':'스킬명'
    ,'mName':'강화대상'
    ,'test_result_count':'강화성공횟수'
    ,'probability':'강화성공확률(%)'
    ,'mExpectedProb':'기대확률(%)'
    ,'mProbDiff':'오차(%)'
    }, inplace = True)

    makeCsv(outputName,"스킬강화",b)

    del a,b
    gc.collect()

    print(f'check_craft() total-run-time : {time.time()-startTime:.4f} sec')

def check_change_mat():#probtest 7
    startTime = time.time()
    probID = 7
    probTestNo = 7

    outputName = f"{resultDir}/매테교체결과_{time.strftime('%y%m%d_%H%M%S')}.csv"
    #gachaID = input("변신 뽑기 ID 입력 > ")
    #print(df_target.loc[1,"mArg0"])
    targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')

    #c=pd.DataFrame(columns=["mTime","item_no","mRarity","mName","test_result_count"])
    
    for target in targetList :
        eachStartTime = time.time()
        
        global df
        print(f'try target ID : {target}')

        a = df[df["probability_type"] == probTestNo]
        #print(a)
        a = a[a["item_no"] == int(target)]
        a = a.head(4)
        a = a.reset_index(drop=True)

        a["mName"] =""
        a["mTime"]=""
        a["mRarity"]=""

        for i in range(len(a)):
            before0 = a.loc[i,"item_no"]
            before1 = a.loc[i,"result_item_no"]

            after0 = df_item.loc[before0,"mName"]
            after1 = df_item.loc[before1,"mName"]

            a.loc[i,"mName"] = f'{after0}>{after1}'

            # #정렬
            rarity = df_item.loc[before0,"mRarity"]
            a.loc[i,"mRarity"] = rarity
            # a = a.sort_values(by=["mRarity","result_item_no"])

            #시간표기용
            a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            

        b=a[["mTime","item_no","mRarity","mName","test_result_count","probability"]]
        #b["mProb"]=""
        # for i in range(len(b)):
        #     tempProb = float(b.loc[i,"test_result_count"])*0.001
        #     b.loc[i,"mProb"] = f"{tempProb:.4f}"
        #b = compare_prob(probID,b)
            
        b.rename(columns={
            'mTime':'수행시각'
        ,'item_no':'매터리얼교환내용'
        #,'mName':'아이템명'
        ,'test_result_count':'뽑기횟수'
        ,'probability':'뽑기확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)
    
        # c.append(b)
        # print(c)
        if not os.path.exists(outputName):
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        else:
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
            
        

        del a
        gc.collect()

        #print(f'success, target ID : {target}')


        #print(f'run-time : {time.time()-eachStartTime:.4f} sec')

    # print(c)
    # c = c.sort_values(by=["mRarity","item_no"])

    # if not os.path.exists(outputName):

    #     c.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
    # else:
    #     c.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        
    # del c
    # gc.collect()
    
    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_reinforce_item():#probtest 8 (인자 불필요)
    startTime = time.time()

    probID = 8

    outputName = f"{resultDir}/아이템강화(포인트미사용)결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    global df

    a = df[df["probability_type"] == probID]
    a = a[(a["result_item_no"]-a["item_sub_no"] == 1)]
    #a = a[a["item_sub_no"] == target] #합성성공:1, 합성실패:0
    a = a.reset_index(drop=True)
    #print(a)

    a["mName"]=""
    a["mTime"]=""
    a["mSuccessCount"]=""
    a["mSuccessRate"]=""
    a["mOrder"]=0

    for i in range(len(a)):

        try :
            before = a.loc[i,"item_no"]
            after = df_item.loc[before,"mName"]
            a.loc[i,"mName"] = after
        except :
            print("no ID")


        #시간표기용
        a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
    b=a[["mTime","item_no","mName","test_result_count","probability"]]
    b = b.reset_index(drop=True)


    #b = compare_prob(probID,b)
    b=a[["mTime","mName","test_result_count","probability"]]

    b.rename(columns={
    'mTime':'수행시각'
    #,'item_no':'아이템ID'
    ,'mName':'강화대상'
    ,'test_result_count':'강화성공횟수'
    ,'probability':'강화성공확률(%)'
    ,'mExpectedProb':'기대확률(%)'
    ,'mProbDiff':'오차(%)'
    }, inplace = True)


    if not os.path.exists(outputName):
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
    else:
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

    del a,b
    gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_reinforce_item_point():#probtest 9 (인자 불필요)
    startTime = time.time()

    probID = 9

    outputName = f"{resultDir}/아이템강화(포인트사용)결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    global df

    a = df[df["probability_type"] == probID]
    a = a[(a["result_item_no"]-a["item_sub_no"] == 1)]
    #a = a[a["item_sub_no"] == target] #합성성공:1, 합성실패:0
    a = a.reset_index(drop=True)
    #print(a)

    a["mName"]=""
    a["mTime"]=""
    a["mSuccessCount"]=""
    #a["mSuccessRate"]=""
    a["mOrder"]=0

    for i in range(len(a)):

        try :
            before = a.loc[i,"item_no"]
            after = df_item.loc[before,"mName"]
            a.loc[i,"mName"] = after
        except :
            print("no ID")


        #시간표기용
        a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
    b=a[["mTime","item_no","mName","test_result_count","probability"]]
    b = b.reset_index(drop=True)

    #b = compare_prob(probID,b)

    b=a[["mTime","mName","test_result_count","probability"]]
    b.rename(columns={
    'mTime':'수행시각'
    #,'item_no':'아이템ID'
    ,'mName':'강화대상'
    ,'test_result_count':'강화성공횟수'
    ,'probability':'강화성공확률(%)'
    ,'mExpectedProb':'기대확률(%)'
    ,'mProbDiff':'오차(%)'
    }, inplace = True)

    if not os.path.exists(outputName):
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
    else:
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

    del a,b
    gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_soul():#probtest 10 (인자 불필요)
    startTime = time.time()

    probID = 10

    outputName = f"{resultDir}/영혼부여결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    global df

    a = df[(df["probability_type"] == probID) & (df["result_item_no"] == 1)]
    #a = a[a["result_item_no"] == 1]
    #a = a[a["item_sub_no"] == target] #합성성공:1, 합성실패:0
    a = a.reset_index(drop=True)
    #print(a)

    a["mItemName"]=""
    a["mScrollName"]=""
    a["mTime"]=""
    a["mSuccessCount"]=""
    a["mRarity"]=""
    #a["mSuccessRate"]=""

    for i in range(len(a)):

        try :
            before0 = a.loc[i,"item_no"]
            before1 = a.loc[i,"item_sub_no"]
            
            after0 = df_item.loc[before0,"mName"]
            after1 = df_item.loc[before1,"mName"]
            rarity = df_item.loc[before0,"mRarity"]

            a.loc[i,"mItemName"] = after0
            a.loc[i,"mScrollName"] = after1
            a.loc[i,"mRarity"] = rarity
        except :
            print("no ID")


        #시간표기용
        a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
    b=a[["mTime","item_no","item_sub_no","mRarity","mItemName","mScrollName","test_result_count","probability"]]
    b = b.reset_index(drop=True)

    #b=compare_prob(probID,b)

    b.rename(columns={
    'mTime':'수행시각'
    #,'item_no':'아이템ID'
    ,'mItemName':'영혼부여대상무기'
    ,'mScrollName':'영혼석명'
    ,'test_result_count':'영혼부여성공횟수'
    ,'probability':'영혼부여성공확률(%)'
    ,'mExpectedProb':'기대확률(%)'
    ,'mProbDiff':'오차(%)'
    }, inplace = True)

    if not os.path.exists(outputName):
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
    else:
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

    del a,b
    gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_spot_tran():#probtest 12 (인자 불필요)
    startTime = time.time()

    probID = 12

    outputName = f"{resultDir}/변신휘장결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    global df

    a = df[(df["probability_type"] == probID)&(df["result_item_no"] == 1)]
    a = a.reset_index(drop=True)

    a["mTime"]=""
    a["mSuccessCount"]=""
    #a["mSuccessRate"]=""

    for i in range(len(a)):

        # try :
        #     before0 = a.loc[i,"item_no"]
        #     before1 = a.loc[i,"item_sub_no"]
        #     after0 = df_item.loc[before0,"mName"]
        #     after1 = df_item.loc[before1,"mName"]
        #     a.loc[i,"mItemName"] = after0
        #     a.loc[i,"mScrollName"] = after1
        # except :
        #     print("no ID")


        #시간표기용
        a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
    b=a[["mTime","probability_category","item_no","test_result_count","probability"]]
    b = b.sort_values(by=["probability_category","item_no"])
    b = b.reset_index(drop=True)
    
    #b = compare_prob(probID,b)


    b= b.replace({"probability_category":1},"유게네스의 휘장")
    b= b.replace({"probability_category":2},"벨제뷔트의 휘장")
    b= b.replace({"probability_category":3},"헤라켄의 휘장")
    b= b.replace({"probability_category":4},"가이아스의 휘장")
    b= b.replace({"probability_category":5},"유피테르의 휘장")
    #전체 확률 표기
    # for i in range(len(b)):
    #     tempProb0 = float(b.loc[i,"test_result_count"])*0.001
    #     b.loc[i,"mSuccessRate"] = f"{tempProb0:.4f}"
    

    b.rename(columns={
    'mTime':'수행시각'
    ,'item_no':'강화성공횟수'
    ,'probability_category':'휘장명'
    ,'item_no':'강화대상단계'
    ,'probability':'강화성공확률(%)'
    ,'mExpectedProb':'기대확률(%)'
    ,'mProbDiff':'오차(%)'
    }, inplace = True)

    if not os.path.exists(outputName):
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
    else:
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

    del a,b
    gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_spot_serv():#probtest 13 (인자 불필요)
    startTime = time.time()

    probID = 13

    outputName = f"{resultDir}/서번트휘장결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    global df

    a = df[(df["probability_type"] == probID)&(df["result_item_no"] == 1)]
    a = a.reset_index(drop=True)

    a["mTime"]=""
    a["mSuccessCount"]=""
    #a["mSuccessRate"]=""

    for i in range(len(a)):

        #시간표기용
        a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            
    b=a[["mTime","probability_category","item_no","test_result_count","probability"]]
    b = b.sort_values(by=["probability_category","item_no"])
    b = b.reset_index(drop=True)

    #b = compare_prob(probID,b)

    b= b.replace({"probability_category":1},"유게네스의 휘장")
    b= b.replace({"probability_category":2},"벨제뷔트의 휘장")
    b= b.replace({"probability_category":3},"헤라켄의 휘장")
    b= b.replace({"probability_category":4},"가이아스의 휘장")
    b= b.replace({"probability_category":5},"유피테르의 휘장")
    #전체 확률 표기
    # for i in range(len(b)):
    #     tempProb0 = float(b.loc[i,"test_result_count"])*0.001
    #     b.loc[i,"mSuccessRate"] = f"{tempProb0:.4f}"
    

    b.rename(columns={
    'mTime':'수행시각'
    ,'item_no':'강화성공횟수'
    ,'probability_category':'휘장명'
    ,'item_no':'강화대상단계'
    ,'probability':'뽑기확률(%)'
    ,'mExpectedProb':'기대확률(%)'
    ,'mProbDiff':'오차(%)'
    }, inplace = True)

    if not os.path.exists(outputName):
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
    else:
        b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
    

    del a,b
    gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_redraw_gacha(probID : int):#probtest 14,16 (인자 2 필요)
    """
    다시뽑기(뽑기로 획득)
    \nprobID 14=변신, 16=서번트
    """
    startTime = time.time()

    probName = ""
    if probID == 14:
        probName = "변신"
    elif probID == 16:
        probName = "서번트"

    outputName = f"{resultDir}/{probName}다시뽑기(뽑기)_{time.strftime('%y%m%d_%H%M%S')}.csv"

    targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')

    for target in tqdm(targetList) :
        cardID, redrawGroupNo    = target.split(sep='|')
        #print(f'try extract target... [cardID:{cardID}, redrawGroupNo:{redrawGroupNo}]')
        #print(probTestNo,cardID, redrawGroupNo)

        global df
        a = df[(df["probability_type"] == probID)&(df["item_no"] == int(cardID))]
        a = a.reset_index(drop=True)
        #print(a)

        a["mOriginName"]=""
        a["mResultName"]=""
        a["mRedrawGroupNo"]=""
        a["mGroupID"]=""

        for i in range(len(a)):

            #etc_json에서 추출
            tempStr = a.loc[i,"etc_json"]
            tempGet0 = re.search('RedrawGroupNo":(.+?)}', tempStr).group(1)
            a.loc[i,"mRedrawGroupNo"] = tempGet0

        a = a[(a["mRedrawGroupNo"] == redrawGroupNo)]
        a = a.reset_index(drop=True)

        if len(a) == 0 :
            print(f'no data... {cardID}|{redrawGroupNo}')
            emptyLogList.append(f'{cardID}|{redrawGroupNo}')
            continue

        for i in range(len(a)):
            if probID == 14 :
                df_redraw = df_tran.copy()
            else :
                df_redraw = df_serv.copy()
            
            #try:
                #카드명 적용

            try : 
                before0 = a.loc[i,"item_no"]
                before1 = a.loc[i,"result_item_no"]
                after0 = df_redraw.loc[before0,"mName"]
                after1 = df_redraw.loc[before1,"mName"]
                a.loc[i,"mOriginName"] = after0
                a.loc[i,"mName"] = after1

                #카드 정렬용
                rarity = df_redraw.loc[before1,"mRarity"]
                a.loc[i,"mRarity"] = rarity
                a = a.sort_values(by=["mRarity","result_item_no"])

                if probID == 14:
                    tempGroupID = df_redraw.loc[before1,"order"]
                    a.loc[i,"mGroupID"] = tempGroupID

                a = a.sort_values(by=["mRarity","mGroupID","mRarity"])

            except :
                emptyDataList.append('\n'+f"no data in {probName}list ID:{before1} ")
                a.loc[i,"mName"] = ""

        b=a[["mOriginName","mRedrawGroupNo","mName","test_result_count","probability"]]
        b = b.reset_index(drop=True)

        #webID = 0 
        if probID == 14 :
            rowID = [943,942]
            
        elif probID == 16:
            rowID = [951,950]
        webID = getWebID(target, rowID)
        b = compare_prob2(webID, b, probID, args = cardID)

        #b = compare_prob(probID, b, redrawGroupNo, after0)
        b.rename(columns={
        'mTime':'수행시각'
        #,'item_no':'아이템ID'
        ,'mOriginName':'교체대상카드명'
        ,'mRedrawGroupNo':'교체그룹ID'
        ,'mName':'교체된 카드명'
        ,'test_result_count':'뽑기횟수'
        ,'probability':'뽑기확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)


        # if not os.path.exists(outputName):
        #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        # else:
        #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        
        
        makeCsv(outputName,target,b)

        del a,b
        gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_redraw_combine(probID):#probtest 15, 17 (인자 2 필요)
    startTime = time.time()

    #probID = 15
    if probID == 15:
        probName = "변신"
    elif probID == 17:
        probName = "서번트"


    #outputName = f"{resultDir}/변신교체뽑기(합성획득)_{time.strftime('%y%m%d_%H%M%S')}.csv"
    outputName = f"{resultDir}/{probName}교체뽑기(합성)_{time.strftime('%y%m%d_%H%M%S')}.csv"

    targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')
    #targetList = targetList_before.split(sep='|')

    for target in tqdm(targetList) :
        cardID, rarity = target.split(sep='|')
        #print(f'try extract target... [cardID:{cardID}, rarity:{rarity}]')
        #print(probTestNo,cardID, redrawGroupNo)

        global df
        a = df[(df["probability_type"] == probID)&(df["item_no"] == int(cardID))&(df["item_sub_no"] == int(rarity))]
        a = a.reset_index(drop=True)
        #print(a)

        #a["mTime"]=""
        a["mOriginRarity"]=""
        a["mOriginName"]=""
        a["mResultName"]=""

        if len(a) == 0 :
            print(f'no data... {cardID}|{rarity}')

        for i in range(len(a)):
            try:
                if probID == 15 :
                    df_redraw = df_tran.copy()
                else :
                    df_redraw = df_serv.copy()
                #카드명 적용
                before0 = a.loc[i,"item_no"]
                before1 = a.loc[i,"result_item_no"]
                after0 = df_redraw.loc[before0,"mName"]
                after1 = df_redraw.loc[before1,"mName"]
                a.loc[i,"mOriginName"] = after0
                a.loc[i,"mResultName"] = after1

                #카드 정렬용
                tempRarity = df_redraw.loc[before1,"mRarity"]
                a.loc[i,"mRarity"] = tempRarity
                a = a.sort_values(by=["mRarity","result_item_no"])

            except :
                print(f"data 업데이트 요망... Type:변신,ID:{before0}or{before1} 누락")
                a.loc[i,"mOriginName"] = "BLANK"
                a.loc[i,"mResultName"] = "BLANK"

            #시간표기용
            #a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
        b=a[["mOriginName","mResultName","test_result_count","probability"]]
        b = b.reset_index(drop=True)
        #print(b)

        if probID == 15 :
            rowID = [943]
            
        elif probID == 17:
            rowID = [951]
        webID = getWebID(target, rowID)
        b = compare_prob2(webID, b, probID,args = cardID)

        
        # b= b.replace({"item_sub_no":2},"희귀합성")
        # b= b.replace({"item_sub_no":3},"영웅합성")
        # b= b.replace({"item_sub_no":4},"전설합성")

        # title = ""
        # rarity = int(rarity)
        # if rarity == 0 :
        #     title = "일반 합성"
        # elif rarity == 1 :
        #     title = "고급 합성"
        # elif rarity == 2 :
        #     title = "희귀 합성"
        # elif rarity == 3 :
        #     title = "영웅 합성"
        # elif rarity == 4 :
        #     title = "전설 합성"

        
        b.rename(columns={
        #'mTime':'수행시각'
        #,'item_no':'아이템ID'
        'mOriginName':'교체대상카드명'
        ,'mRedrawGroupNo':'합성종류'
        ,'mResultName':'교체된 카드명'
        ,'test_result_count':'뽑기횟수'
        ,'probability':'뽑기확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)

        # if not os.path.exists(outputName):
        #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        # else:
        #     b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

        makeCsv(outputName, target, b)

        del a,b
        gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_redraw_serv_gacha():#probtest 16 (인자 2 필요)
    startTime = time.time()

    probTestNo = 16

    outputName = f"{resultDir}/서번트교체뽑기(뽑기획득)결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')
    #targetList = targetList_before.split(sep='|')

    for target in targetList :
        cardID, redrawGroupNo = target.split(sep='|')
        print(f'try extract target... [cardID:{cardID}, redrawGroupNo:{redrawGroupNo}]')
        #print(probTestNo,cardID, redrawGroupNo)

        global df
        a = df[(df["probability_type"] == probTestNo)&(df["item_no"] == int(cardID))]
        a = a.reset_index(drop=True)
        #print(a)

        a["mTime"]=""
        a["mOriginName"]=""
        a["mResultName"]=""
        a["mRedrawGroupNo"]=""

        if len(a) == 0 :
            print(f'no data... {cardID}|{redrawGroupNo}')
        for i in range(len(a)):

            #etc_json에서 추출
            tempStr = a.loc[i,"etc_json"]
            tempGet0 = re.search('RedrawGroupNo":(.+?)}', tempStr).group(1)
            a.loc[i,"mRedrawGroupNo"] = tempGet0

        a = a[(a["mRedrawGroupNo"] == redrawGroupNo)]
        a = a.reset_index(drop=True)

        for i in range(len(a)):
            try:
                #카드명 적용
                before0 = a.loc[i,"item_no"]
                before1 = a.loc[i,"result_item_no"]
                after0 = df_serv.loc[before0,"mName"]
                after1 = df_serv.loc[before1,"mName"]
                a.loc[i,"mOriginName"] = after0
                a.loc[i,"mResultName"] = after1

                #카드 정렬용
                rarity = df_serv.loc[before1,"mRarity"]
                a.loc[i,"mRarity"] = rarity
                a = a.sort_values(by=["mRarity","result_item_no"])

            except :
                print(f"data 업데이트 요망... Type:서번트,ID:{before0}or{before1} 누락")
                a.loc[i,"mOriginName"] = "BLANK"
                a.loc[i,"mResultName"] = "BLANK"
            #시간표기용
            a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
        b=a[["mTime","mOriginName","mRedrawGroupNo","mResultName","test_result_count","probability"]]
        b = b.reset_index(drop=True)

        
        b.rename(columns={
        'mTime':'수행시각'
        #,'item_no':'아이템ID'
        ,'mOriginName':'교체대상카드명'
        ,'mRedrawGroupNo':'교체그룹ID'
        ,'mResultName':'교체된 카드명'
        ,'test_result_count':'봅기횟수'
        ,'probability':'뽑기확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)


        if not os.path.exists(outputName):
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        else:
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

        del a,b
        gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_redraw_serv_combine():#probtest 17 (인자 2 필요)
    startTime = time.time()

    probTestNo = 17

    outputName = f"{resultDir}/서번트교체뽑기(합성획득)결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')
    #targetList = targetList_before.split(sep='|')

    for target in targetList :
        cardID, rarity = target.split(sep='|')
        print(f'try extract target... [cardID:{cardID}, rarity:{rarity}]')
        #print(probTestNo,cardID, redrawGroupNo)

        global df
        a = df[(df["probability_type"] == probTestNo)&(df["item_no"] == int(cardID))&(df["item_sub_no"] == int(rarity))]
        a = a.reset_index(drop=True)
        #print(a)

        a["mTime"]=""
        a["mOriginRarity"]=""
        a["mOriginName"]=""
        a["mResultName"]=""
        #a["mRedrawGroupNo"]=""

        # for i in range(len(a)):

        #     #etc_json에서 추출
        #     tempStr = a.loc[i,"etc_json"]
        #     tempGet0 = re.search('Rarity":(.+?)}', tempStr).group(1)
        #     a.loc[i,"mOriginRarity"] = tempGet0

        # a = a[(a["mOriginRarity"] == rarity)]
        # a = a.reset_index(drop=True)

        for i in range(len(a)):
            try:
                #카드명 적용
                before0 = a.loc[i,"item_no"]
                before1 = a.loc[i,"result_item_no"]
                after0 = df_serv.loc[before0,"mName"]
                after1 = df_serv.loc[before1,"mName"]
                a.loc[i,"mOriginName"] = after0
                a.loc[i,"mResultName"] = after1

                #카드 정렬용
                tempRarity = df_serv.loc[before1,"mRarity"]
                a.loc[i,"mRarity"] = tempRarity
                a = a.sort_values(by=["mRarity","result_item_no"])
            except:
                print(f"data 업데이트 요망... Type:서번트,ID:{before0}or{before1} 누락")
                a.loc[i,"mOriginName"] = "BLANK"
                a.loc[i,"mResultName"] = "BLANK"
            #시간표기용
            a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
        b=a[["mTime","item_no","mOriginName","item_sub_no","result_item_no","mResultName","test_result_count","probability"]]
        b = b.reset_index(drop=True)

        
        b= b.replace({"item_sub_no":2},"희귀합성")
        b= b.replace({"item_sub_no":3},"영웅합성")
        b= b.replace({"item_sub_no":4},"전설합성")

        b.rename(columns={
        'mTime':'수행시각'
        #,'item_no':'아이템ID'
        ,'mOriginName':'교체대상카드명'
        ,'mRedrawGroupNo':'합성종류'
        ,'mResultName':'교체된 카드명'
        ,'test_result_count':'뽑기횟수'
        ,'probability':'뽑기확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)

        if not os.path.exists(outputName):
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        else:
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

        del a,b
        gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_reinforce_slot():#probtest 18 (인자 필요)
    startTime = time.time()

    probTestNo = 18

    outputName = f"{resultDir}/슬롯강화결과_{time.strftime('%y%m%d')}.csv"

    targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')
    #targetList = targetList_before.split(sep='|')

    for target in targetList :
        print(f'try extract target... [typeNo:{target}]')
        #print(probTestNo,cardID, redrawGroupNo)

        global df
        a = df[(df["probability_type"] == probTestNo)&(df["probability_category"] == int(target))&(df["result_item_no"] == 1)]
        a = a.reset_index(drop=True)
        #print(a)

        a["mTime"]=""
        a["mStep"]=""

        for i in range(len(a)):

            #etc_json에서 추출
            tempStr = a.loc[i,"etc_json"]
            tempGet0 = re.search('Step":(.+?),', tempStr).group(1)
            a.loc[i,"mStep"] = int(tempGet0) + 1

        # a = a[(a["mOriginRarity"] == rarity)]
        # a = a.reset_index(drop=True)

        for i in range(len(a)):

            #시간표기용
            a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
        b=a[["mTime","probability_category","item_no","item_sub_no","mStep","test_result_count","probability"]]
        b = b.reset_index(drop=True)



        b.loc[((b.probability_category == 0) & (b.item_no == 0)), "item_no"] = "무기"
        b.loc[((b.probability_category == 0) & (b.item_no == 1)), "item_no"] = "투구"
        b.loc[((b.probability_category == 0) & (b.item_no == 2)), "item_no"] = "갑옷"
        b.loc[((b.probability_category == 0) & (b.item_no == 4)), "item_no"] = "신발"
        b.loc[((b.probability_category == 0) & (b.item_no == 7)), "item_no"] = "반지I"
        b.loc[((b.probability_category == 0) & (b.item_no == 8)), "item_no"] = "반지II"
        b.loc[((b.probability_category == 0) & (b.item_no == 9)), "item_no"] = "목걸이"
        b.loc[((b.probability_category == 0) & (b.item_no == 10)), "item_no"] = "벨트"
        
        b.loc[((b.probability_category == 2) & (b.item_no == 0)), "item_no"] = "숙련"
        b.loc[((b.probability_category == 2) & (b.item_no == 1)), "item_no"] = "영혼"
        b.loc[((b.probability_category == 2) & (b.item_no == 2)), "item_no"] = "수호"
        b.loc[((b.probability_category == 2) & (b.item_no == 3)), "item_no"] = "파괴"
        b.loc[((b.probability_category == 2) & (b.item_no == 4)), "item_no"] = "생명"
        
        b= b.replace({"probability_category":0},"장비슬롯")
        b= b.replace({"probability_category":2},"매터리얼슬롯")
        
        b= b.replace({"item_sub_no":0},"일반")
        b= b.replace({"item_sub_no":1},"고급")
        b= b.replace({"item_sub_no":2},"희귀")
        b= b.replace({"item_sub_no":3},"영웅")
        b= b.replace({"item_sub_no":4},"전설")
        b= b.replace({"item_sub_no":5},"초월")
        #df = df.convert_objects(convert_numeric=True)

        #b=b.convert_objects("mStep",convert_numeric=True)
        #b["mStep"] = int(b["mStep"]) + 1
        b.rename(columns={
        'mTime':'수행시각'
        ,'probability_category':'슬롯타입'
        ,'item_no':'슬롯명'
        ,'item_sub_no':'등급'
        ,'mStep':'단계'
        ,'test_result_count':'강화성공횟수'
        ,'probability':'강화성공확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)

        if not os.path.exists(outputName):
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        else:
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

        del a,b
        gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_reinforce_slot_ancient():#probtest 19 (인자 필요)
    startTime = time.time()

    probTestNo = 19

    outputName = f"{resultDir}/슬롯강화결과(고대주문서)_{time.strftime('%y%m%d')}.csv"

    targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')
    #targetList = targetList_before.split(sep='|')

    for target in targetList :
        print(f'try extract target... [typeNo:{target}]')
        #print(probTestNo,cardID, redrawGroupNo)

        global df
        a = df[(df["probability_type"] == probTestNo)&(df["probability_category"] == int(target))&(df["result_item_no"] == 1)]
        a = a.reset_index(drop=True)
        #print(a)

        a["mTime"]=""
        a["mStep"]=""

        for i in range(len(a)):

            #etc_json에서 추출
            tempStr = a.loc[i,"etc_json"]
            tempGet0 = re.search('Step":(.+?),', tempStr).group(1)
            a.loc[i,"mStep"] = int(tempGet0) + 1

        # a = a[(a["mOriginRarity"] == rarity)]
        # a = a.reset_index(drop=True)

        for i in range(len(a)):

            #시간표기용
            a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
        b=a[["mTime","probability_category","item_no","item_sub_no","mStep","test_result_count","probability"]]
        b = b.reset_index(drop=True)



        b.loc[((b.probability_category == 0) & (b.item_no == 0)), "item_no"] = "무기"
        b.loc[((b.probability_category == 0) & (b.item_no == 1)), "item_no"] = "투구"
        b.loc[((b.probability_category == 0) & (b.item_no == 2)), "item_no"] = "갑옷"
        b.loc[((b.probability_category == 0) & (b.item_no == 4)), "item_no"] = "신발"
        b.loc[((b.probability_category == 0) & (b.item_no == 7)), "item_no"] = "반지I"
        b.loc[((b.probability_category == 0) & (b.item_no == 8)), "item_no"] = "반지II"
        b.loc[((b.probability_category == 0) & (b.item_no == 9)), "item_no"] = "목걸이"
        b.loc[((b.probability_category == 0) & (b.item_no == 10)), "item_no"] = "벨트"
        
        b.loc[((b.probability_category == 2) & (b.item_no == 0)), "item_no"] = "숙련"
        b.loc[((b.probability_category == 2) & (b.item_no == 1)), "item_no"] = "영혼"
        b.loc[((b.probability_category == 2) & (b.item_no == 2)), "item_no"] = "수호"
        b.loc[((b.probability_category == 2) & (b.item_no == 3)), "item_no"] = "파괴"
        b.loc[((b.probability_category == 2) & (b.item_no == 4)), "item_no"] = "생명"
        
        b= b.replace({"probability_category":0},"장비슬롯")
        b= b.replace({"probability_category":2},"매터리얼슬롯")
        
        b= b.replace({"item_sub_no":0},"일반")
        b= b.replace({"item_sub_no":1},"고급")
        b= b.replace({"item_sub_no":2},"희귀")
        b= b.replace({"item_sub_no":3},"영웅")
        b= b.replace({"item_sub_no":4},"전설")
        b= b.replace({"item_sub_no":5},"초월")
        #df = df.convert_objects(convert_numeric=True)

        #b=b.convert_objects("mStep",convert_numeric=True)
        #b["mStep"] = int(b["mStep"]) + 1

        b.rename(columns={
        'mTime':'수행시각'
        ,'probability_category':'슬롯타입'
        ,'item_no':'슬롯명'
        ,'item_sub_no':'등급'
        ,'mStep':'단계'
        ,'test_result_count':'뽑기횟수'
        ,'probability':'뽑기확률(%)'
        ,'mExpectedProb':'기대확률(%)'
        ,'mProbDiff':'오차(%)'
        }, inplace = True)

        if not os.path.exists(outputName):
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
        else:
            b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
        

        del a,b
        gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_engrave():#probtest 11 (인자 필요)
    startTime = time.time()

    probTestNo = 11

    outputName = f"{resultDir}/각인결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    targetList = str(df_target.loc[probTestNo,"mArg0"]).split(sep=';')

    for target in targetList :
        print(f'extracting target... [itemID:{target}]')
        #print(probTestNo,cardID, redrawGroupNo)

        for i in range(0,2):

            global df

            if i == 0 :
                scrollID = 700
            else : 
                scrollID = 701

            a = df[(df["probability_type"] == probTestNo)&(df["item_no"] == int(target))&(df["item_sub_no"] == scrollID)]
            a = a.reset_index(drop=True)
            #print(a)

            a["mTime"]=""
            a["mItemName"]=""
            a["mSlainType"]=""
            a["mSlainTypeName"]=""
            a["mAbilityType"]=""
            a["mAbilityTypeName"]=""
            a["mStatLevel"]=""
            a["mNormalCount"]=""
            a["mBlessCount"]=""
            a["mStatName"]=""
            

            for i in range(len(a)):
                #print(i)
                defaultTypeList = [2,80] #공속 미포함
                
                #etc_json에서 추출
                tempStr = a.loc[i,"etc_json"]
                tempGet0 = re.search('SlaintType":(.+?),', tempStr).group(1)
                tempGet1 = re.search('AbilityType":(.+?)}', tempStr).group(1)
                a.loc[i,"mSlainType"] = int(tempGet0)
                a.loc[i,"mAbilityType"] = int(tempGet1)

                before0 = a.loc[i,"item_no"]
                after0 = df_item.loc[before0,"mName"]
                a.loc[i,"mItemName"] = after0

                before1 = a.loc[i,"mSlainType"]
                after1 = df_engraveSlain.loc[before1,"mName"]
                a.loc[i,"mSlainTypeName"] = after1

                before2 = a.loc[i,"mAbilityType"]
                after2 = df_engraveAbility.loc[before2,"mName"]
                a.loc[i,"mAbilityTypeName"] = after2

                statLevel = a.loc[i,"result_item_no"]                

                optionID = int( df_item.loc[df_item["mName"] == after0 , "mSubType"])
                if optionID in defaultTypeList :
                    a=a.replace({"probability_category":0},"1단계 옵션")
                    a=a.replace({"probability_category":1},"2단계 옵션(단검)")
                    a=a.replace({"probability_category":2},"3단계 옵션")
                    a=a.replace({"probability_category":3},"4단계 옵션")
                    a=a.replace({"probability_category":4},"5단계 옵션")
                else :
                    a=a.replace({"probability_category":0},"1단계 옵션")
                    a=a.replace({"probability_category":1},"2단계 옵션(공격 속도)(단검 외)")
                    a=a.replace({"probability_category":2},"3단계 옵션")
                    a=a.replace({"probability_category":3},"4단계 옵션")
                    a=a.replace({"probability_category":4},"5단계 옵션")

                #||일부 능력치 계수 보정■■■■■■■■■■■■■■■■■■■■■■■■■■■■■||#
                if int(statLevel) < 0 :
                    statLevel = int(statLevel)*(-1)

                if "치명타 확률" in after2 :
                    statLevel *= 0.5
                    statLevel = f'{round(statLevel, 2)}'
                elif "최대 소지 무게" in after2 :
                    statLevel *= 0.01
                    statLevel = round(statLevel)
                elif "마나 소모 감소율" in after2 :
                    statLevel *= 0.01
                    statLevel = f'{round(statLevel, 2)}'
                elif "흡수 확률" in after2 :
                    statLevel *= 0.01
                    statLevel = f'{round(statLevel, 2)}'
                elif "흡수 확률" in after2 :
                    statLevel *= 0.01
                    statLevel = f'{round(statLevel, 2)}'
                elif "골드 획득량" in after2 :
                    statLevel *= 0.01
                    statLevel = f'{round(statLevel, 2)}'
                elif "경험치 획득량" in after2 :
                    statLevel *= 0.01
                    statLevel = f'{round(statLevel, 2)}'
                elif "아이템 드랍률" in after2 :
                    statLevel *= 0.01
                    statLevel = f'{round(statLevel, 2)}'
                elif "계약 효과 증가" in after2 :
                    statLevel *= 0.01
                    statLevel = f'{round(statLevel, 2)}'
                elif "포션 회복률" in after2 :
                    statLevel *= 0.01
                    statLevel = f'{round(statLevel, 2)}'
                elif "공격 속도" in after2 :
                    statLevel *= 0.1
                    statLevel = f'{round(statLevel, 1)}'

                #||■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■||#
                a.loc[i,"mStatLevel"] = statLevel


                if before1 != 0 :
                    a.loc[i,"mStatName"] = f'[{after1}]{after2} +{statLevel}'
                else :
                    a.loc[i,"mStatName"] = f'{after2} +{statLevel}'

        


            # a = a[(a["mOriginRarity"] == rarity)]
            # a = a.reset_index(drop=True)

            for i in range(len(a)):

                #시간표기용
                a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                    
            a = a.sort_values(by=["probability_category","item_sub_no","mAbilityType","mSlainType","result_item_no"])

            b=a[["item_sub_no","mItemName","probability_category","mAbilityType","mSlainType","mSlainTypeName","mAbilityTypeName","mStatLevel","mStatName","test_result_count","probability"]]
            b = b.reset_index(drop=True)

            #try : 
            gachaID = int(target)
            #print(gachaID)
            colNum = df_probInfo.columns[df_probInfo.eq(gachaID).any()][0]
            row = df_probInfo[df_probInfo[colNum] == gachaID].index[0]
            title = df_probInfo.loc[df_probInfo[colNum] == gachaID, 'title'].iloc[0]
            webID = f"{row}_{str(colNum).split('.')[0]}"
            b=compare_prob2(webID,b,11).copy()
            #except :
            #   emptyProbList.append(f"11|{target}|{title}|{row}|{colNum}")
            
            # b= b.replace({"probability_category":0},"1")
            # b= b.replace({"probability_category":1},"2")
            # b= b.replace({"probability_category":2},"3")
            # b= b.replace({"probability_category":3},"4")
            # b= b.replace({"probability_category":4},"5")

            # b= b.replace({"item_sub_no":700},"일반 각인")
            # b= b.replace({"item_sub_no":701},"축복 각인")
            
            # b.rename(columns={
            # 'mTime':'수행시각'
            # #,'probability_category':'슬롯타입'
            # #,'item_no':'슬롯명'
            # ,'item_sub_no':'각인분류'
            # ,'mItemName':'장비명'
            # ,'probability_category':'옵션번호'
            # ,'mSlainTypeName':'슬레인타입'
            # ,'mAbilityTypeName':'능력치'
            # ,'mStatLevel':'세부수치'
            # ,'mStatName':'능력치명'
            # ,'test_result_count':'뽑기횟수'
            # ,'probability':'뽑기확률(%)'
            # ,'mExpectedProb':'기대확률(%)'
            # ,'mProbDiff':'오차(%)'
            # }, inplace = True)
            
            if not os.path.exists(outputName):
                b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",mode='w')
            else:
                b.to_csv(outputName,sep=',',index=False,encoding="utf-8-sig",header=False,mode='a')
            

            del a,b
            gc.collect()

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

def check_redraw_tran_gacha_all():#probtest 14 (인자 불필요 - 전체)
    startTime = time.time()

    probID = 14

    outputName = f"{resultDir}/변신교체뽑기(뽑기획득)결과_{time.strftime('%y%m%d_%H%M%S')}.csv"

    global df

    df_temp = df[(df['probability_type']==probID)]
    df_temp = df_temp.reset_index(drop=True)
    print(df_temp)
    df_temp['temp0'] = ""
    for i in range(len(df_temp)):
        print(f'{i}/{len(df_temp)}', end = '\r')
        df_temp.loc[i,'temp0'] = df_temp.loc[i,'etc_json']
    #df_temp['temp1'] = df_temp['etc_json']
    #df_temp['temp0'] = df_temp['temp0'].str.replace('{"value":{"RedrawGroupNo":', '')
    #df_temp['temp0'] = df_temp['temp0'].str.replace('}}', '')

    df_temp1 = df_temp.drop_duplicates(subset='temp0')
    #groupList = df_temp1['temp0'].astype('int')
    #print(groupList)
    #df_temp['temp0'] = df_temp['temp0'].str.replace('}}', '')
    #df_temp = df_temp.replace('(.*){"value":{"RedrawGroupNo":(.*)', r'\1\2', regex=True)
    #df_temp = df_temp.replace('(.*)}}(.*)', r'\1\2', regex=True)

    #print(df_temp)
    #targetList = str(df_target.loc[probID,"mArg0"]).split(sep=';')
    #targetList = targetList_before.split(sep='|')

    # for target in targetList :
    #     cardID, redrawGroupNo = target.split(sep='|')
    #     print(f'try extract target... [cardID:{cardID}, redrawGroupNo:{redrawGroupNo}]')
    #     #print(probTestNo,cardID, redrawGroupNo)

    #     global df
    #     a = df[(df["probability_type"] == probID)&(df["item_no"] == int(cardID))]
    #     a = a.reset_index(drop=True)
    #     #print(a)

    #     a["mTime"]=""
    #     a["mOriginName"]=""
    #     a["mResultName"]=""
    #     a["mRedrawGroupNo"]=""
    #     a["mGroupID"]=""

    #     for i in range(len(a)):

    #         #etc_json에서 추출
    #         tempStr = a.loc[i,"etc_json"]
    #         tempGet0 = re.search('RedrawGroupNo":(.+?)}', tempStr).group(1)
    #         a.loc[i,"mRedrawGroupNo"] = tempGet0

    #     a = a[(a["mRedrawGroupNo"] == redrawGroupNo)]
    #     a = a.reset_index(drop=True)

    #     for i in range(len(a)):
    #         try:
    #             #카드명 적용
    #             before0 = a.loc[i,"item_no"]
    #             before1 = a.loc[i,"result_item_no"]
    #             after0 = df_tran.loc[before0,"mName"]
    #             after1 = df_tran.loc[before1,"mName"]
    #             a.loc[i,"mOriginName"] = after0
    #             a.loc[i,"mResultName"] = after1

    #             #카드 정렬용
    #             rarity = df_tran.loc[before1,"mRarity"]
    #             a.loc[i,"mRarity"] = rarity
    #             a = a.sort_values(by=["mRarity","result_item_no"])

    #             tempGroupID = df_tran.loc[before1,"mGroupID"]
    #             a.loc[i,"mGroupID"] = tempGroupID

    #         except :
    #             print(f"data 업데이트 요망... Type:변신,ID:{before0}or{before1} 누락")
    #             a.loc[i,"mOriginName"] = "BLANK"
    #             a.loc[i,"mResultName"] = "BLANK"

    #         a = a.sort_values(by=["mRarity","mGroupID","mRarity"])

    #         #시간표기용
    #         a.loc[i,"mTime"]= time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
                
    #     b=a[["mTime","mOriginName","mRedrawGroupNo","mResultName","test_result_count","probability"]]
    #     b = b.reset_index(drop=True)

    #     b = compare_prob(probID, b, redrawGroupNo, after0)
    #     b.rename(columns={
    #     'mTime':'수행시각'
    #     #,'item_no':'아이템ID'
    #     ,'mOriginName':'교체대상카드명'
    #     ,'mRedrawGroupNo':'교체그룹ID'
    #     ,'mResultName':'교체된 카드명'
    #     ,'test_result_count':'뽑기횟수'
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

    print(f'total-run-time : {time.time()-startTime:.4f} sec')

if __name__ == "__main__" : 
    #check_gacha()                      #230307 #230330
    #check_combine_card(2)              #230307
    #check_combine_card(3)              #230307
    #check_combine_mat()                #230307
    #check_craft()                      #230307
    #check_skill()                      #진행중
    #check_change_mat()         
    #check_reinforce_item()     
    #check_reinforce_item_point()  
    #check_soul()   
    #check_engrave()
    #check_spot_tran()                   #변신/서번트합치자
    #check_spot_serv()  
    check_redraw_gacha(14)             #230307
    check_redraw_combine(15)      #230320 5|3,5|4케이스 로그 누락(사방신 변신) > 아마 3월말에하면 될것으로 추측
    #check_redraw_gacha(16)             #230317
    #check_redraw_combine(17)      #230320
    #check_reinforce_slot()
    #check_reinforce_slot_ancient()
    
    
    #input("press any key to exit...")
    
    
    emptyStr = (f"로그 추가 필요 : {len(emptyLogList)}건"+"\n" + "\n".join(emptyLogList))
    emptyStr += (f"\n데이터 추가 필요 : {len(emptyDataList)}건"+"\n" + "\n".join(emptyDataList))
    emptyStr += (f"\n고지표 업데이트 필요 : {len(emptyProbList)}건"+"\n" + "\n".join(emptyProbList))
    #check_redraw_tran_gacha_all()

    emptyFileName = f"{resultDir}/emptyList.txt"
    with open(emptyFileName, "a") as f:
        f.write(emptyStr)