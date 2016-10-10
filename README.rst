OSIRISDB
========

This is a Flask/SQLAlchemy web interface to a database of OSIRIS observations.

It is a work in progress.

To install, get the source code, then use pip to get dependencies::
    
    $ pip install -r requirements.txt
    

To run the Flask development server::
    
    $ export FLASK_APP=osirisdb
    $ export FLASK_DEBUG=1
    $ flask run
    

To run the full server using twisted::
    
    $ twistd web --wsgi osirisdb.app --port 5000
    

To shutdown the twistd server::
    
    $ kill $(cat twistd.pid)
    

To import OSIRIS data files, use::
    
    $ export FLASK_APP=osirisdb
    $ flask oimport /path/to/my/osiris/fits/files/*.fits
    
