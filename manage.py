#!/usr/bin/env python
# -*- coding:utf-8 -*-


from application import app
from flask_script import Manager

# 附加路由和自定义的错误页面
from application.controllers import main as main_blueprint

app.register_blueprint(main_blueprint)

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
