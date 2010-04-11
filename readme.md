# pyGoogleReaderClient

PyGoogleReaderClient is a Google Reader client. It is based on the comments found in these <a href="http://code.google.com/p/pyrfeed/wiki/GoogleReaderAPI">notes</a> (as of autumn 2009). The client is based on version 0.9.1 of <a href="http://pypi.python.org/pypi/restkit/">restkit</a>.

## Tests

Open and edit test/testgooglereader.py and edit the cfg dict in the setUp method of the testcase. Use a (test) google reader username and password and a client id so Google can identify the client. Then run nosetests -v test/testgooglereader.py to run the tests. This is a bit rubbish but I don't know of nice way to pass arguments to nose.

## Todo

* Update to use the latest version of restkit (1.3.0+). Will then be able to remove the json stuff and support oAuth.
