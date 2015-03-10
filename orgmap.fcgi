#!/home/username/orgmap/env/bin/python

import sys
from os.path import join
import os

from paste.deploy import loadapp
from pyramid import paster
from flup.server.fcgi_fork import WSGIServer

INI = 'production.ini'

path = '/home/username/orgmap'
ini = join(path, INI)

# Redirect stdout and stderr
os.chdir(path)
sys.stdout = file('fcgi.log', 'a')
sys.stderr = sys.stdout

paster.setup_logging(ini)
app = loadapp('config:{0}'.format(ini))
server = WSGIServer(app)
server.run()
