#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/20 17:17
# @Author  : youqingkui
# @File    : __init__.py
# @Desc    :


class Err(object):
    Invalid_request = 400
    Not_found = 404
    Internal_server_error = 500
    Unknown_error = 510


    class Msg(object):
        Invalid_request = 'Invalid Request'
        Internal_server_error = 'Internal Server Error'
        Not_found = 'Not Found'
        Unknown_error = 'Unknown Error'
