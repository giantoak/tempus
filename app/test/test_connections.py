import os
import sys
import nose

# Put git root into path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import app
import unittest
import requests
import urlparse
from nose.tools import eq_, ok_, raises, nottest
from app.config import OPENCPUURL, dburl

class InitializationTests(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_init(self):
        ''' Is the import chain within the app handled correctly? '''
        assert self.app

    def test_opencpu_running(self):
        ''' Is the OpenCPU server running and receiving requests? '''
        url = urlparse.urljoin(OPENCPUURL, 'ocpu')
        req_root = requests.get(url)
        eq_(req_root.status_code, 200, 
                'OpenCPU server is not running at {}'.format(
                    OPENCPUURL))

    def test_opencpu_packages(self):
        ''' Are the required R packages installed? '''
        # a naked request on /ocpu/libraries returns a list of currently
        # installed packages
        url_packages = urlparse.urljoin(OPENCPUURL, 'ocpu/library')
        r = requests.get(url_packages)
        eq_(r.status_code, 200, 'OpenCPU library listing ({}): {}'.format(
            url_packages, r.text))
        packages = r.text.split()

        # TODO abstract R installation process so packages can be read by nose
        required_libraries = ['rlines']
        for lib in required_libraries:
            yield ok_, lib in packages, 'Required R library {} not installed!'\
                    .format(lib)
    
    def test_db_connection(self):
       ''' Can we connect to the database? '''
       import sqlalchemy
       engine = sqlalchemy.create_engine(dburl)
       conn = engine.connect()

       ok_(conn, '''Database endpoint {} not available; configure dburl in 
            app/config.py'''.format(conn))

