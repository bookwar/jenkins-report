from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool

import logging

from datetimeutils import *


logger = logging.getLogger(__name__)

def get_build_color(build_data):

    result = build_data['result']

    if result == 'SUCCESS':
        return 'green'
    elif result == 'FAILURE':
        return 'red'
    elif result == 'UNSTABLE':
        return 'gold'
    elif result == 'ABORTED':
        return 'gray'
    else:
        return 'blue'

def figure_as_html(builds_data, nodes, title):
    ''' For every build in builds_data draw rectangle with data:

    :center_x: = left(=timestamp) + width/2
    :center y: = builtOn
    :width: = duration
    :height: = 100
    :color: = result_to_color(result)
    :label: = fullDisplayName
    '''

    TOOLS="pan,xwheel_zoom,box_zoom,reset,previewsave,hover"

    p = figure(x_axis_type="datetime", y_range=nodes, width=900,
               tools=TOOLS,
               title=title,
               toolbar_location="below"
    )
    # p.rect(x=[1, 2, 3], y=[1, 2, 3], width=0.2, height=40, color="#CAB2D6",
    # angle = pi/3, height_units="screen")

    hover = p.select(dict(type=HoverTool))

    hover.tooltips = '<font color="@color">&bull;</font> @label'

    center_x = []
    center_y = []
    width = []
    height = 0.95
    label = []
    color = []

    max_time = datetime_to_timestamp(datetime.datetime.now())

    for build_data in builds_data:
        logger.debug("Processing build %s" % build_data)

        build_left = build_data['timestamp']

        if build_data['duration'] == 0:
            logger.debug("Build %s is still running" % build_data['fullDisplayName'])
            duration = max_time - build_data['timestamp']
            build_width = duration
        else:
            build_width = build_data['duration']

        build_bottom = nodes.index(build_data['builtOn']) * 105
        build_label = build_data['fullDisplayName']

        build_color = get_build_color(build_data)

        width.append(build_width)
        label.append(build_label)
        center_x.append(build_left + build_width/2)
        center_y.append(build_data['builtOn'])
        color.append(build_color)


    source = ColumnDataSource(
        data=dict(
            x=center_x,
            y=center_y,
            width=width,
            color=color,
            label=label,
        )
    )
    p.rect('x', 'y', 'width', height, color='color', source=source, line_color=None, fill_alpha=0.4)

    script, div = components(p)
    return script + div
