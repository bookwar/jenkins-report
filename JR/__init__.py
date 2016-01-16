import flask
import logging

app = flask.Flask(__name__)

app.config.from_object('config')
app.config.from_envvar('JENKINS_REPORT_SETTINGS', silent=True)

import JR.views
import JR.filters
