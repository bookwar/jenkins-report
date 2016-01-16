import json
import requests
import argparse
import logging
import dataset

logger = logging.getLogger(__name__)

def fetch_builds_data(jenkins_url):
    '''Get json data of all Jenkins builds

    JENKINS_URL/api/json?
      tree=jobs[name,builds[number,result,duration,builtOn,id,timestamp,fullDisplayName]]

    Return builds_data dictionary with following schema::

     [
      {
        "name" : <job_name>,
        "builds" : [
                     {
                       "duration" : <build_duration>,
                       "timestamp" : <build_timestamp>,
                       "id" : <build_id>,
                       "url" : <build_url>,
                       "number" : <build_number>,
                       "result" : <build_result>,
                       "builtOn" : <node>,
                       "fullDisplayName": <build_display_name>,
                     }
                   ],
                   ...
      },
      ...

     ]
    '''

    params = {}
    params['tree'] = 'jobs[name,builds[number,url,result,duration,builtOn,id,timestamp,fullDisplayName]]'
    r = requests.get(
        "%s/api/json" % jenkins_url,
        verify=False,
        params=params
    )
    builds_data = json.loads(r.text)["jobs"]
    logger.info("Fetched %d job entries" % len(builds_data))
    return builds_data

def store_builds_data(builds_data, dbname):
    '''Saves builds_data in SQLite database

    Database has one table `builds` with following columns::

       index           = 5
       builtOn         = slave01.example.com
       name            = check_shell
       timestamp       = 1432739306340
       number          = 113
       id              = 2015-05-27_15-08-26
       result          = SUCCESS
       duration        = 3796
       fullDisplayName = check_shell #113

    '''

    db = dataset.connect('sqlite:///%s' % dbname)

    table = db.get_table('builds', primary_id='index')
    last_stored_build = table.find_one(_limit=1, order_by='-timestamp')
    if last_stored_build:
        last_stored_build_timestamp = last_stored_build['timestamp']
    else:
        last_stored_build_timestamp = 0

    logger.debug(last_stored_build)
    skipped_counter = 0
    db.begin()
    for job_entry in builds_data:
        for build in job_entry['builds']:
            if build['timestamp'] >= last_stored_build_timestamp:
                build['name'] = job_entry['name']
                table.upsert(build, ['name','number'])
            else:
                skipped_counter+=1
    logger.debug("Skipped builds: %d" % skipped_counter)
    db.commit()

    return len(db['builds'])

def update_builds_db(dbname, source_file=None, source_url=None):

    if source_file:
        with open(source_file, 'r') as f:
            builds_data = json.loads(f.readline())['jobs']
    elif source_url:
        builds_data = fetch_builds_data(source_url)
    else:
        raise ValueError("No URL and no source file specified")

    return store_builds_data(builds_data, dbname)

def update_db(dbname, source):

    source_file = source.get('file')
    source_url = source.get('url')

    if source_file:
        with open(source_file, 'r') as f:
            builds_data = json.loads(f.readline())['jobs']
    elif source_url:
        builds_data = fetch_builds_data(source_url)
    else:
        raise ValueError("No URL and no source file specified")

    return store_builds_data(builds_data, dbname)

if __name__ == '__main__':

    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--datafile',
                        help="file with JSON source data",
                        default=None,
    )
    parser.add_argument('--url',
                        help="URL of Jenkins instance",
                        default=None,
    )
    parser.add_argument('-d', '--dbname',
                        help="Filename of the SQLite database",
                        default='output.db'
    )

    parser.add_argument('-v', '--verbose',
                        help="Enable debug output",
                        action="store_true",
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug(args)

    update_builds_db(dbname=args.dbname, source_file=args.datafile, source_url=args.url)
