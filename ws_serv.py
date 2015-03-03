import uwsgi
import time

def application(env, sr):
    print("websockets is starting...")
    uwsgi.websocket_handshake(env['HTTP_SEC_WEBSOCKET_KEY'], env.get('HTTP_ORIGIN', ''))
    lircd_socket = uwsgi.opt["lircd_socket"].decode("utf-8")
    msg_serv_socket = uwsgi.opt["msg_serv_socket"].decode("utf-8")
    print("connecting to lircd socket at {}".format(lircd_socket))
    lircd_fd = uwsgi.async_connect(lircd_socket)
    print("lircd_fd = {}".format(lircd_fd))
    print("connecting to msg_srv socket at {}".format(msg_serv_socket))
    msg_serv_fd = uwsgi.async_connect(msg_serv_socket)
    print("msg_serv_fd = {}".format(msg_serv_fd))
    websocket_fd = uwsgi.connection_fd()
    while True:
        uwsgi.wait_fd_read(websocket_fd, 3)
        uwsgi.wait_fd_read(lircd_fd)
        uwsgi.wait_fd_read(msg_serv_fd)
        uwsgi.suspend()
        fd = uwsgi.ready_fd()
        if fd > -1:
            if fd == websocket_fd:
                msg = uwsgi.websocket_recv_nb()
                if msg and len(msg) > 0:
                    print("got message from ws: {}".format(msg))
                    uwsgi.send(lircd_fd, msg)
            elif fd == lircd_fd:
                msg = uwsgi.recv(lircd_fd).decode()
                for msg in msg.split("\n"):
                    if not len(msg):
                        continue
                    print("got message from lircd: {}".format(msg))
                    uwsgi.websocket_send(msg.encode())
            elif fd == msg_serv_fd:
                msg = uwsgi.recv(msg_serv_fd)
                print("got message from msg_srv: {}".format(msg))
                uwsgi.websocket_send(msg)
        else:
            # on timeout call websocket_recv_nb again to manage ping/pong
            msg = uwsgi.websocket_recv_nb()
            print("ws ping/pong")
            if msg and len(msg) > 0:
                print("got message from ws: {}".format(msg))
                uwsgi.send(lircd_fd, msg)
