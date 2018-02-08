# -*- coding: utf-8 -*-

try:
    import cups
except ImportError:
    cups = None  # CUPS is optional
import threading
import collections
import os.path as osp
from xml.etree import ElementTree
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    # Python 2.x fallback
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from pibooth.utils import LOGGER


class NotificationHandler(BaseHTTPRequestHandler):

    _last_notif = collections.deque(maxlen=500)

    def get_chunk_size(self):
        size_str = self.rfile.read(2)
        while size_str[-2:] != b"\r\n":
            size_str += self.rfile.read(1)
        return int(size_str[:-2], 16)

    def get_chunk_data(self, chunk_size):
        data = self.rfile.read(chunk_size)
        self.rfile.read(2)
        return data

    def log_request(self, code='-', size='-'):
        """Don't print requests.
        """
        pass

    def do_GET(self):
        """At the begining of the connection, CUPS server ask for existing
        RSS file. What is the reason?
        """
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_PUT(self):
        """Serve a PUT request.
        """
        chunk_size = self.get_chunk_size()
        if chunk_size == 0:
            LOGGER.warning("Notification without data received")
        else:
            chunk_data = self.get_chunk_data(chunk_size)
            root = ElementTree.fromstring(chunk_data.decode('utf-8'))
            for channel in root.iterfind('channel'):
                for item in reversed([e for e in channel.iterfind('item')]):
                    txt = ElementTree.tostring(item, encoding='utf8')
                    if txt not in NotificationHandler._last_notif:
                        # Print only the new notifications
                        LOGGER.info("%s - %s", item.findtext('pubDate'), item.findtext('title'))
                        NotificationHandler._last_notif.append(txt)

        self.send_response(200)
        self.end_headers()


class NotificationServer(HTTPServer):

    def __init__(self, cups_conn):
        HTTPServer.__init__(self, ('localhost', 9988), NotificationHandler)
        self._thread = None
        self._conn = cups_conn
        self.notif_uri = 'rss://{}:{}'.format(self.server_address[0],
                                              self.server_address[1])

    def start(self):
        """Start the notification server.
        """
        if self._thread:
            raise EnvironmentError("Server is already running")
        self._thread = threading.Thread(target=self.serve_forever)
        self._thread.daemon = True
        self._thread.start()

        self.cancel_subscriptions()

        # Renew notifications subscription
        cups_uri = "ipp://localhost:{}".format(cups.getPort())
        self._conn.createSubscription(cups_uri, recipient_uri=self.notif_uri,
                                      events=['job-completed',
                                              'job-created',
                                              'job-stopped',
                                              'printer-restarted',
                                              'printer-shutdown',
                                              'printer-stopped'])

    def is_running(self):
        """Return True if the notification server is started.
        """
        if self._thread:
            return self._thread.is_alive()
        return False

    def cancel_subscriptions(self):
        """Cancel all subscriptions related to the notification URI.
        """
        try:
            for sub in self._conn.getSubscriptions(self.notif_uri):
                self._conn.cancelSubscription(sub['notify-subscription-id'])
        except cups.IPPError:
            pass

    def shutdown(self):
        """Stop the notification server.
        """
        if self.is_running():
            self.cancel_subscriptions()
            HTTPServer.shutdown(self)
            self._thread.join()
            self._thread = None
        self.server_close()  # Close socket, can be opened event if thread not started


class PtbPrinter(object):

    def __init__(self, name='default'):
        self._conn = cups.Connection() if cups else None
        self._notif_server = NotificationServer(self._conn)
        self.name = None
        if not cups:
            return  # CUPS is not installed
        elif not name or name.lower() == 'default':
            self.name = self._conn.getDefault()
            if not self.name and self._conn.getPrinters():
                self.name = list(self._conn.getPrinters().keys())[0]  # Take first one
        elif name in self._conn.getPrinters():
            self.name = name

    def is_installed(self):
        """Return True if the CUPS server is available for printing.
        """
        return cups is not None

    def print_file(self, filename):
        """Send a file to the CUPS server to the default printer.
        """
        if not self._notif_server.is_running():
            self._notif_server.start()
        if not self.name:
            raise EnvironmentError("No printer found (check config file or CUPS config)")
        self._conn.printFile(self.name, filename, osp.basename(filename), {})

    def cancel_all_tasks(self):
        """Cancel all tasks in the queue.
        """
        if not self.name:
            raise EnvironmentError("No printer found (check config file or CUPS config)")
        self._conn.cancelAllJobs(self.name)

    def quit(self):
        """Do cleanup actions.
        """
        self._notif_server.shutdown()
