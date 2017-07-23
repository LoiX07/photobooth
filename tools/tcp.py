# -*- coding: utf-8 -*-
"""
Server for picture synchronization
"""

from socketserver import TCPServer, BaseRequestHandler

from .remote_log import REMOTE_LOG as log


class PhotoTCPHandler(BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        try:
            self.server.put(
                self.data.decode(encoding="utf-8", errors="strict"))
        except UnicodeError:
            pass


class PhotoServer(TCPServer):
    """ Class that represents our TCP server"""

    def __init__(self, address, port, queue):
        self._queue = queue
        log.debug(
            'Binding the listening socket to address %(address)s and port %(port)s',
            {'address': address,
             'port': port})
        super(PhotoServer, self).__init__((address, port), PhotoTCPHandler)

    def put(self, data):
        """ Method used to put data into the queue """
        log.debug('Received the following data from the network: %s', data)
        self._queue.put(data)
