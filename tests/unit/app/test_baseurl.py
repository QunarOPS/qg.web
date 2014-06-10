#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @ 2014 OPS, Qunar Inc. (qunar.com)
#
# Author: zhen.pei <zhen.pei@qunar.com>
#

from testtools import TestCase

from flask import Blueprint
from qg.web.app import QFlaskApplication
from qg.test.apps import make_webtest_by_qflaskapp
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
        app = make_webtest_by_qflaskapp(TestApplication())
        resp = app.get('/')
        self.assertEqual(resp.body, "hello world")
        self.assertEqual(resp.status_code, 200)
        resp = app.get('/abc/123', expect_errors=True)
        self.assertEqual(resp.status_code, 404)

    @mock_cli_options('test', '--web-base-url', '/abc/123')
    def test_baseurl(self):
        app = make_webtest_by_qflaskapp(TestApplication())
        resp = app.get('/', expect_errors=True)
        self.assertEqual(resp.body, "Page not found.")
        self.assertEqual(resp.status_code, 404)
        resp = app.get('/abc/123')
        self.assertEqual(resp.body, "hello world")
        self.assertEqual(resp.status_code, 200)
        resp = app.get('/abc/123/456', expect_errors=True)
        self.assertEqual(resp.status_code, 404)
