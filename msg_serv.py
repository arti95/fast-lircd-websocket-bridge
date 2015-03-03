#!/usr/bin/env python3
import asyncio
import sys
import os

class EchoServer(asyncio.Protocol):
    clients = {}
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport
        self.clients[transport] = None

    def data_received(self, data):
        # print('data received: {}'.format(data.decode()))
        for transport in self.clients:
            if transport == self.transport:
                pass
                #continue
            transport.write(data)

    def connection_lost(self, exc):
        print("connection lost")
        self.transport.close()
        del self.clients[self.transport]

server_address = sys.argv[1]

try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise

loop = asyncio.get_event_loop()
#coro = loop.create_server(EchoServer, "127.0.0.1", 8888)
coro = loop.create_unix_server(EchoServer, server_address)
server = loop.run_until_complete(coro)
print('serving on {}'.format(server_address))

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("exit")
finally:
    server.close()
    loop.close()
