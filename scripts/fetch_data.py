import json
import requests
import dataset


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

    db.begin()
    for job_entry in builds_data:
        for build in job_entry['builds']:

            # FIXME: Build DB is append-only, thus, for efficiency, we
            # should process only new builds with timestamp later than
            # the last one which alredy exists in db

            build['name'] = job_entry['name']
            table.upsert(build, ['name','number'])
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
    update_builds_db(source_file='test.data', dbname='test.db')
