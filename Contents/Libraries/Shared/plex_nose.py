from functools import wraps
import os
import nose

core = None

def publish_local_file(local_path, name = None):
    local_path = os.path.abspath(__file__ + '/../../../../' + local_path)
    local_file = open(local_path, 'r')
    contents   = local_file.read()
    local_file.close()

    if not name: name = os.path.basename(local_path)
    core.sandbox.publish_api(contents, name = name)

def sandbox(f):
    @wraps(f)
    def wrapper():
        core.sandbox.publish_api(nose)
        core.sandbox.publish_api(nose.tools.eq_)
        core.sandbox.publish_api(nose.tools.ok_)
        core.sandbox.execute(f.func_code)

    return wrapper
