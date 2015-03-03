# fast-lircd-websocket-bridge a websocket to lirc daemon socket bridge

Needs python 3.4 (or 3.3 with asyncio lib), uwsgi and lirc daemon running somewhere.

`lircd_socket` variable in `config.ini` is the address to lircd socket

this project can be started with this command:

    uwsgi --ini config.ini:dev
    
and when its running you should be abel to open http://localhost:9090/ in your
browser and send some command to lirc daemon


## this code has pretty much no error checking and will fall into pieces quite easily

