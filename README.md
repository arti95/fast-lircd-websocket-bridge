# LIRC daemon controll webinterface using WebSockets

With this you can send mute, volume up or volume down commands to lirc daemon 
from every where.

# How to run

you need uwsgi and python3 with asyncio

 1. git clone this
 2. create virtualenv `pyvenv venv` and activate it `source venv/bin/activate`
 3. install flask `pip install flask`
 4. start websocket daemon `uwsgi --ini config.ini:ws-serv`
 5. start flask website `uwsgi --ini config.ini:web-dev`
 6. open http://localhost:8080/
 
`lircd_socket` variable in `config.ini` controlls where the lirc daemon is
