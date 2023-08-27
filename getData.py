#『なろう小説API』を用いて、なろうの『全作品情報データを一括取得する』Pythonスクリプト
# 2020-04-26更新
import requests
import pandas as pd
import json
import time as tm
import datetime
import gzip
from tqdm import tqdm
import sqlite3
#正規表現
from datetime import timedelta
import re
import math
#値算定
import statistics


host = 'hostname'#任意のﾎｽﾄ名
user = 'username'#任意のﾕｰｻﾞ名
db = 'dbname'#任意のﾃﾞｰﾀﾍﾞｰｽ名
password = 'password'#任意のﾊﾟｽﾜｰﾄﾞ
charaset = 'utf8'

url = 'mysql+pymysql://'+user+':'+password+'@'+host+'/'+db+'?charset='+charaset
engine = sqa.create_engine(url, echo=True)


#リクエストの秒数間隔(1以上を推奨)
interval = 2
is_narou = True
now_day = datetime.datetime.now()
str_day = now_day.strftime("%Y-%m-%d %H:%M:%S")

if is_narou:
    filename = 'Narou_All_OUTPUT_%s.xlsx'%now_day
    sql_filename = 'Narou_All_OUTPUT_%s.sqlite3'%now_day
    api_url="https://api.syosetu.com/novelapi/api/"    
else:
    filename ='Narou_18_ALL_OUTPUT_%s.xlsx'%now_day
    sql_filename = 'Narou_18_ALL_OUTPUT_%s.sqlite3'%now_day
    api_url="https://api.syosetu.com/novel18api/api/"
# データをSqlite3形式でも保存する
is_save_sqlite = False

#全作品情報の取得
def get_all_novel_info():
       
    df = pd.DataFrame()
    
    payload = {'out': 'json','gzip':5,'of':'n','lim':1}
    res = requests.get(api_url, params=payload).content
    r =  gzip.decompress(res).decode("utf-8")
    allcount = json.loads(r)[0]["allcount"]
    print('対象作品数  ',allcount);
    
    all_queue_cnt = (allcount // 500) + 10
    
    #現在時刻を取得
    nowtime = datetime.datetime.now().timestamp()
    lastup = int(nowtime)
                     
    for i in tqdm(range(all_queue_cnt)):
        payload = {'out': 'json','gzip':5,'opt':'weekly','lim':500,'of':'t-n-g-w-ga-dp-wp-a-gf-gl','lastup':"1073779200-"+str(lastup)}
        
        # なろうAPIにリクエスト
        cnt=0
        while cnt < 5:
            try:
                res = requests.get(api_url, params=payload, timeout=30).content
                break
            except:
                print("Connection Error")
                cnt = cnt + 1
                tm.sleep(120) #接続エラーの場合、120秒後に再リクエストする
            
        r =  gzip.decompress(res).decode("utf-8")
    
        # pandasのデータフレームに追加する処理
        df_temp = pd.read_json(r)
        df_temp['get_date'] = now_day
        df_temp = df_temp.drop(0)
        df = pd.concat([df, df_temp])
        
        last_general_lastup = df.iloc[-1]["general_lastup"]
        lastup = datetime.datetime.strptime(last_general_lastup, "%Y-%m-%d %H:%M:%S").timestamp()
        lastup = int(lastup)
        #取得間隔を空ける
        tm.sleep(interval)

    return df

if __name__ == '__main__':
    get_all_novel_info()


