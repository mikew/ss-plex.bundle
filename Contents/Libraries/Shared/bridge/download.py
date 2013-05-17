import ss
import settings

import os
import signal
import thread

log = ss.util.getLogger('ss.bridge.download')

def queue():           return settings.get('downloads',        [])
def history():         return settings.get('download_history', [])
def failed():          return settings.get('download_failed',  [])
def avoid_flv():       return settings.get('avoid_flv_downloading')
def speed_limit():     return settings.get('download_limit', 0)
def current():         return settings.get('download_current')
def current_pid():     return current().get('pid')
def assumed_running(): return settings.get('download_current') != None
def curl_running():    return pid_running(current_pid())
def running_windows(): return 'nt' == os.name

def strategy():
    return settings.get('download_strategy', 'curl')

def clear_history(): settings.clear('download_history')
def clear_current(): settings.clear('download_current')
def clear_failed():  settings.clear('download_failed')

def append(**kwargs):
    queue().append(kwargs)
    settings.persist()

def append_failed(**kwargs):
    failed().append(kwargs)
    settings.persist()

def append_history(endpoint):
    history().append(endpoint)
    settings.persist()

def remove(endpoint):
    remove_from_collection(endpoint, queue())

def remove_failed(endpoint):
    remove_from_collection(endpoint, failed())

def set_current(download):
    settings.set('download_current', download)
    settings.persist()

def is_current(endpoint):
    return assumed_running() and endpoint == current()['endpoint']

def in_history(endpoint):
    return endpoint in history()

def get_from_collection(endpoint, collection):
    found = filter(lambda d: d['endpoint'] == endpoint, collection)
    if found: return found[0]

def remove_from_collection(endpoint, collection):
    found = get_from_collection(endpoint, collection)
    if not found: return

    collection.remove(found)
    settings.persist()

def from_queue(endpoint):
    return get_from_collection(endpoint, queue())

def from_failed(endpoint):
    return get_from_collection(endpoint, failed())

def is_queued(endpoint):
    return bool(from_queue(endpoint))

def is_failed(endpoint):
    return bool(from_failed(endpoint))

def get(endpoint):
    _current = is_current(endpoint)
    if _current: return current()

    _queued = from_queue(endpoint)
    if _queued: return _queued

    _failed = from_failed(endpoint)
    if _failed: return _failed

def includes(endpoint):
    if get(endpoint): return True
    return in_history(endpoint)

def was_successful(endpoint):
    return is_current(endpoint) or is_queued(endpoint) or in_history(endpoint)

def update_library(section): pass

def command(command):
    if not curl_running():
        return

    signals  = [ signal.SIGTERM, signal.SIGINT ]
    commands = [ 'cancel',       'next' ]
    to_send  = signals[commands.index(command)]

    return signal_process(current_pid(), to_send)

def force_success():
    import os

    _d = current()
    _h = _d['media_hint']
    dest_key = '%s_destination' % _h
    destination = settings.get(dest_key)
    localfile = os.path.join(destination, _d['title'])
    partfile = localfile + '.part'

    try:    os.rename(partfile, localfile)
    except: pass

    update_library(_h)
    append_history(_d['endpoint'])
    clear_current()
    dispatch()

def force_failure():
    import os

    _d = current()
    _h = _d['media_hint']
    dest_key = '%s_destination' % _h
    destination = settings.get(dest_key)
    localfile = os.path.join(destination, _d['title'])
    partfile = localfile + '.part'

    try:    os.remove(partfile)
    except: pass

    append_failed(title = _d['title'], endpoint = _d['endpoint'],
            media_hint = _d['media_hint'])
    clear_current()
    dispatch()

def dispatch(should_thread = True):
    log.info('Dispatching download')

    if assumed_running():
        return

    try:
        download = queue().pop(0)
    except IndexError, e:
        log.info('Download queue empty')
        return

    def store_curl_pid(dl):
        current()['title'] = dl.file_name
        current()['pid']   = dl.pid
        settings.persist()

    def _update_library(dl):
        update_library(download['media_hint'])

    def clear_download_and_dispatch(dl):
        clear_current()
        dispatch(False)

    def store_download_endpoint(dl):
        append_history(dl.endpoint)

    def append_failed_download(dl):
        append_failed(endpoint = dl.endpoint,
                title = dl.wizard.file_hint or download['title'],
                media_hint = download['media_hint'])

    def clear_download_from_failed(dl):
        remove_failed(dl.endpoint)

    def perform_download():
        dest_key = '%s_destination' % download['media_hint']
        downloader = ss.Downloader(download['endpoint'],
            destination = settings.get(dest_key),
            limit       = speed_limit(),
            strategy    = strategy(),
            avoid_small_files = True
        )
        downloader.wizard.avoid_flv = avoid_flv()

        downloader.on_start(store_curl_pid)
        downloader.on_start(clear_download_from_failed)

        downloader.on_success(_update_library)
        downloader.on_success(store_download_endpoint)
        downloader.on_success(clear_download_and_dispatch)

        downloader.on_error(append_failed_download)
        downloader.on_error(clear_download_and_dispatch)

        downloader.download()

    set_current(download)

    if should_thread:
        thread.start_new_thread(perform_download, ())
    else:
        perform_download()

def pid_running(pid):
    if running_windows(): return pid_running_windows(pid)
    else:                 return signal_process_unix(pid)

def pid_running_windows(pid):
    import ctypes, ctypes.wintypes

    # GetExitCodeProcess uses a special exit code to indicate that the process is
    # still running.
    still_active = 259
    kernel32     = ctypes.windll.kernel32
    handle       = kernel32.OpenProcess(1, 0, pid)

    if handle == 0:
        return False

    # If the process exited recently, a pid may still exist for the handle.
    # So, check if we can get the exit code.
    exit_code  = ctypes.wintypes.DWORD()
    is_running = ( kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) == 0 )
    kernel32.CloseHandle(handle)

    # See if we couldn't get the exit code or the exit code indicates that the
    # process is still running.
    return is_running or exit_code.value == still_active

def signal_process(pid, to_send = 0):
    if running_windows(): return signal_process_windows(pid, to_send)
    else:                 return signal_process_unix(pid,    to_send)

def signal_process_unix(pid, to_send = 0):
    try:
        os.kill(pid, to_send)
        return True
    except:
        return False

def signal_process_windows(pid, to_send = 0):
    import ctypes

    try:
        # 1 == PROCESS_TERMINATE
        handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
        ctypes.windll.kernel32.TerminateProcess(handle, to_send * -1)
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    except:
        return False
