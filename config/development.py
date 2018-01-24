#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/20 17:17
# @Author  : youqingkui
# @File    : __init__.py
# @Desc    :

import os


class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://'


    # celery指定导入的任务模块
    CELERY_IMPORTS = [

    ]

    # 发送邮件
    MAIL_CONFIG =  {
        'server': 'xxx',
        'port': 25,
        'send_from': '',
        'user': '',
        'password': '',
        'send_to': ''
    }


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    # cache配置
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'flask_cache_'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = '7403'
    # CACHE_REDIS_PASSWORD = ''
    CACHE_REDIS_DB = '1'

    # redis配置
    REDIS_CONFIG = {
        'default': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0
        },
        # redis缓存
        'session': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 1
        },
        'celery_broker': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 2
        },
        'celery_result_backend': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 3
        },

    }

    # DB配置
    DB_CONFIG = {
        'db_xxx': {
            'dialect': 'mysql',
            'driver': 'mysqldb',
            'host': '',
            'user': '',
            'password': '',
            'database': '',
            'port': 3306,
            'charset': 'utf8'
        },

    }
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_BINDS = dict(
        ((k, '{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}?charset={charset}'.format_map(v)) for k, v
         in DB_CONFIG.items()))

    # celery配置
    CELERY_BROKER_URL = 'redis://{host}:{port}/{db}'.format_map(REDIS_CONFIG['celery_broker']),
    CELERY_RESULT_BACKEND = 'redis://{host}:{port}/{db}'.format_map(REDIS_CONFIG['celery_result_backend'])



class TestingConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,

}.get(os.getenv('FLASK_CONFIG') or 'default', DevelopmentConfig)
