import os
import sys
import nose

# Put git root into path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import app
import unittest
import requests
from requests.exceptions import HTTPError
import urlparse
from nose.tools import eq_, ok_, raises, nottest, set_trace
from app.config import OPENCPUURL, dburl, port
from app.helpers import ocpu_wrapper
import json

# Nose cannot run generator tests inside subclasses of unittest.testcase
class TestEndpoints(object):
    def setUp(self):
        self.app = app.app.test_client()
    ########################################################################
    ### Helper functions
    ########################################################################
    def construct_endpoint_url(self, func):
        return os.path.join('ocpu/library/rlines/R', func)

    def visit(self, endpoint, method, status, **args):
        rv = self.app.open(endpoint, method=method, **args)
        eq_(rv.status_code, status, rv.get_data())

    ########################################################################
    ### Test functions
    ########################################################################
    @nottest
    def test_opencpu_endpoint_generic_handles(self):
        # Currently used endpoints
        funcs = ['diffindiff', 'store_csv', 'get_features_data']
        endpoints = map(self.construct_endpoint_url, funcs)

        # Endpoints should return 200 when an endpoint exists
        for endpoint in endpoints:
            yield self.visit, endpoint, 'GET', 200
        
        # Endpoints should return 400 when given an empty post
        for endpoint in endpoints:
            yield self.visit, endpoint, 'POST', 400

    def test_opencpu_failure_nonexistent_endpoint(self):
        ''' Does OpenCPU correctly return an error when a nonexistent endpoint
        is requested?'''
        
        endpoint = self.construct_endpoint_url('______nonexistent')
        self.visit(endpoint, 'GET', 400)


    def test_comparison_upload_expected_return_structures(self):
        
        # TODO:
        # This test should not needs to be updated whenever there is a new
        # naming convention 
        self.visit('get_comparison_upload/', 'POST', 200, 
                data=json.dumps({'targetRegion': 'dc'}))

        self.visit('get_comparison_upload/', 'POST', 400, 
                data=json.dumps({'targetRegion': '__nonexistent'}))
    

