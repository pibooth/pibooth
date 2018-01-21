# -*- coding: utf-8 -*-

import cups
import threading
import collections
from xml.etree import ElementTree
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    # Python 2.x fallback
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


class NotificationHandler(BaseHTTPRequestHandler):

    _last_notif = collections.deque(maxlen=1000)

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
        """Dont print requests.
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
            print("Notification without data received")
        else:
            chunk_data = self.get_chunk_data(chunk_size)
            root = ElementTree.fromstring(chunk_data.decode('utf-8'))
            for channel in root.iterfind('channel'):
                for item in reversed([e for e in channel.iterfind('item')]):
                    txt = ElementTree.tostring(item, encoding='utf8')
                    if txt not in NotificationHandler._last_notif:
                        # Print only the new notifications
                        print("{} - {}".format(item.findtext('pubDate'), item.findtext('title')))
                        NotificationHandler._last_notif.append(txt)

        self.send_response(200)
        self.end_headers()


class NotificationServer(HTTPServer):

    def __init__(self, cups_conn):
        HTTPServer.__init__(self, ('localhost', 9988), NotificationHandler)
        self._thread = None
        self._conn = cups_conn
        self._id = None
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

        # Remove all existing subscribtions (may exists due to previous crashes)
        try:
            for sub in self._conn.getSubscriptions(self.notif_uri):
                self._conn.cancelSubscription(sub['notify-subscription-id'])
        except cups.IPPError:
            pass

        # Renew notifications subscription
        cups_uri = "ipp://localhost:{}".format(cups.getPort())
        self._id = self._conn.createSubscription(cups_uri, recipient_uri=self.notif_uri,
                                                 events=['job-completed',
                                                         'job-created',
                                                         'job-state-changed',
                                                         'job-stopped',
                                                         'printer-restarted',
                                                         'printer-shutdown',
                                                         'printer-state-changed',
                                                         'printer-stopped'])

    def is_running(self):
        """Return True if the notification server is started.
        """
        if self._thread:
            return self._thread.is_alive()
        return False

    def shutdown(self):
        """Stop the notification server.
        """
        if self.is_running():
            if self._id:
                self._conn.cancelSubscription(self._id)
            HTTPServer.shutdown(self)
            self._thread.join()
            self._thread = None
        self.server_close()  # Close socket, can be opened event if thread not started


class PtbPrinter(object):

    def __init__(self):
        self._conn = cups.Connection()
        self._notif_server = NotificationServer(self._conn)

    def print_file(self, filename):
        """Send a file to the CUPS server to the default printer.
        """
        if not self._notif_server.is_running():
            self._notif_server.start()
        if not self._conn.getDefault():
            raise EnvironmentError("Default printer not found")
        self._conn.printFile(self._conn.getDefault(), filename, 'pibooth', {})

    def cancel_all_tasks(self):
        """Cancel all tasks in the queue.
        """
        self._conn.cancelAllJobs(self._conn.getDefault())

    def quit(self):
        """Do cleanup actions.
        """
        self._notif_server.shutdown()
