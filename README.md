# Euroticket à la card REST API

This document details the [Euroticket à la card](https://www.euroticket-alacard.pt/) REST API used in the [Android](https://play.google.com/store/apps/details?id=pt.bes.pp.edenred&hl=pt_PT) and [iOS](https://itunes.apple.com/pt/app/euroticket-a-la-card/id820890384?mt=8) mobile apps.
The protocol details were inferred from the official Android app APK decompilation and network analysis.

Eager to see this running? Jump to my [example Python implementation](alacard.py).

Before official mobile apps being released the only known way to retrieve this information was to simulate the browser's behaviour using standard HTTP requests along with screen scraping. If you are interested in that version please check my older project [python-alacard](https://github.com/marmelo/python-alacard).

- [Introduction](#introduction)
- [Authentication](#authentication)
- [Balance and Movements](#balance-and-movements)
- [Error Messages](#error-messages)
- [Password Hashing](#password-hashing)


## Introduction

The following table lists the mandatory fields every API call must set.
Although their values are not strict to the next example I believe them to work just fine.

|Name|Example Value|Description|
|:---|:---|:---|
|appId|5000|App ID (from manifest)|
|appVersion|1.0.1|App Version (from manifest)|
|deviceId|XXX|Device IMEI|
|deviceModel|YYY|Device Model (usually brand and type)|
|osId|android|Operating System ID|
|osVersion|4.1.1|Operating System Version|
|language|pt|Language|

The calls described in the next sections will use the following credentials by default.

|Name|Value|Description|
|:---|:---|:---|
|username|1111111111111111|The card number|
|password|222222|The card password|

The API calls are standard HTTP POSTs where both request and response consist on JSON documents.


## Authentication

The autentication request contains not only the mandatory fields but also a `username` and `hashPin`. The `hashPin` is not the password itself but an `HmacSHA256` hash computed from the magic key `JFq7JpxvRoE1XjqTE6qNKfvcddA5V43A` and the concatenation of `deviceId`, `username` and `password`.

```
HmacSHA256('JFq7JpxvRoE1XjqTE6qNKfvcddA5V43A', 'XXX1111111111111111222222')
>>> 2caabd51b72c839b129636a2bcb8f4274fd7905eb5fa7af494ea4356e0602457
```

In the [Password Hashing](#password-hashing) section you may find how to use `bash`, `Python` or `JavaScript` to compute the `HmacSHA256` hash.


### Request

```JavaScript
POST https://www.euroticket-alacard.pt/alc/rsvc/login
Content-Type: application/json

{
  "appId": "5000",
  "appVersion": "1.0.1",
  "deviceId": "x",
  "deviceModel": "x",
  "osId": "android",
  "osVersion": "4.1.1",
  "language": "pt",
  "username": "1111111111111111", 
  "hashPin": "2caabd51b72c839b129636a2bcb8f4274fd7905eb5fa7af494ea4356e0602457"
}
```

### Response

```JavaScript
{
  "securityToken": "96FE753288A1A197CB17E2B7A7471A6A0503D6B60B3F784DFE9519C8540F4CE3A8FB916326168373E2C897E1371F95A5DDB69434F112D0D4EB582E3F8F2AB81B",
  "mustUpgrade": false,
  "status": {
    "severity": 0,
    "errorCode": 0
  }
}
```

The returned `securityToken` will be used to authenticate further requests.

The response always contains a `status` entry where you may assert if there was something wrong with the request. The most common errors may be found in the [Error Messages](#error-messages) section.


## Balance and Movements

### Request

```JavaScript
POST https://www.euroticket-alacard.pt/alc/rsvc/getBalanceAndTransactions
Content-Type: application/json

{
  "appId": "5000",
  "appVersion": "1.0.1",
  "deviceId": "x",
  "deviceModel": "x",
  "osId": "android",
  "osVersion": "4.1.1",
  "language": "pt",
  "securityToken": "96FE753288A1A197CB17E2B7A7471A6A0503D6B60B3F784DFE9519C8540F4CE3A8FB916326168373E2C897E1371F95A5DDB69434F112D0D4EB582E3F8F2AB81B"
}
```

### Response

```JavaScript
{
  "cardName": "JOHN DOE",
  "cardNumber": "xxxxxxxxxxxx1111",
  "balanceDisp": 130.02,
  "balanceCont": 136.17,
  "movements": [
    {
      'date': '2014-09-17T20:42:00.187+0000',
      'type': 'Movimento',
      'description': "Compra: MCDONALD'S PADRE    LISBOA",
      'value': -6.15,
      'balance': 130.02
    },
    {
      "date": "2014-09-16T18:17:11.844+0000",
      "type": "Movimento",
      "description": "Compra: PREGO GOURMET LDA   2790-045 CARNAXIDE",
      "value": -8.95,
      "balance": 136.17
    },
    {
      'date': '2014-09-15T11:20:16.634+0000',
      'type': 'Movimento',
      'description': 'Compra: MERCEARIA DA PRACA  LISBOA',
      'value': -12.16,
      'balance': 145.12
    }
  ],
  "resourcesLastModified": "2013-12-19T18:13:01.000+0000",
  "securityToken": "96FE753288A1A197CB17E2B7A7471A6A0503D6B60B3F784DFE9519C8540F4CE3A8FB916326168373E2C897E1371F95A5DDB69434F112D0D4EB582E3F8F2AB81B",
  "mustUpgrade": false,
  "status": {
    "severity": 0,
    "errorCode": 0
  }
}
```

## Error Messages

When everithing is fine (no errors):
```JavaScript
{
  "status": {
    "severity": 0,
    "errorCode": 0
  }
}
```

When you send an invalid field value or miss a mandatory one:
```JavaScript
{
  "status": {
    "severity": 3,
    "errorCode": 1,
    "errorMsg": "Invalid input data."
  }
}
```

When the `username` or `password` is not correct:
```JavaScript
{
  "status": {
    "severity": 6,
    "errorCode": 3,
    "errorMsg": "Falha de autenticação."
  }
}
```

When the `securityToken` is invalid or expired:
```JavaScript
{
  "status": {
    "severity": 6,
    "errorCode": 5,
    "errorMsg": "Token de segurança inválido."
  }
}
```


## Password Hashing

```bash
$ # bash
$ echo -n "XXX1111111111111111222222" | openssl sha256 -hmac "JFq7JpxvRoE1XjqTE6qNKfvcddA5V43A"
```

```Python
# python
import hashlib
import hmac
hmac.new(b'JFq7JpxvRoE1XjqTE6qNKfvcddA5V43A', msg=b'XXX1111111111111111222222', digestmod=hashlib.sha256).hexdigest()
```

```JavaScript
// JavaScript
// https://code.google.com/p/crypto-js/
CryptoJS.HmacSHA256("XXX1111111111111111222222", "JFq7JpxvRoE1XjqTE6qNKfvcddA5V43A").toString()
```
