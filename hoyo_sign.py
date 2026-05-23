#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hoyolab Auto Sign - GitHub Actions version
Supports: Genshin, Star Rail, Honkai 3, Tears of Themis, Zenless Zone Zero
"""
import requests
import time
import random
import os


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

URL_DICT = {
    'Genshin': 'https://sg-public-api.hoyoverse.com/event/sol/sign?lang=en-us&act_id=e202102251931481',
    'Star_Rail': 'https://sg-public-api.hoyoverse.com/event/luna/os/sign?lang=en-us&act_id=e202303301540311',
    'Honkai_3': 'https://sg-public-api.hoyoverse.com/event/mani/sign?lang=en-us&act_id=e202110291205111',
    'Tears_of_Themis': 'https://sg-public-api.hoyoverse.com/event/luna/os/sign?lang=en-us&act_id=e202308141137581',
    'Zenless_Zone_Zero': 'https://sg-public-api.hoyoverse.com/event/luna/zzz/os/sign?lang=en-us&act_id=e202406031448091',
}

HEADER_DICT = {
    'default': {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'x-rpc-app_version': '2.34.1',
        'User-Agent': USER_AGENT,
        'x-rpc-client_type': '4',
        'Referer': 'https://act.hoyolab.com/',
        'Origin': 'https://act.hoyolab.com',
    },
    'Zenless_Zone_Zero': {
        'x-rpc-signgame': 'zzz',
    }
}

DELAY_MIN = 1
DELAY_MAX = 3
GAME_DELAY = 2


def random_delay():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def sign_game(profile, game_name):
    """签到单个游戏"""
    config = profile['games']
    key = game_name.lower().replace(' ', '_').replace('-', '_')
    if key == 'genshin':
        key = 'genshin'
    elif game_name == 'Honkai_3':
        key = 'honkai_3'
    elif game_name == 'Star_Rail':
        key = 'honkai_star_rail'
    elif game_name == 'Tears_of_Themis':
        key = 'tears_of_themis'
    elif game_name == 'Zenless_Zone_Zero':
        key = 'zenless_zone_zero'
    if not config.get(key, False):
        return None

    headers = {
        **HEADER_DICT['default'],
        **HEADER_DICT.get(game_name, {}),
        'Cookie': profile['token']
    }

    url = URL_DICT[game_name]
    random_delay()

    try:
        resp = requests.post(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return f"❌ {game_name.replace('_', ' ')}: HTTP {resp.status_code}, body={resp.text[:200]}"
        try:
            data = resp.json()
        except:
            return f"❌ {game_name.replace('_', ' ')}: Invalid JSON response (status={resp.status_code}, body={resp.text[:200]})"

        if data is None:
            result = f"❌ {game_name.replace('_', ' ')}: API returned empty response"
            time.sleep(GAME_DELAY)
            return result

        if data.get('retcode') == 0:
            result = f"✅ {game_name.replace('_', ' ')}: {data['data']['is_sign']} - {data['data']['info']}"
        else:
            msg = data.get('message', 'Unknown error')
            gt_result = (data.get('data') or {}).get('gt_result')
            if gt_result and gt_result.get('is_risk'):
                msg = 'CAPTCHA blocked'
            result = f"❌ {game_name.replace('_', ' ')}: {msg}"

        time.sleep(GAME_DELAY)
        return result

    except Exception as e:
        return f"❌ {game_name.replace('_', ' ')}: {str(e)}"


def main():
    # HOYOLAB_TOKEN 现在存储完整 Cookie
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
        'accountName': os.getenv('ACCOUNT_NAME', 'My Account')
    }

    print(f"Hoyolab Auto Sign - {profile['accountName']}")
    print("=" * 50)

    results = []
    for game_name in URL_DICT:
        game_key = game_name.lower().replace(' ', '_').replace('-', '_')
        if game_key == 'genshin':
            game_key = 'genshin'
        elif game_name == 'Honkai_3':
            game_key = 'honkai_3'
        elif game_name == 'Star_Rail':
            game_key = 'honkai_star_rail'
        elif game_name == 'Tears_of_Themis':
            game_key = 'tears_of_themis'
        elif game_name == 'Zenless_Zone_Zero':
            game_key = 'zenless_zone_zero'

        result = sign_game(profile, game_name)
        if result:
            results.append(result)

    for r in results:
        print(r)

    print("=" * 50)
    print("Done.")


if __name__ == '__main__':
    main()
