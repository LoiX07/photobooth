# -*- coding: utf-8 -*-
"""
Server for picture synchronisations
"""

from socketserver import TCPServer, BaseRequestHandler

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
        self.server.put(self.data)

class PhotoServer(TCPServer):
    """ Class that represents our TCP server"""
    def __init__(self, port, queue):
        self._queue = queue
        super(PhotoServer, self).__init__(("localhost", port), PhotoTCPHandler)

    def put(self, data):
        """ Method used to put data into the queue """
        self._queue.put(data)
