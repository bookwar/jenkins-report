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
    last_builds = report.get_last_builds(app.config['DB'])
    return flask.render_template('hello.html', last=last_builds)

@app.route('/db/<db_name>/builds')
def show_builds_from_db(db_name):
    dbname = app.config['DB'][db_name]['filename']
    offset = int(flask.request.args.get('offset', '0'))
    limit = int(flask.request.args.get('limit', '20'))
    builds = report.get_builds(dbname, offset=offset, limit=limit)
    return flask.render_template('builds.html',
                                 builds=builds,
                                 title="Builds for %s" % app.config['DB'][db_name]['description']
    )

@app.route('/db/<db_name>/graph')
def show_graph_from_db(db_name):
    dbname = app.config['DB'][db_name]['filename']
    graph = report.get_graph(dbname)
    return flask.render_template('graph.html',
                                 title="Graph for %s" % app.config['DB'][db_name]['description'],
                                 graph=graph
    )

@app.route('/update/<db_name>')
def update_db(db_name):
    dbname = app.config['DB'][db_name]['filename']
    key = flask.request.args.get('key', None)
    title = "Update %s" % db_name
    if key == app.config['KEY']:
        number_of_records = scripts.fetch_data.update_db(
            dbname=dbname,
            source=app.config['DB'][db_name]['source'])
        content = "%s records" % number_of_records
    else:
        content = "%s" % "Speak, friend, and enter"

    return flask.render_template('page.html', title=title, content=content)

@app.route('/db/<db_name>/ds/<job>/lastBuild')
@app.route('/db/<db_name>/ds/<job>/last')
@app.route('/db/<db_name>/ds/<job>/<int:number>')
def show_downstream(db_name, job, number='lastBuild'):
    dbname = app.config['DB'][db_name]['filename']
    builds = report.jenkins.list_downstream(
        app.config['DB'][db_name]['source']['url'],
        job,
        number,
        )
    builds_data = []
    for build in builds:
        builds_data += report.get_builds(
            dbname,
            limit=1,
            name=build[0],
            number=build[1],
        )
    graph = report.graph_bokeh.figure_as_html(
        builds_data,
        title="Builds for %s #%s" % builds[0],
    )

    return flask.render_template('graph_and_builds.html',
                                 builds=builds_data,
                                 graph=graph,
    )

@app.route('/db/<db_name>/job/<job>')
def show_job(db_name, job):
    dbname = app.config['DB'][db_name]['filename']

    graph, builds = report.get_data_for_job(dbname, job)

    return flask.render_template('graph_and_builds.html',
                                 builds=builds,
                                 graph=graph,
                                 title="%s - %s" % (db_name, job),
    )

@app.route('/db/<db_name>/jobs/<string>')
def show_jobs(db_name, string):
    dbname = app.config['DB'][db_name]['filename']

    graph, builds = report.get_data_for_jobs(dbname, string)

    return flask.render_template('graph_and_builds.html',
                                 builds=builds,
                                 graph=graph,
                                 title="%s - %s" % (db_name, string),
    )

# Filters ################################################

@app.template_filter('ts_to_time')
def _jinja2_filter_datetime(timestamp):
    if timestamp:
        dt = report.datetimeutils.datetime_from_timestamp(timestamp)
        return str(dt)

@app.template_filter('duration_to_td')
def _jinja2_filter_duration(duration):
    if duration:
        td = report.datetimeutils.timedelta_from_duration(duration)
        return str(td)

@app.template_filter('result_to_css')
def _jinja2_filter_result(result):
    result_to_css = {
        'SUCCESS': 'success',
        'UNSTABLE': 'warning',
        'FAILURE': 'danger',
        'ABORTED': 'default',
        'other': 'info',
    }

    return result_to_css.get(result, result_to_css['other'])


if __name__ == '__main__':
    app.run(debug=True)
