from bokeh.plotting import figure, ColumnDataSource
from bokeh.io import vform
from bokeh.embed import components
from bokeh.models import HoverTool

import logging

from datetimeutils import *


logger = logging.getLogger(__name__)

def get_build_color(build_data):

    color_map = {
        'SUCCESS': 'green',
        'UNSTABLE': 'gold',
        'FAILURE': 'red',
        'ABORTED': 'gray',
        'other': 'blue',
    }

    return color_map.get(build_data['result'], color_map['other'])

def figure_as_html(builds_data, nodes=None, title=None, with_labels=False):
    ''' For every build in builds_data draw rectangle with data:

    :center_x: = left(=timestamp) + width/2
    :center y: = builtOn
    :width: = duration
    :height: = 100
    :color: = result_to_color(result)
    :label: = fullDisplayName
    '''

    # Data

    center_x = []
    center_y = []
    width = []
    left = []
    height = 0.95
    label = []
    color = []

    max_time = datetime_to_timestamp(datetime.datetime.now())

    for build_data in builds_data:
        logger.debug("Processing build %s" % build_data)

        build_left = build_data['timestamp']

        if build_data['duration'] == 0 and not build_data['result']:
            logger.debug("Build %s is still running" % build_data['fullDisplayName'])
            duration = max_time - build_data['timestamp']
            build_width = duration
        else:
            build_width = build_data['duration']

        build_label = build_data['fullDisplayName']
        build_color = get_build_color(build_data)

        left.append(build_left)
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
            left=left,
            color=color,
            label=label,
        )
    )

    if not nodes:
        nodes = sorted(list(set(center_y)))

    # Plot properties

    TOOLS="pan,xwheel_zoom,box_zoom,reset,previewsave,hover,resize"

    p = figure(x_axis_type="datetime", y_range=nodes, width=900,
               tools=TOOLS,
               title=title,
               toolbar_location="below",
               height=max(min(len(nodes)* 40, 800),100),
    )

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = '<font color="@color">&bull;</font> @label'

    # Draw data
    p.rect('x', 'y', 'width', height, color='color', source=source,
           line_width=1,
           line_color='white',
           line_alpha=0.4,
           fill_alpha=0.4,
    )

    if with_labels:
        # Add labels layer
        p.text('left', 'y', 'label',
               source=source,
               angle=0.3,
               name="Labels",
               text_font_size='6pt',
               text_baseline='middle',
               text_alpha=0.8,
               x_offset=map(lambda x: x % 3 * 20, xrange(len(label))),
               y_offset=map(lambda y: y % 2 * 10 -5 , xrange(len(label))),
        )

    # To HTML

    script, div = components(p)
    return script + div
