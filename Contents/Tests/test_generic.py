import plex_nose
from nose.tools import *

def setup_mocks():
    from helpers import listings_elements
    plex_nose.core.sandbox.publish_api(listings_elements.mocks, name = 'mocks')

class TestRenderListings(plex_nose.TestCase):
    def test_can_recover_from_errors():
        import mock
        @mock.patch.object(JSON, 'ObjectFromURL', return_value = Exception)
        def test(mock_json):
            container = generic.render_listings('/')
            rendered = container.objects[0]

            eq_(1, len(container))
            eq_('heading.error', rendered.title._key)

        test()

class TestRenderListingsResponse(plex_nose.TestCase):
    @classmethod
    def setup_class(cls):
        setup_mocks()

    def test_can_render_endpoint():
        mocked       = mocks['endpoint']
        response     = dict(items = [ mocked ])
        container    = generic.render_listings_response(response, '/')
        rendered     = container.objects[0]
        expected_key = Callback(generic.RenderListings,
            endpoint      = mocked['endpoint'],
            default_title = mocked['display_title']
        )

        eq_('DirectoryObject', rendered.__class__.__name__)
        eq_(mocked['display_title'], rendered.title)
        eq_(expected_key, rendered.key)

    def test_can_render_show():
        mocked       = mocks['show']
        response     = dict(items = [ mocked ])
        container    = generic.render_listings_response(response, '/')
        rendered     = container.objects[0]
        expected_key = Callback(generic.ListTVShow,
            endpoint = mocked['endpoint'],
            show_title = mocked['display_title'],
            refresh = 0
        )

        eq_('TVShowObject',             rendered.__class__.__name__)
        eq_(mocked['display_title'],    rendered.title)
        eq_(mocked['display_overview'], rendered.summary)
        eq_(mocked['artwork'],          rendered.thumb)
        eq_(expected_key,               rendered.key)

    def test_can_render_episode():
        mocked    = mocks['episode']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]
        expected_key = Callback(generic.WatchOptions,
            endpoint = mocked['endpoint'],
            title = mocked['display_title'],
            media_hint = 'show'
        )

        eq_('PopupDirectoryObject',     rendered.__class__.__name__)
        eq_(mocked['display_title'],    rendered.title)
        eq_(mocked['display_overview'], rendered.summary)
        eq_(mocked['artwork'],          rendered.thumb)
        eq_(expected_key, rendered.key)

    def test_can_render_movie():
        mocked    = mocks['movie']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]
        expected_key = Callback(generic.WatchOptions,
            endpoint = mocked['endpoint'],
            title = mocked['display_title'],
            media_hint = 'movie'
        )

        eq_('PopupDirectoryObject',  rendered.__class__.__name__)
        eq_(mocked['display_title'],    rendered.title)
        eq_(mocked['display_overview'], rendered.summary)
        eq_(mocked['artwork'],          rendered.thumb)
        eq_(expected_key, rendered.key)

    def test_can_render_foreign():
        from ss.util import q

        mocked    = mocks['foreign']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]
        expected  = ('//ss/translate?original=%s&foreign=%s&endpoint=%s' % (
            mocked['original_url'], mocked['foreign_url'], q('/')
        ))

        eq_('VideoClipObject', rendered.__class__.__name__)
        eq_(mocked['domain'], rendered.title)
        eq_(expected, rendered.url)

    def test_can_render_foreign_with_final():
        from ss.util import q

        mocked    = mocks['foreign_with_final']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]
        expected  = ('//ss/procedure?url=%s&endpoint=%s' % (
            q(mocked['final_url']), q('/')
        ))

        eq_(expected, rendered.url)

    def test_can_suggest_title():
        response  = dict()
        suggested = 'foo'
        container = generic.render_listings_response(response, '/', default_title = suggested)

        eq_('foo', container.title1)

    def test_cannot_suggest_title_when_exists():
        response  = dict(title = 'bar')
        suggested = 'foo'
        container = generic.render_listings_response(response, '/', default_title = suggested)

        eq_('bar', container.title1)

class TestIcons(plex_nose.TestCase):
    def test_icon_for_tv():
        mocked = dict(endpoint = '/tv', _type = 'endpoint')
        response = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered = container.objects[0]
        ok_('icon-tv.png' in rendered.thumb)

    def test_icon_for_movies():
        mocked = dict(endpoint = '/movies', _type = 'endpoint')
        response = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered = container.objects[0]
        ok_('icon-movies.png' in rendered.thumb)

class TestWatchOptions(plex_nose.TestCase):
    def test_when_fresh():
        generic.JSON.ObjectFromURL = lambda *a, **k: dict()

        container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
        watch_now_key = ('//ss/wizard?endpoint=%s&avoid_flv=%s' % (
            '/', int(Prefs['avoid_flv_streaming'])
        ))

        eq_(3, len(container))

        # May be due to the fact that it is a VideoClipObject
        # but we cannot test against I18N key here
        eq_('Watch Now',       container.objects[0].title)
        eq_('VideoClipObject', container.objects[0].__class__.__name__)
        eq_(watch_now_key,     container.objects[0].url)

        eq_('media.watch-later', container.objects[1].title._key)
        eq_('media.all-sources', container.objects[2].title._key)

    def test_when_in_history():
        import mock

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(bridge.download, 'history', return_value = ['/'])
        def test(*a):
            container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
            eq_('media.persisted', container.objects[1].title._key)

        test()

    def test_when_in_queue():
        import mock

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(bridge.download, 'queue', return_value = [dict(endpoint = '/')])
        def test(*a):
            container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
            eq_('media.persisted', container.objects[1].title._key)

        test()

    def test_when_is_downloading():
        import mock

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(bridge.download, 'current', return_value = dict(endpoint = '/'))
        @mock.patch.object(bridge.download, 'assumed_running', return_value = True)
        def test(*a):
            container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
            eq_('media.persisted', container.objects[1].title._key)

        test()

    @with_setup(setup_mocks)
    def test_with_suggestions():
        import mock

        @mock.patch.object(JSON, 'ObjectFromURL', return_value = dict(items = [ mocks['show'] ]))
        def test(mock_json):
            container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')

            eq_(4, len(container))
            eq_(mocks['show']['display_title'], container.objects[3].title)

        test()
