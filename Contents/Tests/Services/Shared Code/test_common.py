import plex_nose

class TestSsEnvironment(plex_nose.TestCase):
    def test_works():
        ok_(isinstance(ss.environment.factory, common.SSPlexEnvironment))
