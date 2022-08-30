import cloudscraper
import sys
import json
from time import gmtime, strftime
from datetime import datetime
import time
import traceback
from pprint import pprint
from function import create_tran


scraper = cloudscraper.create_scraper(browser={'custom': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37"})

f = open('./setting.json',)
setting = json.load(f)
f.close()

def timestamp():
    nowTime = int(datetime.timestamp(datetime.now()))
    timeUnit = datetime.fromtimestamp(nowTime).strftime('%Y-%m-%d %H:%M:%S')
    fomat_dt = f'[{timeUnit}]'
    return fomat_dt

if not setting['session']:
    print(f'{timestamp()} Please check dropid in file setting.json need session')
    sys.exit()
if not setting['dropid']: 
    print(f'{timestamp()} Please check dropid in file setting.json need dropid')
    sys.exit()
if not setting['count']: 
    print(f'{timestamp()} Please check count in file setting.json need more than 0')
    sys.exit()

cookies = {'session_token': setting['session']}

def login():
    return scraper.get("https://api-idm.wax.io/v1/accounts/auto-accept/login", cookies=cookies, headers={"origin":"https://wallet.wax.io"}).text


def GetUserInfo(user):
    data = {
        "account_name": user
    }
    return scraper.post("https://chain.wax.io/v1/chain/get_account", json.dumps(data), cookies=cookies, headers={"origin":"https://wallet.wax.io"}).text

def CheckDrops(code):
    scraper = cloudscraper.create_scraper()
    data = {
    "json": True,
    "code": "neftyblocksd",
    "scope": "neftyblocksd",
    "table": "drops",
    "lower_bound": code,
    "upper_bound": "",
    "index_position": 1,
    "key_type": "",
    "limit": 1,
    "reverse": False,
    "show_payer": False
    }
    return scraper.post("https://wax.neftyblocks.com/v1/chain/get_table_rows", json.dumps(data)).text



def main():
    try:
        logincheck = json.loads(login())
    except Exception as e:
        logincheck = json.loads(login())


    try:
        if logincheck['userAccount']:
            waxuser = logincheck['userAccount']
            waxsession = setting['session']
            sender = {
            'id': waxuser,
            'session': waxsession
            }
            userinfo = json.loads(GetUserInfo(waxuser))
            
            print(f"{timestamp()} {logincheck['userAccount']} Account Balance: {userinfo['core_liquid_balance']}")
            print(f"{timestamp()} {logincheck['userAccount']} Cpu Info (use/max): {str(userinfo['cpu_limit']['used'])} / {str(userinfo['cpu_limit']['max'])} | Available: {str(userinfo['cpu_limit']['available'])}")
            if userinfo['cpu_limit']['used'] >= userinfo['cpu_limit']['max']:
                print(f"{timestamp()} {logincheck['userAccount']} CPU overload please staked CPU")
                exit()
            checkdropes = json.loads(CheckDrops(setting['dropid']))
            try:
                dropseiei = {
                    'quantity': checkdropes["rows"][0]["listing_price"],
                    'symbol': checkdropes["rows"][0]["settlement_symbol"],
                    'drop_id': checkdropes["rows"][0]["drop_id"],
                    'template_id': checkdropes["rows"][0]["assets_to_mint"][0]["template_id"],
                    'count': int(setting['count'])
                }
                timestartcon = datetime.fromtimestamp(checkdropes['rows'][0]['start_time']).strftime('%Y/%m/%d %H:%M:%S')
                datenow = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                fmt = '%Y/%m/%d %H:%M:%S'
                ts1 = datetime.strptime(timestartcon, fmt)
                ts2 = datetime.strptime(datenow, fmt)
                if ts1 > ts2:
                    ts = ts1 - ts2
                else:
                    ts = ts1 - ts2
                td_mins = int(round(ts.total_seconds()) - 3.5)
                if td_mins > 0:
                    td_mins = td_mins
                else:
                    td_mins = 0
                seconds_in_day = 60 * 60 * 24
                seconds_in_hour = 60 * 60
                seconds_in_minute = 60
                days = td_mins // seconds_in_day
                hours = (td_mins - (days * seconds_in_day)) // seconds_in_hour
                minutes = (td_mins - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
                print(f"{timestamp()} {logincheck['userAccount']} Wait Time: {str(days)} Day {str(hours)} Hours {str(minutes)} Minutes")
                time.sleep(td_mins)
                start = create_tran(scraper, sender, dropseiei)
                print(strftime("[%H:%M:%S]", gmtime())+" [#PORSERVER]["+logincheck['userAccount']+"] => ADD TX SUCCESS : "+start)
                print(f"{timestamp()} {logincheck['userAccount']} ADD TX SUCCESS : {start}")
                time.sleep(9999)
            except Exception as e:
                print(f"{timestamp()} {logincheck['userAccount']} No DropId or error (Exit in 10 seconds")
                time.sleep(10)
                exit()
        else:
            print(f"{timestamp()} Check cookie error")
            traceback.print_exc()
            time.sleep(99999)
    except Exception as e:
        print(f"{timestamp()} Error!!")
        traceback.print_exc()
        time.sleep(99999)



if __name__ == '__main__':
    main()