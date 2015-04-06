import unittest
import requests
import json
from config import OPENCPUURL
import os

# These tests are based off of the existing data in the rlines package
# from openads
class ocpu_wrapper():
    def __init__(self, url, baseurl = OPENCPUURL, header={}, files={}, data=''):
        
        self.url= os.path.join(baseurl, url)
        self.baseurl = baseurl
        self.header = header
        self.files = files
        self.data = data
        self.result = None
        self.session_id = None
        self.endpoints = None
    def perform(self):
        print('Calling %s' % self.url)
        self.result = requests.post(self.url, files=self.files, headers=self.header, data=self.data)
        # perform the initial search
        if self.result.status_code == 400:
            print('Error: %s' % self.result.text)
        self.result.raise_for_status()

        self.endpoints = self.result.text.split('\n')
        # Set the list of endpoints
        self.session_id = self.endpoints[0][10:21]
        # Get the session ID
    def get_result_object(self, format='json'):
        """
        Gets the result object of this call as a json object
        """
        if not self.result:
            raise(NameError('Search not performed!'))
        req = requests.get(os.path.join(self.baseurl, 'ocpu','tmp', self.session_id, 'R','.val', format))
        req.raise_for_status()
        return req.json()
    def get_result_pointer(self):
        return self.session_id + '::.val'

def call_r(endpoint, files={}, header={}, data=''):
    """
    Call endpoint and receive link to data object
    """
    if data:
        header = {
                'content-type': 'application/x-www-form-urlencoded'
                }
    api = ocpu_wrapper(files=files, header=header, url=endpoint, data = data)
    api.perform()
    return api.session_id + "::.val"

def get_from_val(session,endpoint='/ocpu/tmp/'):
    """
    Take a session object like 'x4abe33184::.val' and does a 'get' on the json of the object

    This would work with just 'x4abe33184' as well
    """
    if ':' in session:
        session_id = session.split(':')[0]
    #api = ocpu_wrapper(url=endpoint + session_id + '/R/.val')
    r = requests.get('http://localhost' + endpoint + session_id + '/R/.val/json')
    r.raise_for_status()
    #api.perform()
    return r.json()

def list_to_r_array(input_list):
    """
    Function that puts python lists into R argument strings
    """
    if not len(input_list):
        raise Exception('No items in input list')
    if type(input_list[0]) == int or type(input_list[0]) == float:
        return 'c(%s)' % ','.join(map(str,input_list))
        # Just put numbers right in the array
    if type(input_list[0]) == str:
        return 'c(%s)' % ','.join(map(lambda x: '"%s"' % x,input_list))

def dict_to_r_args(input_dict):
    output_args = []
    for k, v in input_dict.iteritems():
        if type(v) == str:
            output_args.append( '%s="%s"' % (k, v))
        elif type(v) == int:
            output_args.append( '%s=%s' % (k, v))
        elif type(v) == bool:
            if v:
                output_args.append( '%s=TRUE' % k)
            else:
                output_args.append( '%s=FALSE' % k)
        elif type(v) == list:
            output_args.append('%s=%s' % (k, list_to_r_array(v)))
        #else:
            #try:
        elif isinstance(v,ocpu_wrapper):
            output_args.append('%s=%s' % (k, v.get_result_pointer()))
            #except:
        else:
            raise Exception('Unknown argument type for %s: %s' % (str(v), type(v)))
    return '&'.join(output_args)


#if __name__ == '__main__':
    #unittest.main()
