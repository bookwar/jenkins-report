import flask
import report
import scripts

from JR import app

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
