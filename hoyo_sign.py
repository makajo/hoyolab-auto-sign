#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hoyolab Auto Sign - GitHub Actions version
国服 (CN Server) - 使用 api-takumi.miyoushe.com
Supports: Genshin, Star Rail, Honkai 3, Tears of Themis, Zenless Zone Zero
"""
import requests
import time
import random
import hashlib
import os


USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
DEVICE_ID = '7ab3bc70b846186b9da1e816e6c6f08d'
APP_VERSION = '2.41.1'
SALT = '1OUn34iIy84ypu9cpXyun2VaQ2zuFeLm'


def get_ds():
    t = str(int(time.time()))
    r = str(random.randint(0, 999999)).zfill(6)
    c = f"salt={SALT}&t={t}&r={r}"
    md5 = hashlib.md5(c.encode()).hexdigest()
    return f"{t},{r},{md5}"


SIGN_INFO_URL = 'https://api-takumi.miyoushe.com/event/bbs_sign_reward/info'
SIGN_URL = 'https://api-takumi.miyoushe.com/event/bbs_sign_reward/sign'

DELAY_MIN = 1
DELAY_MAX = 3
GAME_DELAY = 2


def random_delay():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def get_headers(cookie):
    ds = get_ds()
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'User-Agent': USER_AGENT,
        'DS': ds,
        'x-rpc-device_id': DEVICE_ID,
        'x-rpc-app_version': APP_VERSION,
        'x-rpc-client_type': '2',
        'Content-Type': 'application/json',
        'Referer': 'https://webstatic.miyoushe.com/',
    }


# 国服游戏配置: (act_id, region, uid_key)
GAME_CONFIG = {
    'Genshin': ('e20230330144011', 'prod_gf_cn', 'genshin_uid'),
    'Star_Rail': ('e202102251931481', 'prod_gf_cn', 'star_rail_uid'),
    'Honkai_3': ('e20230330144011', 'prod_bbs_cn', 'honkai_3_uid'),
    'Tears_of_Themis': ('e20230330144011', 'prod_gf_cn', 'tears_of_themis_uid'),
    'Zenless_Zone_Zero': ('e202310201548501', 'prod_gf_cn', 'zzz_uid'),
}


def sign_game(profile, game_name):
    """签到单个游戏"""
    config = profile['games']

    # 映射游戏名到配置 key
    game_map = {
        'Genshin': 'genshin',
        'Star_Rail': 'honkai_star_rail',
        'Honkai_3': 'honkai_3',
        'Tears_of_Themis': 'tears_of_themis',
        'Zenless_Zone_Zero': 'zenless_zone_zero',
    }
    config_key = game_map.get(game_name, '')
    if config_key not in config or not config[config_key]:
        return None

    uid_key = GAME_CONFIG[game_name][2]
    uid = profile.get(uid_key, '0')

    act_id, region, _ = GAME_CONFIG[game_name]

    headers = get_headers(profile['token'])
    random_delay()

    # 先调 info 获取 act_id 验证
    try:
        info_url = f"{SIGN_INFO_URL}?region={region}&act_id={act_id}"
        info_resp = requests.post(
            info_url, headers=headers,
            json={"uid": uid, "region": region, "act_id": act_id},
            timeout=15
        )
        info_data = info_resp.json()

        if info_data.get('retcode') != 0:
            return f"❌ {game_name}: {info_data.get('message', 'unknown error')}"

        sign_data = info_data.get('data', {})
        is_sign = sign_data.get('is_sign', False)

        # 如果没签到，再调 sign 接口
        if not is_sign:
            sign_resp = requests.post(
                SIGN_URL, headers=headers,
                json={"uid": uid, "region": region, "act_id": act_id},
                timeout=15
            )
            sign_data = sign_resp.json()
            if sign_data.get('retcode') == 0:
                is_sign = sign_data.get('data', {}).get('is_sign', True)

        if is_sign:
            return f"✅ {game_name}: Signed in"
        else:
            return f"❌ {game_name}: Sign failed"

    except Exception as e:
        return f"❌ {game_name}: {str(e)}"

    time.sleep(GAME_DELAY)


def main():
    token = os.getenv('HOYOLAB_TOKEN', '')
    if not token:
        print("Error: HOYOLAB_TOKEN not set")
        return

    profile = {
        'token': token,
        'games': {
            'genshin': os.getenv('GENSHIN', 'false').lower() == 'true',
            'honkai_star_rail': os.getenv('STAR_RAIL', 'false').lower() == 'true',
            'honkai_3': os.getenv('HONKAI_3', 'false').lower() == 'true',
            'tears_of_themis': os.getenv('THERMIS', 'false').lower() == 'true',
            'zenless_zone_zero': os.getenv('ZZZ', 'false').lower() == 'true',
        },
        'accountName': os.getenv('ACCOUNT_NAME', 'My Account'),
        # 国服游戏 UID
        'genshin_uid': os.getenv('GENSHIN_UID', '0'),
        'star_rail_uid': os.getenv('STAR_RAIL_UID', '0'),
        'honkai_3_uid': os.getenv('HONKAI_3_UID', '0'),
        'tears_of_themis_uid': os.getenv('THERMIS_UID', '0'),
        'zzz_uid': os.getenv('ZZZ_UID', '0'),
    }

    print(f"Hoyolab Auto Sign - {profile['accountName']} (CN Server)")
    print("=" * 50)

    results = []
    for game_name in GAME_CONFIG:
        result = sign_game(profile, game_name)
        if result:
            results.append(result)

    for r in results:
        print(r)

    print("=" * 50)
    print("Done.")


if __name__ == '__main__':
    main()
