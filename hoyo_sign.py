#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
米游社游戏签到 - GitHub Actions (国服)
仅绝区零 (ZZZ)
"""
import requests
import time
import random
import hashlib
import os

SALT = "DlOUwIupfU6YespEUWDJmXtutuXV6owG"
USER_AGENT = 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) miHoYoBBS/2.99.1'
DEVICE_ID = '7ab3bc70b846186b9da1e816e6c6f08d'
APP_VERSION = '2.99.1'
CLIENT_TYPE = '5'


def get_ds():
    t = str(int(time.time()))
    r = str(random.randint(100000, 999999))
    c = f"salt={SALT}&t={t}&r={r}"
    md5 = hashlib.md5(c.encode()).hexdigest()
    return f"{t},{r},{md5}"


def get_headers(cookie):
    return {
        'Accept': 'application/json, text/plain, */*',
        'Cookie': cookie,
        'DS': get_ds(),
        'User-Agent': USER_AGENT,
        'x-rpc-app_version': APP_VERSION,
        'x-rpc-client_type': CLIENT_TYPE,
        'x-rpc-device_id': DEVICE_ID,
        'x-rpc-signgame': 'zzz',
        'Content-Type': 'application/json',
    }


ZZZ_ACT_ID = 'e202406242138391'
ZZZ_BASE = 'https://act-nap-api.mihoyo.com/event/luna/zzz'


def sign_zzz(token, uid):
    headers = get_headers(token)

    # 1. 查状态
    time.sleep(random.uniform(1, 3))
    r_info = requests.get(
        f"{ZZZ_BASE}/info",
        headers=headers,
        params={'act_id': ZZZ_ACT_ID, 'lang': 'zh-cn', 'uid': uid, 'region': 'prod_gf_cn'},
        timeout=15
    )
    info = r_info.json()
    if info.get('retcode') != 0:
        return f"❌ 绝区零: {info.get('message', 'unknown')}"

    if info.get('data', {}).get('is_sign'):
        return "✅ 绝区零: 今天已签到"

    # 2. 签到
    time.sleep(random.uniform(2, 5))
    r_sign = requests.post(
        f"{ZZZ_BASE}/sign",
        headers=headers,
        params={'lang': 'zh-cn'},
        json={'act_id': ZZZ_ACT_ID, 'uid': uid, 'region': 'prod_gf_cn'},
        timeout=15
    )
    sign = r_sign.json()
    if sign.get('retcode') == 0:
        return "✅ 绝区零: 签到成功"
    elif sign.get('retcode') == -5003:
        return "✅ 绝区零: 今天已签到"
    else:
        return f"❌ 绝区零: {sign.get('message', 'sign failed')}"


def main():
    token = os.getenv('HOYOLAB_TOKEN', '')
    uid = os.getenv('ZZZ_UID', '')
    if not token or not uid:
        print("Error: HOYOLAB_TOKEN or ZZZ_UID not set")
        return

    print("米游社签到 - 绝区零 (国服)")
    print("=" * 30)
    result = sign_zzz(token, uid)
    print(result)
    print("=" * 30)
    print("Done.")


if __name__ == '__main__':
    main()
