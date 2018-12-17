## qg.web -- 快速使用Flask+gunicorn的工具库

[![Build Status](https://travis-ci.org/QunarOPS/qg.web.png?branch=master)](https://travis-ci.org/QunarOPS/qg.web)

使用Flask创建并初始化应用, Blueprint管理路由, 可通过配置选择WSGIserver为werkzeug或gunicorn, 并对使用gunicorn作为容器时填充了默认参数,比如workers、timeout、loglevel等.
