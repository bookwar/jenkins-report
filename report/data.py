import dataset
import graph_bokeh


def get_builds(dbname, offset=None, since=None, limit=20):

    db = dataset.connect('sqlite:///%s' % dbname)
    table = db.load_table('builds')

    builds = table.find(_limit=limit, _offset=offset, order_by='-timestamp')

    return builds

def get_graph(dbname):

    db = dataset.connect('sqlite:///%s' % dbname)
    table = db.load_table('builds')

    builds = table.find(order_by='-timestamp', _limit=5000)
    builds_data = [item for item in builds]
    nodes = sorted(
        list(
            set(
                [item['builtOn'] for item in builds_data]
            )
        )
    )

    return graph_bokeh.figure_as_html(builds_data, nodes, title="last 5000 builds")
