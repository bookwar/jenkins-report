#
# Dictionary of databases
#
#   'source' can be 'file' with JSON string or
#                   'url' - Jenkins master URL
#
# If both 'file' and 'url' sources are present, only 'file' is used

DB = {
    'test': {
        'description': 'Test Data',
        'filename': 'test.db',
        'source': {
            'file': 'test.data'
        },

    },
    'fedora': {
        'description': 'Fedora Jenkins',
        'filename': 'fedora.db',
        'source': {
            'url': 'http://jenkins.cloud.fedoraproject.org'
        },

    },
}

# Totally secret key. Used in /update/<db_name> request.

KEY = "friend"

# String shown in the top left corner

PROJECT_NAME = 'Jenkins Report'
