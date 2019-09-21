#! C:\Users\goto1\AppData\Local\Programs\Python\Python37\python.exe
#! python3
import sys, pyperclip, time
import pandas as pd
#--
import datetime, re, pprint, codecs
from _my import getHtmlText
from _my import df_to_csvTable, csvTable_to_df
from _my import excel_to_csvTable, csvTable_to_excel
from _my import mk5chText, mkReadersBoard, mgReadersBoard

#useSelenium = False #True # 
bitSelenium = 0b00000001
bitForce    = 0b00000010   # ☆彡 bit演算 >> << & | ^(XOR) ~(NOT)
options = 0 #bitSelenium   # 0 # 
outFiles =[]

txtFilePath = '00ch_LPGAcharangersUrlList.txt'
with codecs.open(txtFilePath, "r", 'cp932', 'ignore')  as f:
    lines = f.readlines()
    for line in lines:
        try:                            # ☆彡 「先頭が空白文字（正規表現） or 空行」をスキップ
           if re.match(r'\s.*', line):            
                continue
        except:
            continue
        cell = line.split()             # ☆彡 文字列を配列に分割 分割文字のでふぉるトは空白
        url = cell[0]
        if url[0] == '-': break
        if cell[1][0] == '-':
            optionStr = cell[1]
            fpath = cell[2]
            if 'f' in optionStr:
                options |= bitForce  # ☆彡 bit演算 ビットを立てる
        else:
            fpath = cell[1]

        #0 URL list の読み込みロジックのチェック
        #print(url ,fpath)
        #
        # 設計時メモを後ろへ移動
        #1 htmlTxt の読み込みと Excel 化
        if '1' in optionStr:
            #1-1 htmlTxt の読み込み
            htmlText = getHtmlText(url, fpath, options & bitForce, options & bitSelenium)
            #1-2 htmlText から excel ファイル生成  ★1 コメントアウトで、動かすものを選ぶ
            #1-2-1 5ch
            #mk5chText(htmlText, fpath.replace('.html', '.txt'))
            #1-2-2 LPGA リーダーズボード
            mkReadersBoard(htmlText, fpath.replace('.html', '.xlsx'))
        #2 将来に向けた予約
        if '2' in optionStr:
            pass
        #3 出力ファイルのリスト化
        if '3' in optionStr:
            outFiles.append(fpath.replace('.html', '.xlsx'))
    #3 リスト化された出力ファイルの処理
    #pprint.pprint(inFiles)
    if '3' in optionStr:
        # LPGA リーダーズボードのマージ  ★1 コメントアウトで、動かすものを選ぶ
        outFilePath = re.sub(r'_([0-9])[a-x].xlsx', r'_\1.xlsx', outFiles[0])  # ☆彡 正規表現 置換 \1 \2,,,
        mgReadersBoard(outFiles, outFilePath)

        # 設計時メモ
        # ここの動きを txt ファイルのオプションで制御する。
        # テーブルを全表示する関数も作る
        # before roop、in the roop、after roop、という汎用性を持たせられないか？
        #     - before roop はない。オプションを見るこの場所がループの中。
        
