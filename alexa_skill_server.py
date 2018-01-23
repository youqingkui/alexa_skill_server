import logging

import time

from random import randint, choice

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session

import redis


app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


def get_redis_conn_pool(opts={}, decode_responses=True):
    """
    获取redis连接池
    :param opts: dict redis参数, {'host': '127.0.0.1', 'port': 6379, 'db': 0, 'timeout': 1}
    :param decode_responses: decode_responses bool 是否decode，默认为True
    :return: object 返回redis连接池对象
    """
    pool = redis.ConnectionPool(
        host=opts.get('host', 'localhost'),
        port=int(opts.get('port', 6379)),
        socket_timeout=int(opts.get('timeout', 3)),
        db=int(opts.get('db', 0)),
        decode_responses=decode_responses
    )
    return redis.Redis(connection_pool=pool)


def timestamp_to_date(timestap, format_str='%Y-%m-%d %H:%M:%S'):
    x = time.localtime(int(timestap))
    date_str = time.strftime(format_str, x)
    return date_str

def random_bayby_name(babay_str):
    logging.debug("babay_str => %s" % babay_str)
    list_babay = babay_str.split(',')
    babay_name = choice(list_babay).strip()
    return babay_name


redis_key_prefix = "baybay:record:milk"


@ask.launch
def new_game():

    welcome_msg = render_template('start')

    return question(welcome_msg)


@ask.intent("StartIntent")
def start_recored():

    redis_conn = get_redis_conn_pool()
    current_time = int(time.time())
    date_str = timestamp_to_date(current_time, format_str='%Y-%m-%d')
    redis_key = "%s:%s" % (redis_key_prefix, date_str)
    redis_conn.lpush(redis_key, current_time)
    baby_name = random_bayby_name(render_template('bayby_name'))
    response = render_template('recorded').format(baby_name=baby_name)
    return statement(response)


@ask.intent('AskIntent')
def ask_answer():
    redis_conn = get_redis_conn_pool()
    current_time = int(time.time())
    date_str = timestamp_to_date(current_time, format_str='%Y-%m-%d')
    redis_key = "%s:%s" % (redis_key_prefix, date_str)
    record_content = redis_conn.lrange(redis_key, 0, -1)
    if not redis_conn:
        response = "I did not find today's record, today's time is %s" % date_str
    else:
        total_record = len(record_content)
        last_date = timestamp_to_date(record_content[-1], '%H:%M')
        baby_name = random_bayby_name(render_template('bayby_name'))
        response = "Find %s records, %s last record is %s" % (total_record, baby_name, last_date)
    return statement(response)


@ask.intent("AMAZON.StopIntent")
def stop():
    return statement("Stopping")


# @ask.intent("StartIntent")
#
# def next_round():
#
#     numbers = [randint(0, 9) for _ in range(3)]
#
#     round_msg = render_template('round', numbers=numbers)
#
#     session.attributes['numbers'] = numbers[::-1]  # reverse
#
#     return question(round_msg)


# @ask.intent("AnswerIntent", convert={'first': int, 'second': int, 'third': int})
#
# def answer(first, second, third):
#
#     winning_numbers = session.attributes['numbers']
#     print("first:%s, second:%s, third:%s" % (first, second, third))
#
#     if [first, second, third] == winning_numbers:
#
#         msg = render_template('win')
#
#     else:
#
#         msg = render_template('lose')
#
#     return statement(msg)




if __name__ == '__main__':

    app.run(debug=True, port=5001)
