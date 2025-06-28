# config_utils.py
import os
import logging
from mht import gui  # adjust import as needed

def set_logging_and_kivy_config(verbose: bool = False):
    os.environ["KIVY_NO_FILELOG"] = "1"
    os.environ['KIVY_NO_CONSOLELOG'] = '1'
    gui.Config.set('graphics', 'width', str(800))
    gui.Config.set('graphics', 'position', 'custom')
    gui.Config.set('graphics', 'left', '0')
    gui.Config.set('graphics', 'top', '0')

    log_level = logging.DEBUG if verbose else logging.WARNING
    gui.Config.set('kivy', 'log_level', 'debug' if verbose else 'warning')
    logging.basicConfig(level=log_level)
    logging.getLogger().setLevel(log_level)
    logging.getLogger('matplotlib').setLevel(log_level)
    logging.getLogger('kivy.network.urlrequest').setLevel(log_level)
    logging.getLogger('kivy.network.httpclient').setLevel(log_level)
    logging.getLogger('h2.connection').setLevel(log_level)
    logging.getLogger('hpack').setLevel(log_level)
    logging.getLogger('hyper').setLevel(log_level)

    # 3) Globally raise the stdlib log level
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger().setLevel(logging.WARNING)

    # 4) Specifically silence the HTTP/2 + HPACK libraries
    logging.getLogger('h2.connection').setLevel(logging.WARNING)
    logging.getLogger('hpack').setLevel(logging.WARNING)
    logging.getLogger('hyper').setLevel(logging.WARNING)

    # 5) And silence Kivy’s URLRequest debug chatter (if you use that)
    logging.getLogger('kivy.network.urlrequest').setLevel(logging.WARNING)
    logging.getLogger('kivy.network.httpclient').setLevel(logging.WARNING)
