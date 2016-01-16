import flask
import logging

app = flask.Flask(__name__)

app.config.from_object('config')
app.config.from_envvar('JENKINS_REPORT_SETTINGS', silent=True)

if not app.debug:
    file_handler = logging.FileHandler('error.log')
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

import JR.views
import JR.filters
