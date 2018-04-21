#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/4 11:58
# @Author  : youqingkui
# @File    : zhihu_remix.py
# @Desc    :


import os
import sys
import json
import  requests
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)
from config.const import REMIX_INFO_PREFIX
from application.utils.lib import get_redis_conn_pool
from application.utils.help import timestamp_to_date

def get_remix():
    url = "https://api.zhihu.com/remix-api/columns/1/tracks"
    headers = {
        'Host': "api.zhihu.com",
        'Connection': "keep-alive",
        'Authorization': "Bearer 1.1TVMjAAAAAAALAAAAYAJVTcHil1rVn2oacxF0VXs9xl-9hTeksv9viA==",
        'Accept': "*/*",
        'x-app-za': "OS=iOS&Release=11.2.1&Model=iPhone7,2&VersionName=4.9.0&VersionCode=808&Width=750&Height=1334&DeviceType=Phone&Brand=Apple&OperatorType=46002",
        'X-UDID': "AACAf7I_9wlLBce97XEdEEKFfKh4nBrq33o=",
        'X-APP-VersionCode': "808",
        'Accept-Language': "zh-Hans-CN;q=1, en-US;q=0.9",
        'X-ZST-82': "1.0AHBrx8YGFw0LAAAASwUAADEuMFu1dVoAAAAAUWTTKdkoJfVd_VN02dFMB0yNz7Y=",
        'X-API-Version': "3.0.79",
        'If-None-Match': "\"3412cfc1ccef148ad6e830a52290eeb06572721a\"",
        'X-Network-Type': "WiFi",
        'User-Agent': "osee2unifiedRelease/4.9.0 (iPhone; iOS 11.2.1; Scale/2.00)",
        'X-Ab-Param': "top_p=2",
        'X-APP-Build': "release",
        'X-SUGER': "SURGVj1FRDhENTM3OS00RTIxLTQxNTAtOEE3RC02NTE4RUREMDlBNjk7",
        'X-APP-VERSION': "4.9.0",
        'Cookie': "zst_82=1.0AHBrx8YGFw0LAAAASwUAADEuMFu1dVoAAAAAUWTTKdkoJfVd_VN02dFMB0yNz7Y=; __utma=51854390.2100135278.1517311713.1517311713.1517311713.1; __utmv=51854390.010--; __utmz=51854390.1517311713.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); q_c1=fb07bf8605274baf9cb7955db22362a4|1517311422000|1517311422000; d_c0=AACAf7I_9wlLBce97XEdEEKFfKh4nBrq33o=|1517663570; aliyungf_tc=AQAAADX+3jUjVQ0AvWxK387q+WUlUahX; q_c0=2|1:0|10:1517311425|4:q_c0|80:MS4xVFZNakFBQUFBQUFMQUFBQVlBSlZUY0hpbDFyVm4yb2FjeEYwVlhzOXhsLTloVGVrc3Y5dmlBPT0=|b758288c0452028599f46325da5105a18390942034270350b91705f09f7a90bb; z_c0=\"2|1:0|10:1517311425|4:z_c0|80:MS4xVFZNakFBQUFBQUFMQUFBQVlBSlZUY0hpbDFyVm4yb2FjeEYwVlhzOXhsLTloVGVrc3Y5dmlBPT0=|d07a44b2f81fc10ff8ff4e93c79cc9064775ef2ffa9737f8725dd6f2dc67e762\"",
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "9e29387e-539a-7e08-e6a4-6e954cb3ece8"
    }

    response = requests.request("GET", url, headers=headers)

    res_json = response.json()
    list_remix = res_json.get('data', [])
    for remix in list_remix:
        remix_title = remix.get('title', '')
        audio_info = remix.get('audio', {})
        publish_at = remix.get('publish_at')
        md5_value = audio_info.get('md5', '')
        audio_url = audio_info.get('url')
        print(remix_title, audio_url)
        save_audio(remix_title, audio_url, publish_at, md5_value)

def save_audio(title, url, publish_at, md5_value):
    response = requests.get(url)
    save_path = '/Users/youqingkui/PycharmProjects/alexa_skill_server/application/scripts'
    save_path = '/data/python_server/alexa_skill_server/application/static'
    save_name = '%s.mp3' % (md5_value)
    save_file = '%s/%s' % (save_path, save_name)
    publish_date = timestamp_to_date(publish_at, format_str="%Y-%m-%d")
    with open(save_file, 'wb') as f:
        f.write(response.content)
    redis_conn = get_redis_conn_pool()
    redis_key = '%s:%s' % (REMIX_INFO_PREFIX, publish_date)
    audio_record = redis_conn.get(redis_key)
    audio_info = {
        'title': title,
        'url': url,
        'skill_url': '%s/static/%s' % ('https://alexa.youqingkui.me', save_name)
    }
    if not audio_record:
        audio_record = [audio_info]
    else:
        audio_record = json.loads(audio_record)
        audio_record.append(audio_info)
    redis_conn.set(redis_key, json.dumps(audio_record))




if __name__ == '__main__':
    get_remix()