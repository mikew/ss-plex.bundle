def dialog(title, message):
    title   = ensure_localized(title)
    message = ensure_localized(message)

    return ObjectContainer(header = title, message = message)

def confirm(otitle, ocb, **kwargs):
    return popup_button(otitle, ocb, **kwargs)

def warning(otitle, ohandle, ocb, **kwargs):
    otitle    = ensure_localized(otitle)
    container = ObjectContainer(header = otitle)
    container.add(button(ohandle, ocb, **kwargs))

    return container

def plobj(obj, otitle, cb, **kwargs):
    icon   = None
    otitle = ensure_localized(otitle)

    if 'icon' in kwargs:
        icon = R(kwargs['icon'])
        del kwargs['icon']

    item = obj(title = otitle, key = Callback(cb, **kwargs))
    if icon:
        item.thumb = icon

    return item

def button(otitle, ocb, **kwargs):
    return plobj(DirectoryObject, otitle, ocb, **kwargs)

def popup_button(otitle, ocb, **kwargs):
    return plobj(PopupDirectoryObject, otitle, ocb, **kwargs)

def input_button(otitle, prompt, ocb, **kwargs):
    prompt = ensure_localized(prompt)
    item   = plobj(InputDirectoryObject, otitle, ocb, **kwargs)
    item.prompt = prompt

    return item

def ensure_localized(string):
    #string = str(string)

    l = Framework.components.localization.LocalString
    f = Framework.components.localization.LocalStringFormatter
    is_localized = isinstance(string, l) or isinstance(string, f)

    if not is_localized:
        string = L(string)

    return string
