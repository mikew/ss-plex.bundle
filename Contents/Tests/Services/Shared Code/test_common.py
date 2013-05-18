import plex_nose

class TestSsEnvironment(plex_nose.TestCase):
    def test_works():
        ok_(isinstance(ss.environment.factory, common.SSPlexEnvironment))

class TestMetadata(plex_nose.TestCase):
    def test_with_episode_numbered():
        numbered_episode = dict(
                display_title = 'foo 1x1 show title',
                display_overview = u'2013-01-01 \u2014 an overview',
                _type = 'episode')

        obj = common.metadata_from(numbered_episode)

        eq_(obj.show, 'foo')
        eq_(obj.season, 1)
        eq_(obj.title, '1. show title')
        eq_(obj.summary, 'an overview')
        eq_(obj.originally_available_at, Datetime.ParseDate('2013-01-01').date())

    def test_with_episode_daily():
        numbered_episode = dict(
                display_title = 'foo: show title 01.01.2013',
                display_overview = u'2013-01-01 \u2014 an overview',
                _type = 'episode')

        obj = common.metadata_from(numbered_episode)

        eq_(obj.show, 'foo')
        eq_(obj.title, 'show title')
        eq_(obj.summary, 'an overview')
        eq_(obj.originally_available_at, Datetime.ParseDate('2013-01-01').date())

    def test_with_episode_subpar():
        subpar_episode = dict(
                display_title = 'foo',
                display_overview = 'an overview',
                _type = 'episode')

        obj = common.metadata_from(subpar_episode)

        eq_(obj.title, 'foo')
        eq_(obj.summary, 'an overview')

    def test_with_movie():
        movie = dict(
                display_title = 'foo',
                display_overview = u'2013-01-01 \u2014 an overview',
                _type = 'movie')

        obj = common.metadata_from(movie)

        eq_(obj.__class__.__name__, 'MovieObject')
        eq_(obj.title, 'foo')
        eq_(obj.summary, 'an overview')
        eq_(obj.originally_available_at, Datetime.ParseDate('2013-01-01').date())

    def test_with_movie_subpar():
        movie = dict(
                display_title = 'foo',
                display_overview = 'an overview',
                _type = 'movie')

        obj = common.metadata_from(movie)

        eq_(obj.title, 'foo')
        eq_(obj.summary, 'an overview')

class TestUrlParsing(plex_nose.TestCase):
    def test_params():
        url = 'http://example.com/foo?foo=1&bar=2'
        params = common.params(url)

        eq_(params.get('foo'), '1')
        eq_(params.get('bar'), '2')

    def test_path():
        url = 'http://example.com/foo?foo=1&bar=2'
        params = common.params(url)

        eq_(params.path, '/foo')
