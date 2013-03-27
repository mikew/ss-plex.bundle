from nose.tools import eq_
import uas

def mock_all_channels():
    import bridge

    f = open('/Users/mike/Work/python/ss-plex.bundle/Contents/Code/test/uas_plugin_details.json', 'r')
    uas.all_channels = bridge.environment.plex.str_to_json(f.read())
    f.close()

def test_uas_fetch_info():
    mock_all_channels()

    info = uas.info_for('foo.bundle')
    eq_('Foo',            info.title)
    eq_('foo.bundle',     info.bundle_name)
    eq_(['Video'],        info.types)
    eq_('description',    info.description)
    eq_('master',         info.branch)
    eq_('foo-icon.png',   info.icon)
    eq_('April 17, 2011', info.added_on)
    eq_('foo-tracking',   info.tracking_url)
    eq_('git@github.com:owner/foo.bundle.git', info.repo)
