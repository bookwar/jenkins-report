import dataset
import graph_bokeh
from datetimeutils import datetime_from_timestamp


def get_builds(dbname, offset=0, limit=20, query=None, **kwargs):

    db = dataset.connect('sqlite:///%s' % dbname)

    if query:
        return db.query(query, _limit=limit, _offset=offset, order_by='-timestamp', **kwargs)

    table = db.load_table('builds')
    builds = table.find(_limit=limit, _offset=offset, order_by='-timestamp', **kwargs)

    return builds

def get_graph(dbname, limit=5000, **kwargs):

    builds = get_builds(dbname, limit=limit, **kwargs)

    return graph_bokeh.figure_as_html(builds, title="last %s builds" % limit)

def get_last_builds(db):

    last_builds = {}

    for dbname, dbdata in db.items():
        try:
            result = get_builds(
                dbdata['filename'],
                limit=1,
                query='select max(timestamp) from builds'
            )
            last_builds[dbname] = next(result)['max(timestamp)']
        except Exception as e:
            pass

    return last_builds
