#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/20 17:17
# @Author  : youqingkui
# @File    : __init__.py
# @Desc    :

import os
import sys



import logging
from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache
from config.development import config

from cloghandler import ConcurrentRotatingFileHandler

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

db = SQLAlchemy()
cache = Cache()


def create_app():
    app = Flask(__name__)

    # 日志模块
    rotateHandler = ConcurrentRotatingFileHandler('%s/logs/service.log' % PROJECT_PATH, 'a', 800 * 1024 * 1024,
                                                  backupCount=10,
                                                  encoding='utf-8')
    datefmt_str = '%Y-%m-%d %H:%M:%S'
    format_str = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s'
    formatter = logging.Formatter(format_str, datefmt_str)
    rotateHandler.setFormatter(formatter)
    app.logger.addHandler(rotateHandler)
    app.logger.setLevel(logging.DEBUG)

    app.config.from_object(config)
    config.init_app(app)

    # 初始化db
    db.init_app(app)

    # 初始化cache
    cache.init_app(app)

    return app


def create_celery(app):
    celery = Celery(app.name,
                    broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['CELERY_RESULT_BACKEND']
                    )
    celery.conf.update(app.config)
    task = celery.Task

    class ContextTask(task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = create_app()

celery = create_celery(app)
