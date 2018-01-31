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
from application.utils.help import timestamp_to_date, random_choice_res
from config.const import DRINK_MILK_ML_PREFIX

zhihu = Blueprint('zhihu', __name__, url_prefix="/zhihu")
ask = Ask(blueprint=zhihu)

logger = logging.getLogger()
logging.getLogger('flask_ask').setLevel(logging.INFO)

@ask.launch
def launch():
    card_title = 'Audio Example'
    text = 'Welcome to an audio example. You can ask to begin demo, or try asking me to play the sax.'
    prompt = 'You can ask to begin demo, or try asking me to play the sax.'
    return question(text).reprompt(prompt).simple_card(card_title, text)


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


@ask.on_playback_nearly_finished()
def nearly_finished():
    _infodump('Stream nearly finished from {}'.format(current_stream.url))

@ask.on_playback_finished()
def stream_finished(token):
    _infodump('Playback has finished for stream with token {}'.format(token))

@ask.session_ended
def session_ended():
    return "{}", 200

def _infodump(obj, indent=2):
    msg = json.dumps(obj, indent=indent)
    app.logger.info(msg)