import uwsgi
import time

def application(env, sr):

    ws_scheme = 'ws'
    if 'HTTPS' in env or env['wsgi.url_scheme'] == 'https':
        ws_scheme = 'wss'

    if env['PATH_INFO'] == '/':
        sr('200 OK', [('Content-Type','text/html')])
        output = """
<!doctype html>
<html>
  <head>
      <meta charset="utf-8">
      <script src="/reconnecting-websocket.js"></script>
      <script language="Javascript">
        var s = new ReconnectingWebSocket("%s://%s/foobar/");
        s.onopen = function() {
            console.log("connected !!!");
            //s.send("SEND_ONCE cd KEY_MUTE\\n");
            s.onmessage({data:"Connected"})
        };
        s.onmessage = function(e) {
            var bb = document.getElementById('blackboard')
            var html = bb.innerHTML;
            bb.innerHTML = html + '<br/>' + e.data;
            bb.scrollTop = bb.scrollHeight;
        };

        s.onerror = function(e) {
            console.log(e);
        }

        s.onclose = function(e) {
            console.log("connection closed");
            s.onmessage({data:"Connection closed"})
        }

        function sendcustomcmd() {
            var value = document.getElementById('cmd').value;
            s.send(value+"\\n");
        }
        function sendcmd(cmd) {
            console.log("sending command "+cmd)
            s.send("SEND_ONCE cd "+cmd+"\\n")
        }
      </script>
 </head>
<body>
    <h1>lircd over WebSocket <br>
        <small>uses unix socets and not exec('irsend')</small>
    </h1>
    <input type="text" id="cmd"/>
    <input type="button" value="send" onClick="sendcustomcmd();"/>
    <input type="button" value="Mute" onClick="sendcmd('KEY_MUTE');"/>
    <input type="button" value="Volume UP" onClick="sendcmd('KEY_VOLUMEUP');"/>
    <input type="button" value="Volume DOWN" onClick="sendcmd('KEY_VOLUMEDOWN');"/>
<div id="blackboard" style="width:640px;height:480px;background-color:black;color:white;border: solid 2px red;overflow:auto">
</div>
</body>
</html>
        """ % (ws_scheme, env['HTTP_HOST'])
        return output.encode()
    elif env['PATH_INFO'] == '/favicon.ico':
        return ""
    elif env['PATH_INFO'] == '/reconnecting-websocket.js':
        return open("reconnecting-websocket.js").read().encode()
    elif env['PATH_INFO'] == '/foobar/':
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
