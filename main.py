from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return """<!doctype html>
<html>
  <head>
      <meta charset="utf-8">
      <script src="/static/reconnecting-websocket.min.js"></script>
      <script language="Javascript">
        var s = new ReconnectingWebSocket("ws://localhost:8080/ws/");
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
</html>"""

if __name__ == "__main__":
    app.run(debug=True)