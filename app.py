import flask
import logging
import report
import scripts

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

### Routes ###############################################

@app.route('/')
def hello_world():
    return flask.render_template('hello.html')

@app.route('/db/<db_name>/builds')
def show_builds_from_db(db_name):
    dbname = "%s.db" % db_name
    offset = int(flask.request.args.get('offset', '0'))
    limit = int(flask.request.args.get('limit', '20'))
    builds = report.get_builds(dbname, offset=offset, limit=limit)
    return flask.render_template('builds.html',
                                 builds=builds,
                                 title="Builds for %s" % app.config['DB'][db_name]['description']
    )

@app.route('/db/<db_name>/graph')
def show_graph_from_db(db_name):
    dbname = "%s.db" % db_name
    graph = report.get_graph(dbname)
    return flask.render_template('graph.html',
                                 title="Graph for %s" % app.config['DB'][db_name]['description'],
                                 graph=graph)

@app.route('/update/<db_name>')
def update_db(db_name):

    key = flask.request.args.get('key', None)
    title = "Update %s" % db_name
    if key == app.config['KEY']:
        number_of_records = scripts.fetch_data.update_db(
            dbname="%s.db" % db_name,
            source=app.config['DB'][db_name]['source'])
        content = "%s records" % number_of_records
    else:
        content = "%s" % "Speak, friend, and enter"

    return flask.render_template('page.html', title=title, content=content)

##########################################################


if __name__ == '__main__':
    app.run(debug=True)
