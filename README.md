# Jenkins Report

This tool can

* Fetch list of builds from Jenkins, put it into table 'builds' of sqlite database.
  Table columns are:
```
    sqlite> .mode line
    sqlite> select * from builds limit 1;
              index = 1
               name = 389-ds-base
             number = 552
            builtOn = Fedora20
                url = http://jenkins.cloud.fedoraproject.org/job/389-ds-base/552/
          timestamp = 1432667167192
                 id = 552
             result = SUCCESS
           duration = 320450
    fullDisplayName = 389-ds-base #552
```
* Use database to create interactive graphs:

     ![Screenshot](/screenshot.png?raw=true)

Based on

 * [Bokeh](http://bokeh.pydata.org/)
 * [Flask](http://flask.pocoo.org/)

Uses [Bootstrap Flatly](https://bootswatch.com/flatly/) theme.

# To run in development mode

## System Dependencies
```
 gcc-c++ libpng-devel freetype-devel
```

## Inside virtualenv

```
  $ pip install -r requirements.txt
  $ cp config.py.example config.py
  $ python runserver.py
```
Use browser to go to http://localhost:5000/

## To create/update database

```
  $ curl localhost:5000/update/<db_name>?key=friend
```

# To Do

* Pagination for builds
* Query by name, by date range, by anything

