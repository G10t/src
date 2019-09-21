#! C:\Users\goto1\AppData\Local\Programs\Python\Python37\python.exe
#! python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import webbrowser, requests, bs4, chromedriver_binary
import sys, pyperclip, time, codecs, csv
import pandas as pd
import datetime, re, pprint, random

def getHtmlText(url, fpath, optionForce, useSelenium):
    try:
        if optionForce: # optionForce ＝ 強制的に web から取得させる
            raise Exception       # ☆彡 exception を故意に発生させる
        with open(fpath, 'r', encoding='utf-8') as f:
            htmlText = f.read()
        print(fpath)
    except:
        if useSelenium:
            # selenium を使う場合
            driver = webdriver.Chrome()
            driver.get(url)
            htmlText = driver.page_source
        else:
            # request を使う場合
            res = requests.get(url)
            res.raise_for_status()
            htmlText = res.text
        with open(fpath, 'w', encoding='utf-8', newline='') as f:  # ☆彡 ファイル書き込み 空行抑制
            f.write(htmlText)
        print(url)
    return htmlText

# https://yolo.love/pandas/tolist/ を見ると、現時点でなお、以下があると便利に見える。
def df_to_csvTable(df):
    df = df.reset_index()            # ☆彡 最左列に数字のインデックスを挿入
    csvHeader = list(df.columns)     # ☆彡 df ヘッダー行を配列にコピー  # 先頭の空欄は配列に入らない
    csvRows = df.values.tolist()     # ☆彡 df 中身だけを配列にコピー    # 最左列（0,1,,,）は配列に入らない
    csvRows[0:0] = [csvHeader]       # ☆彡 配列 配列の挿入              # 出来上がり
    return csvRows

def csvTable_to_df(csvRows, indexName):
    n = len(csvRows[1])
    df = pd.DataFrame(csvRows[1:], columns=csvRows[0][:n])
    if indexName:
        df.set_index(indexName, inplace=True)            # ☆彡 df index列 名まえで指定
    else:
        df.set_index(list(df.columns)[0], inplace=True)  # ☆彡 df index列 番号で指定
    return df

def csvTable_to_excel(csvRows, outFileName, indexName):
    df = csvTable_to_df(csvRows, indexName)
    df.to_excel(outFileName)
    print(outFileName)
    return

def excel_to_csvTable(inFileName):
    df = pd.read_excel(inFileName)   # 最左列に番号の列が付いている。最上行は 空欄+ヘッダー の並び
    csvHeader = list(df.columns)     # ☆彡 df ヘッダー行を配列にコピー  # 先頭の空欄は配列に入らない
    csvRows = df.values.tolist()     # ☆彡 df 中身だけを配列にコピー    # 最左列（0,1,,,）は配列に入らない
    csvRows[0:0] = [csvHeader]       # ☆彡 配列 配列の挿入              # 出来上がり
    return csvRows

def showDfs(dfs):
    for i in range(len(dfs)): # range(3,5): #
        print('【table ' + str(i) + '】=======================================================================')
        pprint.pprint(dfs[i])
        if i==1000:
            outFileName = 'data\\__out_' + str(i).zfill(2) + '.csv'
            dfs[i].to_csv(outFileName, encoding = 'utf-8') #'cp932')
    return

def mk5chText(htmlText, fpath):
    soup = bs4.BeautifulSoup(htmlText, 'lxml')
    divs = soup.find_all('div', {'class':'thread'})
    posts = divs[0].find_all('div', {'class':'post'})   # ☆彡 bs4 find_all 指定
    
    f = codecs.open(fpath, 'w',  'cp932', 'ignore')     # ☆彡 ファイル open
    #for post in posts:
    #    cells = post.find_all('span')
    for i in range(len(posts)): #944, 946): #
        cells = posts[i].find_all('span')
        number = cells[0].get_text()
        name = cells[1].get_text()
        date = cells[2].get_text()
        uid = cells[3].get_text()
        escaped = cells[4].get_text("\n", strip=True)
        #print(number, name, date, uid)
        #print(escaped)
        #print(posts[i])
        f.write(number + ' ' + name + ' ' + date + ' ' + uid +'\n')
        f.write(escaped + '\n\n')
    f.close()

#data = data.split("\n")            # ☆彡 改行コードで1行ずつに分割
#text = "\n".join(data)             # ☆彡 改行コードでつなぐ

def mkReadersBoard(htmlText, fpath):  
    soup = bs4.BeautifulSoup(htmlText, 'lxml')
    table = soup.findAll("table", {"id":"tbl1"})[0]    # ☆彡 以下、html の table を配列化する方法
    rows = table.findAll("tr")
    csvRows = []
    for row in rows:
        csvRow = []
        for cell in row.findAll(['td', 'th']):
            csvRow.append(cell.get_text().strip())
        csvRows.append(csvRow[1:])
    csvTable_to_excel(csvRows, fpath, 'PLAYER') # 'RANK'
    return csvRows

