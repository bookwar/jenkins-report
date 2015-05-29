import datetime

def datetime_from_id(build_id):
    '''Convert Jenkins BUILD_ID to datetime'''
    return datetime.datetime.strptime(build_id, '%Y-%m-%d_%H-%M-%S')


def datetime_from_timestamp(timestamp):
    '''Convert timestamp (in seconds) to UTC time'''
    return datetime.datetime.utcfromtimestamp(timestamp/1000.0)


def datetime_to_timestamp(dt, epoch=datetime.datetime(1970,1,1)):
    '''Convert naive datetime to timestamp (in seconds)'''
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**3


def timedelta_from_duration(duration):
    '''Convert Jenkins duration to timedelta object'''
    return datetime.timedelta(milliseconds=duration)
