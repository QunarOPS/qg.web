# -*- coding: utf-8 -*-
#
# Copyright @ 2014 OPS, Qunar Inc. (qunar.com)
#
# Author: zhen.pei <zhen.pei@qunar.com>
#

from gunicorn import glogging


class GunicornLogger(glogging.Logger):

    def access(self, resp, req, environ, request_time):
        # ignore healthcheck
        if environ.get('RAW_URI') == '/healthcheck.html':
            return
        super(GunicornLogger, self).access(resp, req, environ, request_time)
