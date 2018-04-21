#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/28 19:59
# @Author  : youqingkui
# @File    : zhihu.py
# @Desc    :


import time
import os
import traceback
import logging
import json
from flask_ask import Ask, statement, question, audio, current_stream
from flask import Blueprint, current_app as app, render_template
from application.utils.lib import get_redis_conn_pool
from application.utils.help import timestamp_to_date, random_choice_res, get_today_date
from config.const import DRINK_MILK_ML_PREFIX, REMIX_INFO_PREFIX, REMIX_QUEUE_PREFIX

zhihu = Blueprint('zhihu', __name__, url_prefix="/zhihu")
ask = Ask(blueprint=zhihu)

logger = logging.getLogger()
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def launch():
    card_title = 'Zhihu Remix'
    text = "Welcome to zhihu remix. You can ask today or yesterday's audio information"
    prompt = 'You can ask today, or try asking me yesterday.'
    return question(text).reprompt(prompt).simple_card(card_title, text)


@ask.intent('TodayIntent')
def today_remix():
    today = get_today_date(format_str='%Y-%m-%d')
    redis_conn = get_redis_conn_pool()
    redis_key = '%s:%s' % (REMIX_INFO_PREFIX, today)
    audio_record = redis_conn.get(redis_key)
    if audio_record:
        audio_record = json.loads(audio_record)
        queue_key = REMIX_QUEUE_PREFIX
        for audio_info in audio_record:
            skill_url = audio_info.get('skill_url')
            redis_conn.lpush(queue_key, skill_url)
        redis_conn.expire(queue_key, 10 * 60)
        stream_url = audio_record[-1]['skill_url']
    else:
        sorry_speech = 'Sorry, not find today remix'
        return statement(sorry_speech)

    speech = "Here's today remix"
    return audio(speech).play(stream_url)

@ask.intent('YesterdayIntent')
def today_remix():
    speech = "Here's yesterday's remix"
    stream_url = 'https://alexa.youqingkui.me/static/s2t9_Computer_Speech_Demonstration.mp3'
    return audio(speech).play(stream_url)


@ask.on_playback_nearly_finished()
def nearly_finished():
    redis_conn = get_redis_conn_pool()
    queue_key = REMIX_QUEUE_PREFIX
    next_stream = redis_conn.lpop(queue_key)
    if next_stream:
        _infodump("发现下一个播放队列")
        return audio().enqueue(next_stream)
    else:
        _infodump('Nearly finished with last reminx in playlist')

@ask.intent('DemoIntent')
def demo():
    speech = "Here's one of my favorites"
    stream_url = 'https://alexa.youqingkui.me/static/s2t9_Computer_Speech_Demonstration.mp3'
    return audio(speech).play(stream_url, offset=93000)


# 'ask audio_skil Play the sax
@ask.intent('SaxIntent')
def george_michael():
    speech = 'yeah you got it!'
    stream_url = 'https://alexa.youqingkui.me/static/a5ecebaa2f24d2483099444f2b0c5982.mp3'
    return audio(speech).play(stream_url)


@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio('Paused the stream.').stop()


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming.').resume()

@ask.intent('AMAZON.StopIntent')
def stop():
    return audio('stopping').clear_queue(stop=True)



# optional callbacks
@ask.on_playback_started()
def started(offset, token):
    _infodump('STARTED Audio Stream at {} ms'.format(offset))
    _infodump('Stream holds the token {}'.format(token))
    _infodump('STARTED Audio stream from {}'.format(current_stream.url))


@ask.on_playback_stopped()
def stopped(offset, token):
    _infodump('STOPPED Audio Stream at {} ms'.format(offset))
    _infodump('Stream holds the token {}'.format(token))
    _infodump('Stream stopped playing from {}'.format(current_stream.url))


# @ask.on_playback_nearly_finished()
# def nearly_finished():
#     _infodump('Stream nearly finished from {}'.format(current_stream.url))

@ask.on_playback_finished()
def stream_finished(token):
    _infodump('Playback has finished for stream with token {}'.format(token))

@ask.session_ended
def session_ended():
    return "{}", 200

def _infodump(obj, indent=2):
    msg = json.dumps(obj, indent=indent)
    app.logger.info(msg)