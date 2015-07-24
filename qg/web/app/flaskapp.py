# -*- coding: utf-8 -*-
#
# Copyright 2013, Qunar OPSDEV
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# Author: jaypei <jaypei97159@gmail.com>
#

from flask import Flask
from oslo_config import cfg

from qg.core import exception
from qg.web.app import QWsgiApplication


CONF = cfg.CONF


class QFlaskApplicationError(exception.QException):
    message = "QFlaskApplication Error"


class QFlaskApplication(QWsgiApplication):

    def init_app(self):
        super(QFlaskApplication, self).init_app()
        self.flask_app = None
        self.init_flask_app()

    def configure(self):
        super(QFlaskApplication, self).configure()
        self.set_wsgi_app(self.flask_app)

    def init_flask_app(self, flask_args=None, flask_kwargs=None):
        # init flask arguments
        flask_args = [] if flask_args is None else flask_args
        flask_kwargs = {} if flask_kwargs is None else flask_kwargs
        flask_args.insert(0, self.name)
        # create flask application
        self.flask_app = Flask(*flask_args, **flask_kwargs)
        self.flask_app.debug = CONF.debug
        # NOTE(jianingy): Pass exceptions to faultwrapper
        self.flask_app.config['PROPAGATE_EXCEPTIONS'] = True

    def register_blueprint(self, *args, **kwargs):
        self.flask_app.register_blueprint(*args, **kwargs)
