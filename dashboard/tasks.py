import os
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from tempfile import TemporaryDirectory
from django.core.cache import cache
import pandas as pd
import yagmail
from hyper.contrib import HTTP20Adapter

def task1(name):
    print('Hello')
    time.sleep(3)
    print(name)

def send_email(data):
    print(data)
    with TemporaryDirectory() as tmp_folder:
        cache_data = cache.get(data['sid'])
        orders_df = pd.read_json(cache_data, orient= 'table')
        dt = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        file_path = f'{tmp_folder}/{dt}.csv'
        orders_df.to_csv(file_path, encoding='gbk')

        yag = yagmail.SMTP(user='1140525199@qq.com',host='smtp.qq.com')
        content = ['订单数据见附件', file_path]
        yag.send(data['email'], data['subject'], content)

    return True

def spider_zhihu():
    os.environ['NO_PROXY'] = 'zhihu.com'
    url = 'https://www.zhihu.com/api/v5.1/topics/19553176/feeds/essence?offset=50&limit=10&'
    headers = {
        'Connection': 'close',
        'authority': 'www.zhihu.com',
        'method': 'GET',
        'path': '/api/v5.1/topics/19553176/feeds/essence?offset=50&limit=10&',
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': '_zap=26d4e326-79bc-4b6a-8ba6-b50188ed2d10; d_c0="AODQPKY6-RSPTg_PO3QReFndNmCgFe0en3o=|1653102865"; YD00517437729195%3AWM_NI=6qLvJa1CIuuu3igpcn5oASC5hCjoCkcbJODXijgEMim%2B%2FRYfkf6EH7PEuLyn4z6LPOtRYuI80tPtDO7pZlpMujP2SHxOFiU%2BngvaYK30Y%2FZW0OL4UBc4VIWxVmltGycTcWQ%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6eed2d24a87b5fba7d533bba88fa7c55a979a9a87d15ea2b09db3e47cb187f884d82af0fea7c3b92af6af8497c96bf39d8796f87ff1b7a991e266f7b18fb4c23fac9da690c261a1be86b0c754abb6a9a6d063aff5e1b3dc6ea9bafaa6cb3d949bbbadfc66f8a6faadd345b88e9796cc34f4aca095c745f5b0968df347b7b6a0d3d244bc918a8ad821aeb9ba82dc41f1f097d0d95df49184d5d84aa1ec9aaad67496b3a495c673a18cadb8d437e2a3; YD00517437729195%3AWM_TID=39fiI0PUII1EAAVRAVfQEKpTBKs9MscV; _9755xjdesxxd_=32; captcha_session_v2=2|1:0|10:1653359242|18:captcha_session_v2|88:K1ptelNRZFBPbjBSOVBhbzQ1R0p2UC9DZ2NQMFA5ZGVQTDZQMk5nT255WlJlRjRWQW85ZVVycTBnZXJiZ0VRRg==|b48086b987c1317b22c4e283feb986022b2c91801d10d3806dbe0bf71a1d2ec9; captcha_ticket_v2=2|1:0|10:1653359333|17:captcha_ticket_v2|704:eyJ2YWxpZGF0ZSI6IkNOMzFfNzZQNHZYc1ZwSlVYTFhIaE55VTRJZ1E4cC1EOTZnQ0c2b2x0eGdHRWtpaExmR0dzVE84a3NTbC5iYnZTNW1MUjc0VGNaQmpkdndrdGlZU09FWUlOdlhwb2g3NUgxRV9peHFSdlEuWmI3MDJDR2ZuTWlPODJNNUVHV2VmdkNjLWxJczJ6TmF5cGIySW1MLldCMVhWR2RzZkprZzZ2NEFxV1hyWHRhN3NEaXpxY3BQSFhZYU5pQ0FTaVZYWlV3c1NfcE5ndFEyd0hJajdMZVdzSWdHYkZXdXFxR2Y1NnAyekcybVNreTFEWjBpUWV3Z3FvWGdmVUFmN25lVE93cFBEcXh2Vzl3WUVwMEcwT3lnb3RJd1lyTllzLThQdk9HMjhSNm1yeDgtQVo1SXdqZF9yN01IY2lqLndIVDhmLl9TUXZoZTRGTElMeGQ4TlFtWmdpUHNIenBNUjdMb2VqZ05Ccmtaa2NhWFdBX0l0WXVaUW5GcmVzNnhaLjl2Zk9oYXZrRlVzR2tkd09BXzl4d3hxRktrWjFwdFg2ckRYSVRYOEtOZWNqLS44c1JWX1hCWTBhd0VKYldfbGtfLWc3Z3pRdzZ5ekpwU3NzcDJQVmVuU1RvNmRWenkxXzlrVTItZkYuNFNfOVB4b250UUtQNVBYb1dwS3R0V3ZjdXRaMyJ9|f4bb8f37a875117b6d00a6186047373adbf18a19bbec240010dada07ae4bdd21; gdxidpyhxdE=caZ%2B5zhC2PMI06udjUDyHDVq5LIkMWZn%2FzNlB2wVtozYD4%2BeSCS1pPlmxyECdnpdjboCvM2rYZlonTSxu4EhX%2Fm1cSeu13NomXIHQ09baC0ZBMlo5lxCKSba5hm9lRGjSSCb7Wl3ncU6BQj51UxiS9ZAnHErSTX0Vx%2BkAvUc5yWgt8GI%3A1653360259456; z_c0=2|1:0|10:1653359445|4:z_c0|92:Mi4xVjhxWUJ3QUFBQUFBNE5BOHBqcjVGQ1lBQUFCZ0FsVk5WWkY1WXdCOHRvcFJVc0VCbVg3WGNveFYyOGdFOFdlRFFn|5d0a1d1b025626b69411c4d8866140777970bd274e4005c339c36f9997ff0105; q_c1=f1d99580036b49bcb693e2e74b9bc647|1653361218000|1653361218000; tst=r; _xsrf=1fd232ad-b88a-4371-a877-94f34e50ed68; ariaDefaultTheme=undefined; KLBRSID=975d56862ba86eb589d21e89c8d1e74e|1653567445|1653564319',
        'referer': 'https://www.zhihu.com/topic/19553176/hot',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        'x-ab-param': 'top_test_4_liguangyi=1;tp_zrec=1;tp_dingyue_video=0;se_ffzx_jushen1=0;qap_question_author=0;qap_question_visitor= 0;pf_adjust=0;tp_topic_style=0;tp_contents=2;pf_noti_entry_num=2',
        'x-ab-pb': 'CqQCPwlQA3QIeAeECeEJ1ArPC2oBVAndB0kJNAxSBWcI5QjHCRsAKgPOCtYEmArcC9cLOwJJCoQKQwCiBtEJ/QqmBJ4F3AfGCVILoANXB4wEjQTcCnoIowlWBTID2ghCCWUKqgoSCZsLiwXgCX4GjQnJCd0KwwnMAlUJDwtHAOkE9gkGCkABBApPA8UJVgz2AtgC8wMwBtgHYAn0CcsJAQnECuQKUQUzBYwFFgbrBsUIqwnICYQC8ArsCk8Kgwq+CjcMPwCmBvQLdAGbB3cHkQnlCVcEEQXXAmALhgqlCgEGdgipCrcDmAiiAzIFJwkpBdYIJwjKCQELuQJBBuMF8QknB/IKxAlrCjEGbAh1CX0CMwS1C7QKzAmhAxYJeQi0APQD4AtpARKSAQAAAAAAAAALAQACAQAEBAEAAAIABAEAAAAAAhUAAAAAAQIAAQABBAQBAgAAAAAAAAAAAgAAAAAAAAAAAAEAAAAAAQAAAAEAAAAAAAIAAAEAAAEAAAAAAAAAAAABAAIAAQAAAAAAAAEAAQAAAAECBwAAAAMAAQAAAAAAABUAAAAAAAAAAAAAAQADAAAAAAAAAAAC',
        'x-requested-with': 'fetch',
        'x-zse-93': '101_3_2.0',
        'x-zse-96': '2.0_aLtBUJ9yoHtYe7tqyg20Ug90STOfo8OyY8xBFJXBe8Yf',
        'x-zst-81': '3_2.0ae3TnRUTEvOOUCNMTQnTSHUZo02p-HNMZBO8YDQqS6kxcHtqXRFZri90-LS9-hp1DufI-we8gGHPgJO1xuPZ0GxCTJHR7820XM20cLRGDJXfgGCBxupMuD_Ie8FL7AtqM6O1VDQyQ6nxrRPCHukMoCXBEgOsiRP0XL2ZUBXmDDV9qhnyTXFMnXcTF_ntRueThRCLtBN_6qtxnJeCi9Vf3rH0IveXSgpqygYLSrULjg3p3UH0mQNBeMxG-qCPvMxqtUtC8GSMxDVYLgFMN9g9QqS8iuo8BweV_DCCywO9bJXM-D3mgu2q3CHGEcXBtUF1Y4L_rr9YnDS1ZJO1-9om1CoBYqH89ho_PceVzvOm3Cw1Lqpm4qfz60p1bTNMqhVyRGNLb7efHhX8hqOy7rHOhC3Kgq3YZGLKMHCm2TSYQ6S1kC3G3bH9wuCyqwefo0HBEwefeHxf2GxMsbOMbUeLkqcBtG2Vwcxy10eLWBHC'
    }
    sessions = requests.session()
    sessions.mount('www.zhihu.com', HTTP20Adapter())
    req = sessions.get(url, headers=headers, stream= True, verify=False, timeout=(5,5))
    req.encoding = 'utf-8'
    data = req.text
    false = False
    null = None
    data = eval(data)
    result = []
    items = data['data']

    for item in items:
        item_type = item['target']['type']
        print(item_type)
        if item_type == 'answer':
            result.append({
                'type': item_type,
                'title': item['target']['question']['title'],
                'author': item['target']['author']['name'],
                'content': item['target']['excerpt']
            })
        elif item_type == 'article':
            result.append({
                'type': item_type,
                'title': item['target']['title'],
                'author': item['target']['author']['name'],
                'content': item['target']['excerpt']
            })
        elif item_type == 'zvideo':
            result.append({
                'type': item_type,
                'title': item['target']['title'],
                'author': item['target']['author']['name'],
                'content': item['target']['video']['playlist']['hd']['url']
            })

    cache.set('spider-zhihu', result)
    print(result)

    return True