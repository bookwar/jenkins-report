import logging
import requests
import json

'''
Functions which require access to Jenkins Master
'''

logger = logging.getLogger(__name__)

def list_downstream(jenkins_url, job, number='lastBuild'):
    '''Get list of downstream builds

    Return [(name, number),...]
    '''

    params = {}
    params['tree'] = 'subBuilds[jobName,buildNumber],number'

    r = requests.get(
        "%s/job/%s/%s/api/json" % (jenkins_url, job, number),
        verify=False,
        params=params,
    )
    data = json.loads(r.text)
    logger.debug("Data: %s" % data)

    builds = [(job, data['number'])]

    for subbuild in data['subBuilds']:
        builds.append((subbuild['jobName'], subbuild['buildNumber']))

    return builds
