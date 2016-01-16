import report

from JR import app

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
