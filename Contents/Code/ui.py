def dialog(title, message):           return ObjectContainer(header = L(title), message = L(message))
def confirm(otitle, ocb, **kwargs):   return popup_button(otitle, ocb, **kwargs)
def warning(otitle, ohandle, ocb, **kwargs):
    container = ObjectContainer(header = L(otitle))
    container.add(button(ohandle, ocb, **kwargs))

    return container

def plobj(obj, otitle, cb, **kwargs):
    icon = None

    if 'icon' in kwargs:
        icon = R(kwargs['icon'])
        del kwargs['icon']

    if not isinstance(otitle, Framework.components.localization.LocalString):
        otitle = L(otitle)

    item = obj(title = otitle, key = Callback(cb, **kwargs))
    if icon:
        item.thumb = icon

    return item

def button(otitle, ocb, **kwargs):       return plobj(DirectoryObject,      otitle, ocb, **kwargs)
def popup_button(otitle, ocb, **kwargs): return plobj(PopupDirectoryObject, otitle, ocb, **kwargs)
def input_button(otitle, prompt, ocb, **kwargs):
    item        = plobj(InputDirectoryObject, otitle, ocb, **kwargs)
    item.prompt = L(prompt)
    return item
