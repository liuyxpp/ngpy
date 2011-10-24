# Ensure the application can be imported.
# the path is where our app locates
import sys
sys.path.insert(0,'/export/home/lyx/opt/lyx/ngpy')
# Or you can use site.addsitedir
#
#import site
#site.addsitedir('/export/home/lyx/opt/lyx/ngpy')

# the NGPy configuration file
import os
os.environ['NGPY_CONFIG'] = '/export/home/lyx/opt/lyx/ngpy/ngpy.cfg'

from ngpy import app as application

# Following is a test code
# comment out them and comment above lines to test
# by browsing http://10.22.4.52:8080/ngpy/ngpy.wsgi
# The Apache should be configured after http.conf.sample.
# If Hello World! shows up, everythin went right.
# Otherwise, check the error in ~/opt/apache2/logs/error_log
#
#def application(environ,start_response):
#    status = '200 OK'
#    output = 'Hello World'
#
#    response_headers = [('Content-type','text/plain'),('Content-Length',str(len(output)))]
#    start_response(status,response_headers)
#    return [output]

