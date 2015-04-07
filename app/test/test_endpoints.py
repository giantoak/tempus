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
from nose.tools import eq_, ok_, raises, nottest, set_trace
from app.config import OPENCPUURL, dburl

def construct_endpoint_url(func):
    return urlparse.urljoin(OPENCPUURL, os.path.join('ocpu/library/rlines/R', 
        func))

# Nose cannot run generator tests inside subclasses of unittest.testcase
class TestEndpoints(object):
    def setUp(self):
        self.app = app.app.test_client()
    
    ########################################################################
    ### Helper functions
    ########################################################################
    def http_get(self, endpoint, status):
        r = requests.get(endpoint)
        eq_(r.status_code, status, '''HTTP GET on {} did not return
200 as expected. Received {} ({})'''.format(endpoint, r.text, 
                r.status_code))

    def http_post(self, endpoint, status, **args):
        ''' Anticipate 400 error with args as arguments '''
        r = requests.post(endpoint, params=args)
        eq_(r.status_code, status, '''HTTP POST on {} with data {} did not 
return 400 as expected. Received {} ({})'''.format(endpoint, args,
                r.text, r.status_code))

    ########################################################################
    ### Test functions
    ########################################################################
    def test_opencpu_endpoint_generic_handles(self):
        '''Are the opencpu endpoints returning expected values?'''
        # Currently used endpoints
        funcs = ['diffindiff', 'store_csv', 'get_features_data']
        endpoints = map(construct_endpoint_url, funcs)

        # Endpoints should return 200 when an endpoint exists
        for endpoint in endpoints:
            yield self.http_get, endpoint, 200
        
        # Endpoints should return 400 when given an empty post
        for endpoint in endpoints:
            yield self.http_post, endpoint, 400

    def test_opencpu_failure_nonexistent_endpoint(self):
        ''' Does OpenCPU correctly return an error when a nonexistent endpoint
        is requested?'''
        
        endpoint = construct_endpoint_url('______nonexistent')
        
        r = requests.get(endpoint)
        
        # OpenCPU returns a 400 (not 404) error code for nonexistent endpoints
        eq_(r.status_code, 400, '''OpenCPU did not return 400 for nonexistent
route {} -- is it configured weirdly?: {} ({})'''.format(endpoint,
            r.text, r.status_code))
    
