import plex_nose
from plex_nose import sandbox as sandboxed
from nose.tools import *

def setup_env():
    endpoint = dict(
        _type = 'endpoint',
        display_title = 'foo',
        endpoint = 'bar'
    )

    movie = dict(
        _type = 'movie',
        display_title = 'foo',
        endpoint = 'bar'
    )

    movie_with_meta = movie.copy()
    movie_with_meta.update(dict(
        display_overview = '42',
        artwork = 'http://example.com/artwork.jpg'
    ))

    show = dict(
        _type = 'show',
        display_title = 'foo',
        endpoint = 'bar'
    )

    show_with_meta = show.copy()
    show_with_meta.update(dict(
        display_overview = '42',
        artwork = 'http://example.com/artwork.jpg'
    ))

    episode = dict(
        _type = 'episode',
        display_title = 'foo',
        endpoint = 'bar'
    )

    episode_with_meta = episode.copy()
    episode_with_meta.update(dict(
        display_overview = '42',
        artwork = 'http://example.com/artwork.jpg'
    ))

    foreign = dict(
        _type = 'foreign',
        domain = 'domain',
        original_url = 'original',
        foreign_url = 'foreign'
    )

    foreign_with_final = foreign.copy()
    foreign_with_final.update(dict(
        final_url = 'final'
    ))

    mocks = dict(
        endpoint = endpoint,
        movie = movie,
        movie_with_meta = movie_with_meta,
        show = show,
        show_with_meta = show_with_meta,
        episode = episode,
        episode_with_meta = episode_with_meta,
        foreign = foreign,
        foreign_with_final = foreign_with_final
    )

    plex_nose.core.sandbox.publish_api(mocks, name = 'mocks')

@with_setup(setup_env)
@sandboxed
def test_can_render_endpoint():
    import generic

    mocked   = mocks['endpoint']
    response = dict(
        items = [ mocked ]
    )

    container    = generic.render_listings_response(response, '/')
    rendered     = container.objects[0]
    expected_key = ('/video/ssp/RenderListings?endpoint=%s&default_title=%s' % (
        mocked['endpoint'], mocked['display_title']
    ))

    eq_('DirectoryObject', rendered.__class__.__name__)
    eq_(mocked['display_title'], rendered.title)
    eq_(expected_key, rendered.key)

@with_setup(setup_env)
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

@with_setup(setup_env)
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

@with_setup(setup_env)
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

@with_setup(setup_env)
@sandboxed
def test_can_render_episode_with_meta():
    import generic

    mocked    = mocks['episode_with_meta']
    response  = dict(items = [ mocked ])
    container = generic.render_listings_response(response, '/')
    rendered  = container.objects[0]

    eq_(mocked['artwork'],          rendered.thumb)
    eq_(mocked['display_overview'], rendered.summary)

@with_setup(setup_env)
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

@with_setup(setup_env)
@sandboxed
def test_can_render_movie_with_meta():
    import generic

    mocked    = mocks['movie_with_meta']
    response  = dict(items = [ mocked ])
    container = generic.render_listings_response(response, '/')
    rendered  = container.objects[0]

    eq_(mocked['artwork'],          rendered.thumb)
    eq_(mocked['display_overview'], rendered.summary)

@with_setup(setup_env)
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

@with_setup(setup_env)
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

@sandboxed
def test_watch_options():
    import generic
    def stubbed_json(*args, **kwargs): return dict()
    generic.JSON.ObjectFromURL = stubbed_json

    container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')
    watch_now_key = ('//ss/wizard?endpoint=%s&avoid_flv=%s' % (
        '/', int(Prefs['avoid_flv_streaming'])
    ))

    eq_(3, len(container))

    eq_('Watch Now',       str(container.objects[0].title))
    eq_('VideoClipObject', container.objects[0].__class__.__name__)
    eq_(watch_now_key,     container.objects[0].url)

    eq_('Watch Later',      str(container.objects[1].title))
    eq_('View All Sources', str(container.objects[2].title))

@with_setup(setup_env)
@sandboxed
def test_watch_options_with_suggestions():
    import generic
    def stubbed_json(*args, **kwargs): return dict(items = [ mocks['show_with_meta'] ])
    generic.JSON.ObjectFromURL = stubbed_json

    container = generic.WatchOptions(endpoint = '/', title = 'foo', media_hint = 'show')

    eq_(4, len(container))
    eq_(mocks['show']['display_title'], container.objects[3].title)
