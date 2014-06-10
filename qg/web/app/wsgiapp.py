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

import sys
import multiprocessing

from oslo.config import cfg
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple

from qg.core.exception import QException
from qg.core.app import QApplication


web_opts = [
    cfg.StrOpt('base-url',
               default='/',
               help='The url prefix of this site.'),
    cfg.StrOpt('run-mode',
               default="local",
               choices=('gunicorn', 'local'),
               help="Run server use the specify mode."),
    cfg.StrOpt('bind',
               default='0.0.0.0',
               help='The IP address to bind'),
    cfg.IntOpt('port',
               default=5000,
               help='The port to listen'),
]

gunicorn_opts = [
    cfg.StrOpt('config',
               default=None,
               help='The path to a Gunicorn config file.'),
    cfg.IntOpt('worker-count',
               default=0,
               help='Process worker count in gunicorn mode.'),
    cfg.BoolOpt('daemon',
                default=False,
                help='Run gunicorn mode as a daemon.'),
    cfg.StrOpt('accesslog',
               default=None,
               help='The Access log file to write to.'
               '"-" means log to stderr.'),
    cfg.BoolOpt('ignore-healthcheck-accesslog',
                default=False),
    cfg.IntOpt('timeout',
               default=30,
               help='Workers silent for more than this many seconds are '
               'killed and restarted.')
]

CONF = cfg.CONF
CONF.register_cli_opts(web_opts, 'web')
CONF.register_cli_opts(gunicorn_opts, 'gunicorn')


class WsgiNotInitialized(QException):
    message = "Wsgi-app was not initialized."


class QWsgiApplication(QApplication):

    def init_app(self):
        super(QWsgiApplication, self).init_app()
        self.wsgi_app = None

    def configure(self):
        super(QWsgiApplication, self).configure()
        self._set_base_url(CONF.web.base_url)

    def _debug_run(self):
        self.flask_app.debug = True
        CONF.debug = True
        run_simple(CONF.web.bind,
                   CONF.web.port,
                   self.wsgi_app,
                   use_reloader=CONF.debug,
                   use_debugger=CONF.debug)

    def _gunicorn_run(self):
        from gunicorn.app.base import Application
        app = self.wsgi_app

        class QlibGunicornApp(Application):

            def init(self, parser, opts, args):
                worker_count = CONF.gunicorn.worker_count
                if worker_count <= 0:
                    worker_count = multiprocessing.cpu_count() * 2 + 1
                logger_class = "simple"
                if CONF.gunicorn.ignore_healthcheck_accesslog:
                    logger_class = "qlib.web.glogging.GunicornLogger"
                return {
                    'bind': '{0}:{1}'.format(CONF.web.bind, CONF.web.port),
                    'workers': worker_count,
                    'daemon': CONF.gunicorn.daemon,
                    'config': CONF.gunicorn.config,
                    'accesslog': CONF.gunicorn.accesslog,
                    'timeout': CONF.gunicorn.timeout,
                    'logger_class': logger_class
                }

            def load(self):
                return app

        # NOTE(zhen.pei): 为了不让gunicorn默认匹配sys.argv[1:]
        sys.argv = [sys.argv[0]]
        QlibGunicornApp().run()

    def _set_base_url(self, base_url):
        base_url = base_url.strip()
        if not base_url.startswith("/"):
            base_url = "/" + base_url
        self.base_url = base_url

    def run(self):
        if CONF.web.run_mode == "local":
            self._debug_run()
        elif CONF.web.run_mode == "gunicorn":
            self._gunicorn_run()

    def append_wsgi_middlewares(self, *middlewares):
        if self.wsgi_app is None:
            raise WsgiNotInitialized()
        for middleware in middlewares:
            self.wsgi_app = middleware(self.wsgi_app)
        return self

    def set_wsgi_app(self, app, base_url=None):
        if base_url is None:
            base_url = self.base_url
        if base_url != "/":
            self.wsgi_app = DispatcherMiddleware(simple_404_app, {
                base_url: app
            })
        else:
            self.wsgi_app = app


def simple_404_app(environ, start_response):
    status = '404 NOT FOUND'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [u"Page not found.".encode('utf8')]
