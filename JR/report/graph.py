#from matplotlib import pyplot as plt
import logging

from datetimeutils import *


logger = logging.getLogger(__name__)

def set_hourly_x_ticks(plt):
    '''Set X-Axis to show hours'''
    xmin, xmax = plt.xlim()
    logger.debug("xmin: %s %s" % (xmin, datetime_from_timestamp(xmin)))

    ceiling_xmin = datetime_from_timestamp(xmin).replace(
        minute=0,
        second=0,
        microsecond=0
    ) + datetime.timedelta(hours=1)
    logger.debug("ceiling_xmin: %s" % ceiling_xmin)

    ceiling_xmin_timestamp = datetime_to_timestamp(ceiling_xmin)
    logger.debug("ceiling_xmin_timestamp: %s" % ceiling_xmin_timestamp)

    x_ticks = xrange(int(ceiling_xmin_timestamp), int(xmax), 1000*60*60)
    plt.xticks(
        x_ticks,
        map(lambda dt: datetime_from_timestamp(dt).strftime("%H:%M"), x_ticks),
        rotation='vertical',
    )

def result_to_color(result):
    if result == 'SUCCESS':
        return 'green'
    elif result == 'FAILURE':
        return 'red'
    elif result == 'ABORTED':
        return 'gray'
    else:
        return 'blue'

def plot_data(builds_data, nodes, title="Graph"):
    # left: timestamp
    left = []
    # width: duration (if duration == 0 build is still running)
    width = []
    # bottom: slave_index * 11
    bottom = []
    # height: 10
    height = 10
    # bar names
    names = []
    # colors: red, green or gray, depending on build status
    color = []

    max_time = datetime_to_timestamp(datetime.datetime.now())

    for build_data in builds_data:
        print build_data
        left.append(build_data['timestamp'])
        if build_data['duration'] == 0:
            logger.debug("Build %s is still running" % build_data['fullDisplayName'])
            duration = max_time - build_data['timestamp']
            width.append(duration)
        else:
            width.append(build_data['duration'])
        bottom.append(nodes.index(build_data['builtOn']) * 11)
        names.append(build_data['fullDisplayName'])
        color.append(result_to_color(build_data['result']))

    plt.barh(bottom, width, height, left, color=color, alpha=0.2, linewidth=0.1)
    plt.yticks(
        xrange(5, len(nodes)*11, 11),
        map(lambda node: node.replace("mirantis.net",".."), nodes),
        fontsize=6,
    )

    set_hourly_x_ticks(plt)

    plt.xlabel('Time')
    plt.title(title)

    # Set labels for every bar
    counters = [0] * len(nodes)
    # for i in xrange(len(names)):
    #     l, b, name = left[i], bottom[i], names[i]
    #     plt.text(
    #         l + 50000,
    #         b + 3*counters[b/11],
    #         name,
    #         horizontalalignment='left',
    #         verticalalignment='bottom',
    #         fontsize=4,
    #         rotation=10,
    #     )
    #     counters[b/11] = (counters[b/11] + 1) % 3

    plt.savefig('test.png')
    return plt
