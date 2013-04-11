from functools import wraps

import os
import nose
import unittest

import Framework

run_once_ = False
def run_once():
    global run_once_
    if run_once_ is False:
        core.sandbox.publish_api(nose)
        core.sandbox.publish_api(nose.tools.eq_)
        core.sandbox.publish_api(nose.tools.ok_)
        publish_helpers()
        run_once_ = True

class EmptyDict(Framework.api.datakit.DictKit):
    def Save(self):
        pass

    def _really_save(self):
        pass

def stub_dict():
    _dict = EmptyDict(core.sandbox)
    core.sandbox.publish_api(_dict, name = 'Dict')

def reset_dict():
    core.sandbox.execute('Dict.Reset()')

def publish_helpers():
    def eqL_(given, expected):
        nose.tools.eq_(given._key, expected)

    def eqF_(given, expected):
        nose.tools.eq_(given._key._string1._key, expected)

    def eqcb_(given, expected, **k):
        cb = core.sandbox.environment['Callback'](expected, **k)
        nose.tools.eq_(given, cb)

    core.sandbox.publish_api(eqL_)
    core.sandbox.publish_api(eqF_)
    core.sandbox.publish_api(eqcb_)

def publish_local_file(local_path, name = None):
    local_path = os.path.abspath(core.bundle_path + '/' + local_path)
    local_file = open(local_path, 'r')
    contents   = local_file.read()
    local_file.close()

    if not name: name = os.path.basename(local_path)
    core.sandbox.publish_api(contents, name = name)

def sandbox(f):
    @wraps(f)
    def wrapper(*a, **k):
        run_once()
        stub_dict()
        core.sandbox.execute(f.func_code)
        reset_dict()

    return wrapper

class TestCase(unittest.TestCase):
    def _exc_info(self):
        """Return a version of sys.exc_info() with the traceback frame
           minimised; usually the top level of the traceback frame is not
           needed.
        """
        import sys
        exctype, excvalue, tb = sys.exc_info()
        if sys.platform[:4] == 'java': ## tracebacks look different in Jython
            return (exctype, excvalue, tb)
        return (exctype, excvalue, tb)

    def run(self, result=None):
        if result is None: result = self.defaultTestResult()
        result.startTest(self)
        testMethod = getattr(self, self._testMethodName)
        testMethod = sandbox(testMethod)

        try:
            try:
                self.setUp()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                return

            ok = False
            try:
                testMethod()
                ok = True
            except self.failureException:
                result.addFailure(self, self._exc_info())
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                ok = False
            if ok: result.addSuccess(self)
        finally:
            result.stopTest(self)
