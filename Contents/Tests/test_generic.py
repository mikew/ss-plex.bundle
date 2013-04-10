import plex_nose
import unittest
from plex_nose import sandbox as sandboxed
from nose.tools import *

def setup_mocks():
    from helpers import listings_elements
    plex_nose.core.sandbox.publish_api(listings_elements.mocks, name = 'mocks')

class TestRenderListings(unittest.TestCase):
    @sandboxed
    def test_can_recover_from_errors():
        import generic
        def sim_error(*a, **k): raise Exception()
        generic.JSON.ObjectFromURL = sim_error

        container = generic.render_listings('/')
        rendered = container.objects[0]

        eq_(1, len(container))
        eq_('heading.error', rendered.title._key)

class TestRenderListingsResponse(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        setup_mocks()

    @sandboxed
    def test_can_render_endpoint():
        import generic

        mocked       = mocks['endpoint']
        response     = dict(items = [ mocked ])
        container    = generic.render_listings_response(response, '/')
        rendered     = container.objects[0]
        expected_key = ('/video/ssp/RenderListings?endpoint=%s&default_title=%s' % (
            mocked['endpoint'], mocked['display_title']
        ))

        eq_('DirectoryObject', rendered.__class__.__name__)
        eq_(mocked['display_title'], rendered.title)
        eq_(expected_key, rendered.key)

    @sandboxed
    def test_can_render_show():
        import generic

        mocked       = mocks['show']
        response     = dict(items = [ mocked ])
        container    = generic.render_listings_response(response, '/')
        rendered     = container.objects[0]
        expected_key = ('/video/ssp/series/i0?endpoint=%s&show_title=%s' % (
            mocked['endpoint'], mocked['display_title']
        ))

        eq_('TVShowObject', rendered.__class__.__name__)
        eq_(mocked['display_title'], rendered.title)
        eq_(expected_key, rendered.key)

    @sandboxed
    def test_can_render_show_with_meta():
        import generic

        mocked       = mocks['show_with_meta']
        response     = dict(items = [ mocked ])
        container    = generic.render_listings_response(response, '/')
        rendered     = container.objects[0]
        expected_key = ('/video/ssp/series/i0?endpoint=%s&show_title=%s' % (
            mocked['endpoint'], mocked['display_title']
        ))

        eq_('TVShowObject',             rendered.__class__.__name__)
        eq_(mocked['display_title'],    rendered.title)
        eq_(mocked['artwork'],          rendered.thumb)
        eq_(mocked['display_overview'], rendered.summary)
        eq_(expected_key,               rendered.key)

    @sandboxed
    def test_can_render_episode():
        import generic

        mocked       = mocks['episode']
        response     = dict(items = [ mocked ])
        container    = generic.render_listings_response(response, '/')
        rendered     = container.objects[0]
        expected_key = ('/video/ssp/WatchOptions?endpoint=%s&media_hint=show&title=%s' % (
            mocked['endpoint'], mocked['display_title']
        ))

        eq_('PopupDirectoryObject',  rendered.__class__.__name__)
        eq_(mocked['display_title'], rendered.title)
        eq_(expected_key, rendered.key)

    @sandboxed
    def test_can_render_episode_with_meta():
        import generic

        mocked    = mocks['episode_with_meta']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]

        eq_(mocked['artwork'],          rendered.thumb)
        eq_(mocked['display_overview'], rendered.summary)

    @sandboxed
    def test_can_render_movie():
        import generic

        mocked       = mocks['movie']
        response     = dict(items = [ mocked ])
        container    = generic.render_listings_response(response, '/')
        rendered     = container.objects[0]
        expected_key = ('/video/ssp/WatchOptions?endpoint=%s&media_hint=movie&title=%s' % (
            mocked['endpoint'], mocked['display_title']
        ))

        eq_('PopupDirectoryObject',  rendered.__class__.__name__)
        eq_(mocked['display_title'], rendered.title)
        eq_(expected_key, rendered.key)

    @sandboxed
    def test_can_render_movie_with_meta():
        import generic

        mocked    = mocks['movie_with_meta']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]

        eq_(mocked['artwork'],          rendered.thumb)
        eq_(mocked['display_overview'], rendered.summary)

    @sandboxed
    def test_can_render_foreign():
        import generic
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

    @sandboxed
    def test_can_render_foreign_with_final():
        import generic
        from ss.util import q

        mocked    = mocks['foreign_with_final']
        response  = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered  = container.objects[0]
        expected  = ('//ss/procedure?url=%s&endpoint=%s' % (
            q(mocked['final_url']), q('/')
        ))

        eq_(expected, rendered.url)

    @sandboxed
    def test_can_suggest_title():
        import generic
        response  = dict()
        suggested = 'foo'
        container = generic.render_listings_response(response, '/', default_title = suggested)

        eq_('foo', container.title1)

    @sandboxed
    def test_cannot_suggest_title_when_exists():
        import generic
        response  = dict(title = 'bar')
        suggested = 'foo'
        container = generic.render_listings_response(response, '/', default_title = suggested)

        eq_('bar', container.title1)

class TestIcons(unittest.TestCase):
    @sandboxed
    def test_icon_for_tv():
        import generic
        mocked = dict(endpoint = '/tv', _type = 'endpoint')
        response = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered = container.objects[0]
        ok_('icon-tv.png' in rendered.thumb)

    @sandboxed
    def test_icon_for_movies():
        import generic
        mocked = dict(endpoint = '/movies', _type = 'endpoint')
        response = dict(items = [ mocked ])
        container = generic.render_listings_response(response, '/')
        rendered = container.objects[0]
        ok_('icon-movies.png' in rendered.thumb)

class TestWatchOptions(plex_nose.TestCase):
    @sandboxed
    def test_when_fresh():
        import generic
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

    @sandboxed
    def test_when_in_history():
        import generic
        generic.JSON.ObjectFromURL = lambda *a, **k: dict()
        #generic.bridge.download.history = lambda: ['/']

        container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')

        eq_('media.persisted', container.objects[1].title._key)

    @sandboxed
    def test_when_in_queue():
        import generic
        generic.JSON.ObjectFromURL = lambda *a, **k: dict()
        #generic.bridge.download.queue = lambda: [ dict(endpoint='/') ]

        container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')

        eq_('media.persisted', container.objects[1].title._key)

    @sandboxed
    def test_when_is_downloading():
        import generic
        generic.JSON.ObjectFromURL = lambda *a, **k: dict()
        #generic.bridge.download.current = lambda: dict(endpoint='/')

        container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')

        eq_('media.persisted', container.objects[1].title._key)

    @with_setup(setup_mocks)
    @sandboxed
    def test_with_suggestions():
        import generic
        generic.JSON.ObjectFromURL = lambda *a, **k: dict(items = [ mocks['show_with_meta'] ])

        container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')

        eq_(4, len(container))
        eq_(mocks['show']['display_title'], container.objects[3].title)
