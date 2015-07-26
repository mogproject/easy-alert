import logging
import paramiko
import subprocess
import re
import itertools

from datetime import datetime
from watcher import Watcher
from easy_alert.entity import Alert, Level
from easy_alert.util import get_server_id
from easy_alert.i18n import *
from easy_alert.setting.setting_error import SettingError


class SSHWatcher(Watcher):
    """
    Check SSH connection to servers

    configuration should be a list of this dict
      user [required]: user name to log in
      key  [required]: path to the SSH private key
      port           : SSH port number (default:22)
      dynamic        : command line string for getting dynamic host definitions
                       The output should be '<host> <name>' for each line.
      host        [*]: host name or IP address of the host to check connection [*required if not dynamic]
      name        [*]: short description of the host [*required if not dynamic]

    The alert level is always ERR.
    """
    DEFAULT_PORT = 22
    CONNECTION_TIMEOUT = 10  # seconds

    def __init__(self, ssh_setting):
        if not isinstance(ssh_setting, list):
            raise SettingError('SSHWatcher settings not a list: %s' % ssh_setting)

        settings = []
        for s in ssh_setting:
            if not isinstance(s, dict):
                raise SettingError('SSHWatcher settings not a dict: %s' % s)

            try:
                user = s['user']
                key = s['key']
                port = int(s.get('port', self.DEFAULT_PORT))
                dynamic_cmd = s.get('dynamic')
                is_dynamic = dynamic_cmd is not None
                name = None if is_dynamic else s['name']
                host = None if is_dynamic else s['host']
                settings.append((user, key, port, is_dynamic, name, host, dynamic_cmd))
            except KeyError as e:
                raise SettingError('SSHWatcher not found config key: %s' % e)
            except Exception as e:
                raise SettingError('SSHWatcher settings syntax error: %s' % e)

        super(SSHWatcher, self).__init__(settings=settings)

    @staticmethod
    def _build_target_list(s):
        """
        :param s: tuple (user, key, port, is_dynamic, name, host, dynamic_cmd)
        :return: list of the tuple (name, host, port, user, key)
        """
        user, key, port, is_dynamic, name, host, dynamic_cmd = s

        if not is_dynamic:
            return [(name, host, port, user, key)]

        ret = []
        p = subprocess.Popen(dynamic_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in p.stdout:
            r = re.compile('^\s*(.+)\s+(.+)\s*$')
            m = r.match(line)
            host, name = m.group(1, 2)
            ret.append((name, host, port, user, key))
        return ret

    def watch(self):
        """
        :return: list of Alert instances
        """
        start_time = datetime.now()

        target = list(itertools.chain.from_iterable(self._build_target_list(s) for s in self.settings))

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
