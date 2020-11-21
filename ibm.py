import pandas as pd
import requests
import sys
from datetime import datetime
from pandas.io.json import json_normalize
import urllib3
from urllib3 import request
print("Hello world")

api_key = 'SY3W1RLBL12C0G45'
symbol1 = 'IBM'
url1 = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=SY3W1RLBL12C0G45'
print(url1)

def request_data(url):
  r = requests.get(url)
  if r.status_code != 200:
    print('Error, status code != 200')
    print(r.status_code)
  else:
    print('Server status shows new update')
    pass
  return r

import certifi
http = urllib3.PoolManager(
       cert_reqs='CERT_REQUIRED',
       ca_certs=certifi.where())

myReq2 = request_data(url1)
myReq1 = http.request('GET', url1)


def construct_df(r):
  high = r.json()['data']['high']
  df = json_normalize(high)
  return df

import json

myData = json.loads(myReq1.data.decode('utf-8'))

myData

myMeta =  pd.json_normalize(data = myData, max_level=1  )
mySymbol = myMeta['Meta Data.2. Symbol']
mySymbol2 = mySymbol[0]
mySymbol2

df = pd.json_normalize(data = myData, max_level=2  )

df

myDf1= df
highs =  df.filter(regex='high$',axis=1).head()
lows =  df.filter(regex='low$',axis=1).head()
opens =  df.filter(regex='open$',axis=1).head()
closes =  df.filter(regex='close$',axis=1).head()
df1 = highs.stack().reset_index(-1).iloc[:, ::-1]
df1.columns = ['high', 'ref_dt_5min']

df2 = lows.stack().reset_index(-1).iloc[:, ::-1]
df2.columns = ['low', 'ref_dt_5min']

df3 = opens.stack().reset_index(-1).iloc[:, ::-1]
df3.columns = ['open', 'ref_dt_5min']

df4 = closes.stack().reset_index(-1).iloc[:, ::-1]
df4.columns = ['close', 'ref_dt_5min']


df4

df1['clean_dt'] = df4.ref_dt_5min.str.extract('\.([^\.]*)')
df2['clean_dt'] = df4.ref_dt_5min.str.extract('\.([^\.]*)')
df3['clean_dt'] = df4.ref_dt_5min.str.extract('\.([^\.]*)')
df4['clean_dt'] = df4.ref_dt_5min.str.extract('\.([^\.]*)')

from functools import reduce
dfs = [df1, df2, df3, df4]

df_wide = reduce(lambda left,right: pd.merge(left,right,on='clean_dt',how='inner'), dfs)
df_formatted = df_wide[[ "clean_dt", "low","high","open","close"]]
df_formatted

from datetime import datetime

# datetime object containing current date and time
df_formatted['Symbol'] = mySymbol2
df_formatted['ETL_JOB_ID'] = datetime.now()
df_formatted

from sqlalchemy import create_engine
engine = create_engine('postgres://fqnznyqrxcnvvv:6587892a6ac0d03c694bcaef2aa2c856c83ae79408726b074fa526d411c66319@ec2-54-247-118-139.eu-west-1.compute.amazonaws.com:5432/dcp3g2j8tjq3t9')
df_formatted.to_sql('stocks_5min', engine)