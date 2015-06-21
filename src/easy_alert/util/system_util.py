import os
import socket


def get_server_id():
    return os.environ.get('NICKNAME', socket.gethostname())