def mgReadersBoard(inFiles, outFilePath):
    pprint.pprint(inFiles)
    dfs = []
    for f in inFiles:
        df = pd.read_excel(f)
        #print(df.columns[0], f)
        df.dropna(axis = 0, how = 'all', inplace=True)  # ☆彡 df NaN 行削除
        df.set_index(df.columns[0], inplace=True)       # ☆彡 df index列 番号で指定
        df['GROUP1'] = re.match(r'.+_[0-9]([a-z])', f).group(1)   # ☆彡 正規表現 抽出
        dfs.append(df)
    df = pd.concat(dfs)             # ☆彡 df 縦連結  # 1次は縦連結が良い。横ではない。
    # df = pd.concat(dfs, axis=1)   # ☆彡 df 横連結
    df.to_excel(outFilePath)
    print(outFilePath)
    return

def getTourListDf(htmlText, yyyy):
    csvRows = getTourList(htmlText, yyyy)
    return csvTable_to_df(csvRows, '')

def getTourList(htmlText, yyyy):  # web 上の表のとおりのリストを作成 
                                  # df で採ると1セルの中にいろいろ混在しているので使わない
    soup = bs4.BeautifulSoup(htmlText, 'lxml')
    table = soup.findAll("table", {"class":"schedule"})[0]
    rows = table.findAll("tr")
    csvRows = [['ID', 'Name', 'days', 'Place', 'Plice', 'Winner', 'URL']]
    for row in rows:
        csvRow = []
        #for cell in row.findAll(['td', 'th']):  # td もしくは th を全部 （それぞれ中身とヘッダ）
        #    csvRow.append(cell.get_text().strip())
        try:
            col01 = row.findAll('td', {'class':'col01'})[0] 
        except:
            continue
        days = col01.get_text().strip()
        col02 = row.findAll('td', {'class':'col02'})[0]
        
        p = col02.findAll('p', {'class':'tournamentName'})[0]
        try:
            a = p.findAll('a')[0]
            tournamentName = a.get_text().strip()  # p からでも採れる
            tournamentInfoUrl = a.get('href')      # a からでないと採れない
            tournamentId = tournamentInfoUrl[-4:]
        except:
            tournamentName = p.get_text().strip()  # p からでも採れる
            tournamentInfoUrl = ''      # a からでないと採れない
            tournamentId = 'dmy' + str(random.randint(10000, 100000)) #''
        csvRow.append('\'' + tournamentId)
        s = re.sub(r'\d+th ', '', tournamentName)
        s = re.sub(r'第\d+回', '', s).replace(yyyy, '').strip()
        csvRow.append(s)
        csvRow.append(days)
        csvRow.append(col02.findAll('p', {'class':'tournamentPlace square'})[0].get_text().strip())
        #p = col02.findAll('p', {'class':'tournamentPlace square'})[0]
        #tournamentPlace = p.get_text().strip()
        csvRow.append(col02.findAll('p', {'class':'nopc square'})[0].get_text().strip())
        #p = col02.findAll('p', {'class':'nopc square'})[0]
        #tournamentMonay = p.get_text().strip()
        csvRow.append(col02.findAll('p', {'class':'tournamentWinner square'})[0].get_text().strip())
        #p = col02.findAll('p', {'class':'tournamentWinner square'})[0]
        #tournamentWinner = p.get_text().strip()
        csvRow.append(tournamentInfoUrl)
        csvRows.append(csvRow)
    return csvRows

def getTourListDfMulti(htmlText, yyyy, nameRef): #def changeTourListDf2Multi(df, yyyy):
    csvRows = getTourList(htmlText, yyyy)    #    csvRows = df_to_csvTable(df)

    # csvRows = [['ID', 'Name', 'days', 'Place', 'Monney', 'Winner', 'URL']]
    # csvHeader = ['Id', 'Item', yyyy]
    csvRowsM = [['Id', 'Item', yyyy]]
    for row in csvRows[1:]:
        tourId = row[0]
        tourName = row[1]
        csvRowsM.append([tourId, '1.日程', row[2]])   # dayes
        csvRowsM.append([tourId, '2.場所', row[3]])  # Place 
        csvRowsM.append([tourId, '3.賞金', row[4]]) # Monney
        csvRowsM.append([tourId, '4.優勝', row[5]]) # Winner
        csvRowsM.append([tourId, 'URL', row[6]])    # URL
        try:
            nameRef[tourId]
        except:
            nameRef[tourId] = tourName
    df = pd.DataFrame(csvRowsM[1:], columns=csvRowsM[0])
    dfM = df.set_index(['Id', 'Item'])
    return dfM

def changeTourListDf2Multi(df, yyyy): # この関数はもう不要。
    csvRows = df_to_csvTable(df)

    # csvRows = [['ID', 'Name', 'days', 'Place', 'Monney', 'Winner', 'URL']]
    # csvHeader = ['Id', 'Item', yyyy]
    csvRowsM = [['Id', 'Item', yyyy]]
    for row in csvRows[1:]:
        tourId = row[0]
        randint(a, b)
        #tourName = row[1]
        csvRowsM.append([tourId, 'days', row[2]])
        csvRowsM.append([tourId, 'Place', row[3]])
        csvRowsM.append([tourId, 'Monney', row[4]])
        csvRowsM.append([tourId, 'Winner', row[5]])
        csvRowsM.append([tourId, 'URL', row[6]])
    with open('data\\a.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csvRowsM)

    dfM = pd.read_csv('data\\a.csv', index_col=['Id', 'Item'])
    dfM.to_excel('data\\a.xlsx')
    return dfM
