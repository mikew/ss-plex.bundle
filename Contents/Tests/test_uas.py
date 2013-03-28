import plex_nose
from plex_nose import sandbox as sandboxed
from nose.tools import with_setup

def mock_all_channels():
    import uas
    import simplejson

    f = open('/Users/mike/Work/python/ss-plex.bundle/Contents/Tests/uas_plugin_details.json', 'r')
    uas.all_channels = simplejson.loads(f.read())
    f.close()

    plex_nose.core.sandbox.publish_api(uas)

def test_uas_fetch_info():
    mock_all_channels()

    @sandboxed
    def test():
        info = uas.info_for('foo.bundle')
        nose.tools.eq_('Foo',            info.title)
        nose.tools.eq_('foo.bundle',     info.bundle_name)
        nose.tools.eq_(['Video'],        info.types)
        nose.tools.eq_('description',    info.description)
        nose.tools.eq_('master',         info.branch)
        nose.tools.eq_('foo-icon.png',   info.icon)
        nose.tools.eq_('April 17, 2011', info.added_on)
        nose.tools.eq_('foo-tracking',   info.tracking_url)
        nose.tools.eq_('git@github.com:owner/foo.bundle.git', info.repo)

    test()
