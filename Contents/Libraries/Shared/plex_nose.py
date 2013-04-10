from functools import wraps

import os
import nose
import unittest

import Framework

class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print 'setup'

    def setUp(self):
        _dict = Framework.api.datakit.DictKit(core.sandbox)
        _dict._dict_path = '/'
        _dict._load()
        core.sandbox.publish_api(_dict, name = 'Dict')
        #core.sandbox.environment['Dict'] = dict()

    def tearDown(self):
        core.sandbox.call_named_function('Reset', mod_name = 'Dict', raise_exceptions = True)

    #def __init__(self):
        #super(UnitTest, self).__init__()
        #self.arg = arg

def publish_local_file(local_path, name = None):
    local_path = os.path.abspath(__file__ + '/../../../../' + local_path)
    local_file = open(local_path, 'r')
    contents   = local_file.read()
    local_file.close()

    if not name: name = os.path.basename(local_path)
    core.sandbox.publish_api(contents, name = name)

run_once_ = False
def run_once():
    global run_once_
    if run_once_ is False:
        print 'run once'
        core.sandbox.publish_api(nose)
        core.sandbox.publish_api(nose.tools.eq_)
        core.sandbox.publish_api(nose.tools.ok_)
        #if core.init_code: core.sandbox.execute(core.init_code)
        run_once_ = True

def sandbox(f):
    @wraps(f)
    def wrapper(*a, **k):
        run_once()
        core.sandbox.execute(f.func_code)

    return wrapper
