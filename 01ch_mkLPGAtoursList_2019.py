#! C:\Users\goto1\AppData\Local\Programs\Python\Python37\python.exe
#! python3
import sys, pyperclip, time
import pandas as pd
#--
import datetime, re, pprint, codecs, csv, pickle
from _my import getHtmlText
from _my import df_to_csvTable, csvTable_to_df
from _my import excel_to_csvTable, csvTable_to_excel
from _my import mk5chText, mkReadersBoard, mgReadersBoard, getTourListDf, getTourListDfMulti
from _my import changeTourListDf2Multi

# 0ch 作成メモ 2019/9/16 マスターしたと思えた日は、、、
# main の構造は一緒だが、URLの並びでループするのではないことから、でファイルを独立させた。
# 従って txtFilePath = 'data\\0ch_urlList.txt' を使わない

STAGE1 = 0b00000001
STAGE2 = 0b00000010
STAGE3 = 0b00000100
STAGEShort = 0b01000100

#STAGE = STAGE1 | STAGE2 | STAGEShort
STAGE = STAGE1 |STAGE2 #| STAGEShort

def func(row):
    return nameRef[row['Id']]

outFileNameA = 'data\\LPGA_toursPast.xlsx'
thisYear = 2019
year1st = {'Regular': 1967,  'Stepup': 1991}
urls = {'Regular': 'https://www.lpga.or.jp/tournament/lpgatour/', 
        'Stepup': 'https://www.lpga.or.jp/tournament/stepup/'}

if STAGE & STAGEShort:
    # 範囲を狭めてテストしたいとき
    outFileNameA = 'data\\a_shortPast.xlsx' 
    thisYear = 2019
    year1st = {'Regular': 2017}

#if __name__ == "__main__":         # ☆彡 起動 このファイルで起動されたかチェック
#if False: #True: # 前半分
if STAGE & STAGE1:
    tourDfList = {}
    nameRef = {}

    for tour in year1st:     #urls: 感覚的にこっちが良い、と変えたが Short ステージが出来ない
        y1 = year1st[tour]
        years = list(reversed(range(y1, thisYear))) # ☆彡 配列 初期化 逆順 list を付けないと
        for year in years:                      # generator（for ループで使うと 1回でおしまい）
            yyyy = str(year)
            htmlFileName = 'data\\LPGA'+ yyyy + '_tours' + tour[0] + '.html'
            url = urls[tour] + yyyy
            
            #1 ループの確認
            #print(url, outFileName)

            #2
            # ファイルをひとつにして、getHtmlText
            htmlText = getHtmlText(url, htmlFileName, False, False)
            
            # どんな df が採れるかをチェック
            #dfs = pd.read_html(htmlText)
            #showDfs(dfs)
            #dfs[0].to_excel(outFileName.replace('.html', '.xlsx'))
            
            # 欲しい df になるようプログラミングしてエクセルで確認
            #df = getTourListDf(htmlText, yyyy); df = changeTourListDf2Multi(df, yyyy)
            df = getTourListDfMulti(htmlText, yyyy, nameRef)   # ☆彡 リストはリファレンス渡し
            #showDfs([df])
            #df.to_excel(outFileName.replace('.html', '.xlsx'))
            #3 リストの作成
            try:
                tourDfList[yyyy].append(df) #tour[0]) #
            except:
                tourDfList[yyyy] = [df]  #tour[0]] #
    #3 リストの処理
    #pprint.pprint(tourDfList) 
    #pprint.pprint(nameRef)
    dfs = []
    for yyyy in tourDfList:                    # データ構造とアルゴリズムが調和して美しい！！
        #print(yyyy, tourDfList[yyyy])
        df = pd.concat(tourDfList[yyyy])
        dfs.append(df)
    df = pd.concat(dfs, axis=1)                 #, sort=False)  #効かなかった、、、 

    df2 = df.reset_index()                      # ☆彡 df 起点に帰る。重要。csv に戻さないで済む！！
    df2.insert(1, 'Name', '')                   # ☆彡 df 列 挿入
    df2['Name'] = df2.apply(func, axis=1)       # ☆彡 df 他の列の値を利用して、値を埋める
    #df2.index.name = 'Id'
    df = df2.set_index(['Id', 'Name', 'Item'])  # ☆彡 df MultiIndex マルチインデックス化は簡単 
    df.to_excel(outFileNameA)

