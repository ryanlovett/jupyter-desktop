from contextlib import closing
import os
import socket
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

def available_port():
    '''Linux returns a random port as low as 1024. We need something >= 5900
       to make the display math work.'''
    for port in range(5900, 65535):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind(('', port))
            except Exception:
                continue
            else:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                break
    return port

def setup_desktop():
    # make a secure temporary directory for sockets
    # This is only readable, writeable & searchable by our uid
    sockets_dir = tempfile.mkdtemp()
    sockets_path = os.path.join(sockets_dir, 'vnc-socket')
    rfbport = available_port()
    return {
        'command': [
            'websockify', '-v',
            '--web', os.path.join(HERE, 'share/web/noVNC-1.1.0'),
            '--heartbeat', '30',
            str(rfbport),
            '--unix-target', sockets_path,
            '--',
            os.path.join(HERE, 'share/tigervnc/bin/vncserver'),
            '-verbose',
            '-xstartup', os.path.join(HERE, 'share/xstartup'),
            '-geometry', '1024x768',
            '-SecurityTypes', 'None',
            '-rfbunixpath', sockets_path,
            '-fg',
            # rfb display port is typically the listing port minus 5900,
            # via rfc 6143: "On systems with multiple RFB servers, server N
            # typically listens on port 5900+N"
            ':' + str(rfbport-5900),
        ],
        'port': rfbport,
        'timeout': 30,
        'mappath': {'/': '/vnc_lite.html'},
    }
