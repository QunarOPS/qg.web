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


from testtools import TestCase

from flask import Blueprint
from qg.web.app import QFlaskApplication
from qg.test.apps import test_wsgi_app
from qg.test.mocks import mock_cli_options

bp = Blueprint("testbp", "testbp")


@bp.route("/")
def index():
    return "hello world"


class TestApplication(QFlaskApplication):
    name = "test-app"
    version = "1.9"

    def init_flask_app(self):
        super(TestApplication, self).init_flask_app()
        self.register_blueprint(bp)


class BaseurlTestCase(TestCase):

    @mock_cli_options('test')
    def test_no_baseurl(self):
        app = test_wsgi_app(TestApplication())
        resp = app.get('/')
        self.assertEqual(resp.body, "hello world")
        self.assertEqual(resp.status_code, 200)
        resp = app.get('/abc/123', expect_errors=True)
        self.assertEqual(resp.status_code, 404)

    @mock_cli_options('test', '--web-base-url', '/abc/123')
    def test_baseurl(self):
        app = test_wsgi_app(TestApplication())
        resp = app.get('/', expect_errors=True)
        self.assertEqual(resp.body, "Page not found.")
        self.assertEqual(resp.status_code, 404)
        resp = app.get('/abc/123/')
        self.assertEqual(resp.body, "hello world")
        self.assertEqual(resp.status_code, 200)
        resp = app.get('/abc/123/456', expect_errors=True)
        self.assertEqual(resp.status_code, 404)
