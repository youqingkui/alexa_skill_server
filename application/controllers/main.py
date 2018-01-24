#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/20 17:17
# @Author  : youqingkui
# @File    : __init__.py
# @Desc    :


import time
import traceback
from flask_ask import Ask, statement, question
from flask import Blueprint, current_app as app, render_template
from application.utils.lib import get_redis_conn_pool
from application.utils.help import timestamp_to_date, random_choice_res
from config.const import DRINK_MILK_ML_PREFIX

main = Blueprint('main', __name__)
ask = Ask(blueprint=main)

@ask.launch
def new_game():

    welcome_msg = render_template('welcome')
    welcome_msg = random_choice_res(welcome_msg)

    return question(welcome_msg)


@ask.intent("BabyDrink", convert={'ml_number': int})
def start_recored(ml_number):
    if ml_number is None:
        response = render_template('sorry')
        return statement(response)
    redis_conn = get_redis_conn_pool()
    current_time = int(time.time())
    date_str = timestamp_to_date(current_time, format_str='%Y-%m-%d')
    redis_key = "%s:%s" % (DRINK_MILK_ML_PREFIX, date_str)
    redis_conn.zadd(redis_key, ml_number, current_time)
    baby_name = random_choice_res(render_template('bayby_name'))
    response = render_template('recorded').format(baby_name=baby_name, ml_number=ml_number)
    return statement(response)


@ask.intent('AskIntent')
def ask_answer():
    redis_conn = get_redis_conn_pool()
    current_time = int(time.time())
    date_str = timestamp_to_date(current_time, format_str='%Y-%m-%d')
    redis_key = "%s:%s" % (DRINK_MILK_ML_PREFIX, date_str)
    record_content = redis_conn.zrange(redis_key, 0, -1, withscores=True)
    if not redis_conn:
        response = "I did not find today's record, today's time is %s" % date_str
    else:
        total_record = len(record_content)
        last_date = timestamp_to_date(record_content[-1][-1], '%H:%M')
        drink_mi = record_content[-1][0]
        baby_name = random_choice_res(render_template('bayby_name'))
        response = "Find %s records, %s last record is %s %s ml" % (total_record, baby_name, last_date, drink_mi)
    return statement(response)


@ask.intent("AMAZON.StopIntent")
def stop():
    return statement("Stopping")

