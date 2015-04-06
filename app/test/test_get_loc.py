import nose
import sys, os
sys.path.append(os.path.dirname(
    os.path.dirname(__file__)))

from getloc import GetLoc

def test_init():
    getloc = GetLoc()

def test_parse():
    getloc = GetLoc()

    def do_test(a, b):
        assert getloc.parse(a) == b

    fixtures = (
            ['1138 Fandy Pun St, Arlington, VA', {'place': 'Arlington',
                                                  'state': 'VA'}],
            ['New York, NY , USA', {'place': 'New York',
                                    'state': 'NY'}],
            ['Richmond, VA', {'place': 'Richmond',
                                    'state': 'VA'}],
            )

    for loc, place in fixtures:
        yield do_test, loc, place

def x_retrieve():
    getloc = GetLoc()
    getloc.retrieve_all(['Miami', 'Stanford, CA', '142 Oak Ridge Rd, Bluesville KY'], num_workers=3)
    
    assert getloc.r.get('Miami')
    assert getloc.r.get('Stanford, CA')
    assert getloc.r.get('142 Oak Ridge Rd, Bluesville KY')
