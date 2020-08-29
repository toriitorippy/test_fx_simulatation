from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.positions as positions
import json
import sys
import urllib.parse
import urllib.request
import datetime
import os

msg1 = ''
msg2 = ''
##line_info
# LINE notify's API
LINE_TOKEN= "xxxx"
LINE_NOTIFY_URL="xxx"

def send_info(msg):
    method = "POST"
    headers = {"Authorization": "Bearer %s" % LINE_TOKEN}
    payload = {"message": msg}
    try:
        payload = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
            url=LINE_NOTIFY_URL, data=payload, method=method, headers=headers)
        urllib.request.urlopen(req)
    except Exception as e:
        print ("Exception Error: ", e)
        sys.exit(1)

##fx_info
accountID = "xxx"
access_token = 'xxx'

api = API(access_token=access_token, environment="practice")

params = { "instruments": "EUR_USD,EUR_JPY,USD_JPY" }
r = accounts.AccountInstruments(accountID=accountID, params=params)
current_info = api.request(r)

#現在のアカウント情報
r = accounts.AccountSummary(accountID)
account_info=api.request(r)
msg1 = '純資産:' + account_info['account']['NAV']  
msg2 = '利益：' + account_info['account']['pl']

#過去100分取得
params = {
  "count": 10,
  "granularity": "M5"
}
r = instruments.InstrumentsCandles(instrument="USD_JPY", params=params)
past_info = api.request(r)
open_list = []
for i in range(10):
    open_list.append(int(past_info['candles'][i]['mid']['o'].replace('.', '')))
    
    
r = positions.OpenPositions(accountID=accountID)
position = api.request(r)

is_position_null = False #positionがあるかどうか

if position['positions'] == []:
    is_position_null = True
else:
    long = int(position['positions'][0]['long']['units'])
    short = int(position['positions'][0]['short']['units'])
    
diff1 = open_list[9] - open_list[5] #最近のモノ
diff2 = open_list[4] - open_list[0] #少し前のモノ

def do_fx():
    msg3 = 'なにもしませんでした'
    if is_position_null:
        if diff1 > 0 and diff2 > 0:
            if diff1 > diff2: #もし上がる傾向が強くなっていたら
                #買う
                print('None→buy')
                data = {
                "order": {
                    "instrument": "USD_JPY",
                    "units": "+10",
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
                }

                r = orders.OrderCreate(accountID, data=data)
                api.request(r)
                msg3 = '買いました' 

        if diff1 < 0 and diff2 < 0:
            if diff1 < diff2: #もし下がる傾向が強くなっていたら
                #売る
                print('None→sell')
                data = {
                "order": {
                    "instrument": "USD_JPY",
                    "units": "-10",
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
                }

                r = orders.OrderCreate(accountID, data=data)
                api.request(r)
                msg3 = '売りました'
    else:
        if not long ==0:
            if diff1 < diff2: #上がる傾向が弱くなっていたら
                print('buy→None')
                data = {
                "longUnits": str(long)
                }
                r = positions.PositionClose(accountID=accountID,
                                            instrument='USD_JPY',
                                            data=data)
                output = api.request(r)
                pl = ['longOrderFillTransaction'][0]['pl']
                msg3 = '買いポジションを終了しました。利益は・・・'  + pl
        if not short == 0:
            if diff1 > diff2: #下がる傾向が弱くなっていたら
                print('sell →None')
                abs_short = short * -1
                data = {
                    "shortUnits": str(abs_short)
                }
                r = positions.PositionClose(accountID=accountID,
                                instrument='USD_JPY',
                                data=data)
                output = api.request(r)
                pl = ['shortOrderFillTransaction'][0]['pl']
                msg3 = '売りポジションを終了しました。利益は・・・' +  pl
    
    msg = str(msg1) + '\n' + str(msg2) +  '\n' + str(msg3)
    print(msg)
    if not msg3 == 'なにもしませんでした':
        send_info(msg)


