#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/20 17:17
# @Author  : youqingkui
# @File    : __init__.py
# @Desc    :

import json
import traceback
from flask import request

from .main import main
from config.error import Err
from application import app


@main.app_errorhandler(404)
def page_not_found(error):
    app.logger.error(error)
    return json.dumps({'code': Err.Not_found, 'msg': Err.Msg.Not_found}), 404


@main.app_errorhandler(500)
def nterror(error):
    try:
        args = request.args if request.method == 'GET' else request.form
        app.logger.debug(args)
    except:
        app.logger.error(traceback.format_exc())
        app.logger.error(error)
    return json.dumps({'code': Err.Unknown_error, 'msg': Err.Msg.Unknown_error}), 500
