from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool

#from bokeh.objects import DatetimeTickFormatter

import logging

from datetimeutils import *


logger = logging.getLogger(__name__)

# def set_hourly_x_ticks(plt):
#     '''Set X-Axis to show hours'''
#     xmin, xmax = plt.xlim()
#     logger.debug("xmin: %s %s" % (xmin, datetime_from_timestamp(xmin)))

#     ceiling_xmin = datetime_from_timestamp(xmin).replace(
#         minute=0,
#         second=0,
#         microsecond=0
#     ) + datetime.timedelta(hours=1)
#     logger.debug("ceiling_xmin: %s" % ceiling_xmin)

#     ceiling_xmin_timestamp = datetime_to_timestamp(ceiling_xmin)
#     logger.debug("ceiling_xmin_timestamp: %s" % ceiling_xmin_timestamp)

#     x_ticks = xrange(int(ceiling_xmin_timestamp), int(xmax), 1000*60*60)
#     plt.xticks(
#         x_ticks,
#         map(lambda dt: datetime_from_timestamp(dt).strftime("%H:%M"), x_ticks),
#         rotation='vertical',
#     )

def get_build_color(build_data):

    result = build_data['result']

    if result == 'SUCCESS':
        return 'green'
    elif result == 'FAILURE':
        return 'red'
    elif result == 'UNSTABLE':
        return 'yellow'
    elif result == 'ABORTED':
        return 'gray'
    else:
        return 'blue'

def figure_as_html(builds_data, nodes, title):
    ''' For every build in builds_data draw rectangle we define

    :center_x: = left(=timestamp) + width/2
    :center y: = bottom(=node_index*11) + height/2
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
    hover.tooltips = "@label"

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
        #        center_y.append(build_bottom + height/2)
        center_y.append(build_data['builtOn'])
        color.append(build_color)


    source = ColumnDataSource(
        data=dict(
            x=center_x,
            y=center_y,
            width=width,
            c=color,
            label=label,
        )
    )
    p.rect('x', 'y', 'width', height, color='c', source=source, line_color=None, fill_alpha=0.4)
    #    p.xaxis[0].formatter = DatetimeTickFormatter()

    script, div = components(p)
    return script + div


    # plt.barh(bottom, width, height, left, color=color, alpha=0.2, linewidth=0.1)
    # plt.yticks(
    #     xrange(5, len(nodes)*11, 11),
    #     map(lambda node: node.replace("mirantis.net",".."), nodes),
    #     fontsize=6,
    # )

    # set_hourly_x_ticks(plt)

    # plt.xlabel('Time')
    # plt.title(title)

    # # Set labels for every bar
    # counters = [0] * len(nodes)
    # # for i in xrange(len(names)):
    # #     l, b, name = left[i], bottom[i], names[i]
    # #     plt.text(
    # #         l + 50000,
    # #         b + 3*counters[b/11],
    # #         name,
    # #         horizontalalignment='left',
    # #         verticalalignment='bottom',
    # #         fontsize=4,
    # #         rotation=10,
    # #     )
    # #     counters[b/11] = (counters[b/11] + 1) % 3

    # plt.savefig('test.png')
    # return plt
