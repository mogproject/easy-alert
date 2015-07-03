from datetime import datetime
from watcher import Watcher
from easy_alert.entity import Alert, Level
import logging
from easy_alert.util import get_server_id
from easy_alert.i18n import *
import paramiko
import subprocess
import re
import itertools


class SSHWatcher(Watcher):
    """
    Check SSH connection to servers
    """
    DEFAULT_PORT = 22
    CONNECTION_TIMEOUT = 10  # seconds

    def __init__(self, ssh_settings):
        super(SSHWatcher, self).__init__(ssh_settings=ssh_settings)

    def watch(self):
        """
        :return: list of Alert instances
        """
        start_time = datetime.now()

        target = list(itertools.chain.from_iterable(self._build_target_list(s) for s in self.ssh_settings))

        errors = []
        for name, host, port, user, key in target:
            is_success, msg = self._check_ssh_connection(host, port, user, key)
            if not is_success:
                m = MSG_SSH_STATUS_FORMAT % {'name': name, 'user': user, 'host': host, 'port': port, 'msg': msg}
                errors.append(m)

        if errors:
            message = MSG_SSH_ALERT % {'server_id': get_server_id(), 'result': '\n'.join('%s' % s for s in errors)}
            return [Alert(start_time, Level(logging.ERROR), MSG_SSH_ALERT_TITLE, message)]
        else:
            return []

    def _build_target_list(self, s):
        port = s.get('port', self.DEFAULT_PORT)
        user = s['user']
        key = s['key']

        cmd = s.get('dynamic')
        if not cmd:
            return [(s['name'], s['host'], port, user, key)]

        ret = []
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in p.stdout:
            r = re.compile('^\s*(.+)\s+(.+)\s*$')
            m = r.match(line)
            host, name = m.group(1, 2)
            ret.append((name, host, port, user, key))
        return ret

    @staticmethod
    def _check_ssh_connection(host, port, user, key):
        """
        :return: (is success, error message)
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(host, port, user, key_filename=key, timeout=10)
            return True, None
        except Exception as e:
            return False, '%s: %s' % (e.__class__.__name__, str(e))
        finally:
            client.close()
