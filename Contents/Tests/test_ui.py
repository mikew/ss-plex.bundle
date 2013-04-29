import plex_nose

class UiHelpersTest(plex_nose.TestCase):
    def test_plobj():
        from ui import plobj
        subject = plobj(DirectoryObject, 'title', noop, icon = consts.art)

        eq_(subject.__class__.__name__, 'DirectoryObject')
        eqL_(subject.title, 'title')
        eq_(subject.thumb, R(consts.art))
        eqcb_(subject.key, noop)

    def test_plobj_with_f():
        from ui import plobj
        subject = plobj(DirectoryObject, F('system.status.version', '1.0'), noop, icon = consts.art)

        eq_(subject.__class__.__name__, 'DirectoryObject')
        eqF_(subject.title, 'system.status.version')
        eq_(subject.thumb, R(consts.art))
        eqcb_(subject.key, noop)

    def test_input_button():
        subject = input_button('foo', 'prompt', noop)

        eq_(subject.__class__.__name__, 'InputDirectoryObject')
        eqL_(subject.title, 'foo')
        eqL_(subject.prompt, 'prompt')
        eqcb_(subject.key, noop)

    def test_popup_button():
        subject = popup_button('title', noop)
        eq_(subject.__class__.__name__, 'PopupDirectoryObject')
        eqL_(subject.title, 'title')
        eqcb_(subject.key, noop)

    def test_button():
        subject = button('title', noop)
        eq_(subject.__class__.__name__, 'DirectoryObject')
        eqL_(subject.title, 'title')
        eqcb_(subject.key, noop)

    def test_warning():
        pass
    def test_confirm():
        pass
    def test_dialog():
        pass
