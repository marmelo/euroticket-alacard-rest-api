#!/usr/bin/env python
"""
Python library to check Euroticket à la card balance and recent history.
"""

import hmac
import hashlib
import json
import urllib.request

BASE_URL = 'https://www.euroticket-alacard.pt'
AUTH_URL = '/alc/rsvc/login'
DATA_URL = '/alc/rsvc/getBalanceAndTransactions'
ENCODING = 'UTF-8'

SYSTEM = {
    'appId': '5000',
    'appVersion': '1.0.1',
    'deviceId': 'XXX',
    'deviceModel': 'YYY',
    'osId': 'android',
    'osVersion': '4.1.1',
    'language': 'pt'
}


def alacard(username, password):
    """Fetch Euroticket à la card balance and recent history."""
    # authentication
    data = dict(SYSTEM, **{
        'username': username,
        'hashPin': _hmacSHA256(username, password)
    })
    
    res = _post(BASE_URL + AUTH_URL, data)
    
    if res['status']['errorCode'] != 0:
        raise Exception(res['status']['errorMsg'])
    
    
    # balance and movements
    data = dict(SYSTEM, **{
        'securityToken': res['securityToken']
    })
    
    res = _post(BASE_URL + DATA_URL, data)
    
    if res['status']['errorCode'] != 0:
        raise Exception(res['status']['errorMsg'])
    
    return res


def _hmacSHA256(username, password):
    """Calculate authentication hash."""
    return hmac.new(b'JFq7JpxvRoE1XjqTE6qNKfvcddA5V43A',
                    msg=(SYSTEM['deviceId'] + username + password).encode(ENCODING),
                    digestmod=hashlib.sha256).hexdigest()


def _post(url, data):
    """Perform a JSON HTTP POST request."""
    req = urllib.request.Request(url, json.dumps(data).encode(ENCODING), { 'Content-Type': 'application/json' })
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode(ENCODING))


if __name__ == "__main__":
    try:
        # change the username and password
        data = alacard('1111111111111111', '222222')
        print(data)
    except Exception as e:
        print("Error: {}".format(e))
