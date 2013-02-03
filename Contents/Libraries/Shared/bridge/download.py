import plex
import user
import environment

import os
import signal
import thread
from ss import Downloader, util

import logging
log = logging.getLogger('ss.bridge.download')

def queue():           return user.initialize_dict('downloads',        [])
def history():         return user.initialize_dict('download_history', [])
def avoid_flv():       return plex.user_prefs()['avoid_flv_downloading']
def speed_limit():     return plex.user_prefs()['download_limit']
def current():         return plex.user_dict()['download_current']
def current_pid():     return current().get('pid')
def assumed_running(): return 'download_current' in plex.user_dict()
def curl_running():    return pid_running(current_pid())
def running_windows(): return 'nt' == os.name

def clear_history(): user.attempt_clear('download_history')
def clear_current(): user.attempt_clear('download_current')

def append(**kwargs):
    queue().append(kwargs)
    plex.user_dict().Save()

def remove(download):
    queue().remove(download)
    plex.user_dict().Save()

def set_current(download):
    plex.user_dict()['download_current'] = download
    plex.user_dict().Save()

def pid_running(pid):
    if running_windows(): return pid_running_windows(pid)
    else:                 return signal_process_unix(pid)

def is_current(endpoint):
    return assumed_running() and endpoint == current()['endpoint']

def in_history(endpoint):
    found = from_queue(endpoint)

    if found: return True
    else:     return endpoint in history()

def from_queue(endpoint):
    if is_current(endpoint):
        return current()
    else:
        found = filter(lambda h: h['endpoint'] == endpoint, queue())

        if found:
            return found[0]

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

def command(command):
    if curl_running():
        signals  = [ signal.SIGTERM, signal.SIGINT ]
        commands = [ 'cancel',       'next' ]
        to_send  = signals[commands.index(command)]
        pid      = current_pid()

        if pid:
            return signal_process(pid, to_send)

def dispatch(should_thread = True):
    log.info('Dispatching download')
    if not assumed_running():
        try:
            download = queue().pop(0)
        except IndexError, e:
            log.info('Download queue empty')
            return

        set_current(download)

        def perform_download():
            downloader = Downloader(download['endpoint'],
                environment = environment.plex,
                destination = plex.section_destination(download['media_hint']),
                limit       = speed_limit()
            )
            downloader.wizard.avoid_flv = avoid_flv()

            def store_curl_pid(dl):
                current()['title'] = dl.file_name()
                current()['pid']   = dl.pid
                plex.user_dict().Save()

            def update_library(dl):
                plex.refresh_section(download['media_hint'])

            def clear_download_and_dispatch(dl):
                clear_current()
                dispatch(False)

            def store_download_endpoint(dl):
                history().append(dl.endpoint)

            downloader.on_start(store_curl_pid)

            downloader.on_success(update_library)
            downloader.on_success(store_download_endpoint)
            downloader.on_success(clear_download_and_dispatch)

            downloader.on_error(clear_download_and_dispatch)
            downloader.download()

        if should_thread:
            thread.start_new_thread(perform_download, ())
        else:
            perform_download()
