# -*- coding: utf-8 -*-
import httplib
import urllib
import json
import hashlib
import hmac
#import requests
from collections import OrderedDict

api_key = ""
secret_key = ""

def getCoinMarketCapData(currencies):
    returns = {}

    for item in currencies:
        url = "https://api.coinmarketcap.com/v1/ticker/" + item['name'].split(" ")[0].lower()
        response = urllib.urlopen(url)
        cmcData = json.loads(response.read())
        c = {"name":item['name'].split(" ")[0], "currency":item['currency'], "price_usd":cmcData[0]['price_usd'], "price_btc":cmcData[0]['price_btc'], "d1h":cmcData[0]['percent_change_1h'], "d24h":cmcData[0]['percent_change_24h'], "d7d":cmcData[0]['percent_change_7d'], "value":0.0}
        returns[item['currency']] = c

    return returns
    

def getData(dataDict, method, server, key, secret):
    encoded_data = urllib.urlencode(dataDict)

    sign = hmac.new(secret, msg=encoded_data, digestmod=hashlib.sha256).hexdigest().upper()

    headers = {"Api-key":key, "Sign":sign}

    conn = httplib.HTTPSConnection(server)
    conn.request("GET", method + '?' + encoded_data, '', headers)

    response = conn.getresponse()
    data = json.load(response)
    conn.close()

    return data

def outputLine(key, value, prefix, suffix):
    spaces = ""
    pslen = len(prefix) + len(suffix)
    key = key.upper()
    key = " " + key + ": "
    keylen = len(key)
    x = 70-keylen-pslen
    for count in range(x-len(str(value))):
        spaces += " "
    return key + prefix + value + suffix + spaces
 
server = "api.livecoin.net"
balancesMethod = "/payment/balances"
coinInfoMethod = "/info/coinInfo"
responses = []
names = []
balances = []

namesJSON = getData([], coinInfoMethod, server, api_key, secret_key)['info']
for name in namesJSON:
    names.append({"name":name['name'], "symbol":name['symbol']})

data = OrderedDict([])
d = getData(data, balancesMethod, server, api_key, secret_key)
responses.append(d)
 
for currency in responses[0]:
    if currency['value'] > 0.0 and currency['type'] == 'total':
        for name in names:
            if name['symbol'] == currency['currency']:
                currency['name'] = name['name']
        balances.append(currency)

ownedCoins = []

for balance in balances:
    ownedCoins.append({"name":balance['name'], "symbol":balance['currency']})

cmcData = getCoinMarketCapData(balances)

for balance in balances:
    try:
        cmcData[balance['currency']]['value'] = balance['value']
    except:
        continue

for coin in ownedCoins:
    item = cmcData[str(coin['symbol'])]
    v = item['value']
    v = "%f" % (v)

    btc = float(item['price_btc'])*float(item['value'])
    usd = float(item['price_usd'])*float(item['value'])
    
    print "+----------------------------------------------------------------------+"
    print "|" + outputLine('currency', item['currency'], "", "") + "|"
    print "|" + outputLine('amount owned', v, "", "") + "|"
    print "|" + outputLine('price/coin in usd', item['price_usd'], "$", "") + "|"
    print "|" + outputLine('your amount in usd', str(usd), "$", "") + "|"
    print "|" + outputLine('price/coin in btc', item['price_btc'], u'\u20BF', "") + "|"
    print "|" + outputLine('your amount in btc', str(btc), u'\u20BF', "") + "|"
    print "|" + outputLine('Percent change 1h', item['d1h'], "", "%") + "|"
    print "|" + outputLine('percent change 24h', item['d24h'], "", "%") + "|"
    print "|" + outputLine('percent change 7d', item['d7d'], "", "%") + "|"
    print "+----------------------------------------------------------------------+"
    print "\n"
        
    

