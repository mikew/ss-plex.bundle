core = None

def sandbox(f):
    import nose

    core.sandbox.publish_api(nose)
    core.sandbox.execute(f.func_code)