#else:                                 # 後ろ半分 # 上記で書いた excel ファイルも、、、、
if STAGE & STAGE2:
    df0 = pd.read_excel(outFileNameA)           # ☆彡 df excel から読んだらいつもの起点、、、の手前、
    #df2 = df0.fillna(method='ffill')   # ☆彡 df MultiIndex 結合セル（NaN混じり）を ffill
    df2 = df0.copy()                    # ☆彡 下の式を代入してしまうと、一行だけの DF になってしまう。
    df2['Id'].fillna(method='ffill',  inplace=True)    # ☆彡 df 部分的に ffill ちゃんとした仕様？ 
    df2['Name'].fillna(method='ffill',  inplace=True)  # ☆彡 df 部分的に ffill 
    # ※ 結合セルだった箇所まで埋めてはくれない（現時点では?）。上記までやって起点。
    # df = df2.set_index(['Id', 'Name', 'Item'])  # これは必要になったときに行う

    tourDfList = {}
    nameRef = {}
    for tour in year1st:     #urls: 感覚的にこっちが良い、と変えたが Short ステージが出来ない
        yyyy = str(thisYear)
        htmlFileName = 'data\\LPGA'+ yyyy + '_tours' + tour[0] + '.html'
        url = urls[tour] + yyyy
        htmlText = getHtmlText(url, htmlFileName, False, False) # 終わったら前半を True にする
        df = getTourListDfMulti(htmlText, yyyy, nameRef)   # ☆彡 リストはリファレンス渡し
        try:
            tourDfList[yyyy].append(df) #tour[0]) #
        except:
            tourDfList[yyyy] = [df]  #tour[0]] #

    df = pd.DataFrame({}, index=df0.index)  # df0 の形（ffillされてなくて重複しない）が好都合
    df['Name'] = df0['Name']
    df['Id'] = df0['Id']
    df = df.dropna(how="all")         # ☆彡 行or列の削除 df NaN 混じり（any）／全部 NaN（all）
    nameDf = df.set_index('Name')
    #nameDf.to_excel('data\\a_nameDf.xlsx')

    iDs = {}
    df = pd.concat(tourDfList[yyyy])
    df = df.reset_index()
    for i in range(len(df.index)):
        id = df.iat[i, 0]
        if 'dmy' in id:
            name = nameRef[id]
            try:
                foundId = nameDf.at[name, 'Id']
                df.iat[i, 0] = foundId
                nameRef[foundId] = name
                id = foundId
            except:
                foundId = 'みつかりません'
                print(id, foundId, nameRef[id])
                continue
        try:
            iDs[id]
        except:
            iDs[id] = True 
    df.insert(1, 'Name', '')                   # ☆彡 df 列 挿入
    df['Name'] = df.apply(func, axis=1)       # ☆彡 df 他の列の値を利用して、値を埋める
    df3 = df.set_index(['Id', 'Name', 'Item'])  # ☆彡 df MultiIndex マルチインデックス化は簡単 
    #df3.to_excel('data\\a_thisYear.xlsx')

    dfs = []
    #for id, sdf in df.groupby('Id'):     # とても便利だが id がソートされてしまうのが余計なお世話
    for id in iDs:
        sdf = df.groupby('Id').get_group(id)
        sdfs = [sdf.set_index(['Id', 'Name', 'Item'])]
        try:
            sdf2 = df2.groupby('Id').get_group(id)
            sdfs.append(sdf2.set_index(['Id', 'Name', 'Item']))
        except:
            pass
        sdf2 = pd.concat(sdfs, axis=1)  #
        dfs.append(sdf2)                #.reset_index()) しなくてOKそう。 
    df = pd.concat(dfs, sort=False)     # ☆彡 df concat にて タイトル行をソートしない
    #df = df.set_index(['Id', 'Name', 'Item'])  
    df.to_excel(outFileNameA.replace('Past.xlsx', yyyy + '.xlsx'))
    pass # これから書くコード

#--------------------------------------------------------------------------
# 残件 pickle
# そもそも if True なんてしなくても、本来のコードの構造と一緒にmasutaすべき
#
#if True: #False: # 開発中、動かすコードを切り替えたいときに上へ ex. 前半分 vs 後ろ半分
#    with open('data\\LPGA_tourNames.bin','wb') as f:
#        pickle.dump(nameRef,f)
#    # 処理再開
#else: # 途中からやれるように、、、と思ったが pickle が動かない。残件
#    with open('data\\LPGA_tourNames.bin','rb') as f:
#        pickle.load(f)
#    pprint.pprint(nameRef)
#--------------------------------------------------------------------------
# tips 
# else の上なら同じ名前の列を複数、drop できる。
# else の下だと、同じ名前だった列に .番号 が付いてしまう。
#
# 2019/9/15 の残件
# dfAll からスマートに欲しい df を作る
# もしくは、adAll を作る前にスマートに dfs を作る
#--------------------------------------------------------------------------
# 以下はできるが非採用。multiindex に方針変更することにした。
#    dfAll = dfAll.drop('days', axis=1)
#    dfAll = dfAll.drop('Place', axis=1)
#    dfAll = dfAll.drop('Plice', axis=1)
#    dfAll = dfAll.drop('Winner', axis=1)
#    dfAll = dfAll.drop('URL', axis=1)
#    dfAll.to_excel(outFileName.replace('All.xlsx', 'V.xlsx'))
# 以下も同様
#    df = pd.read_excel(outFileNameA)
#    df.set_index('Id', inplace=True)
#    df2 = df.fillna(method='bfill', axis=1)  # ☆彡 df NaN を前後の値で埋める。順方向は ffill
#    df2.to_excel(outFileName.replace('All.xlsx', 'V.xlsx'))
