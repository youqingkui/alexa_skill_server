#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/24 16:21
# @Author  : youqingkui
# @File    : help.py
# @Desc    :

import time
import random

def timestamp_to_date(timestap, format_str='%Y-%m-%d %H:%M:%S'):
    x = time.localtime(int(timestap))
    date_str = time.strftime(format_str, x)
    return date_str

def random_choice_res(response):
    lst_res = response.split(',')
    choice_res = random.choice(lst_res).strip()
    return choice_res

def get_today_date(format_str='%Y-%m-%d %H:%M:%S'):
    current_time = int(time.time())
    date_str = timestamp_to_date(current_time, format_str=format_str)
    return date_str

def get_yesterday(format_str='%Y-%m-%d %H:%M:%S'):
    current_time = int(time.time())
    yesterday_timestamp = current_time - 60 * 60 * 24

