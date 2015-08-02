import re
import urllib2
from urlparse import urlparse
from datetime import datetime
from watcher import Watcher
from easy_alert.entity import Alert, Level
from easy_alert.i18n import *
from easy_alert.setting.setting_error import SettingError
from easy_alert.util import Matcher, get_server_id, apply_option, with_retry, exists


class HTTPWatcher(Watcher):
    """
    Check http(s) connection and response to the url

    configuration should be a list of this dict
      name    [required]: short description for the url
      level   [required]: alert level (should be in {critical, error, warn, info, debug})
      url     [required]: url string (scheme should be http or https)
      timeout           : connection timeout in second (default:10)
      retry             : max count to retry (default:2)
      additional_info   : additional information string (default:empty string)
      expect_code    [*]: expected status code of the response
      expect_size    [*]: expected data size in matcher format (e.g. '=123', '< 123', '>=123')
      expect_regexp  [*]: expected content text in regexp

    * Any of {expect_code, expect_size, expect_text} is required.
    """
    DEFAULT_TIMEOUT = 10
    DEFAULT_RETRY = 2

    def __init__(self, http_setting):
        if not isinstance(http_setting, list):
            raise SettingError('HTTPWatcher settings not a list: %s' % http_setting)

        settings = []
        for s in http_setting:
            if not isinstance(s, dict):
                raise SettingError('HTTPWatcher settings not a dict: %s' % s)

            try:
                name = s['name']
                level = self.__get_level(s['level'])
                url = s['url']
                timeout = int(s.get('timeout', self.DEFAULT_TIMEOUT))
                retry = int(s.get('retry', self.DEFAULT_RETRY))
                additional_info = s.get('additional_info', '')
                expect_code = apply_option(int, s.get('expect_code'))
                expect_size = apply_option(Matcher, s.get('expect_size'))
                expect_regexp = apply_option(re.compile, s.get('expect_regexp'))
            except SettingError as e:
                raise e
            except KeyError as e:
                raise SettingError('HTTPWatcher not found config key: %s' % e)
            except Exception as e:
                raise SettingError('HTTPWatcher settings syntax error: %s' % e)

            self.__verify_url(url)
            if all([expect_code is None, expect_size is None, expect_regexp is None]):
                raise SettingError('HTTPWatcher any of expect_code, expect_size or expect_regexp should be set.')

            settings.append((
                name, level, url, timeout, retry, additional_info, expect_code, expect_size, expect_regexp))

        super(HTTPWatcher, self).__init__(settings=settings)

    @staticmethod
    def __verify_url(url):
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme or 'http'
        if scheme not in ['http', 'https']:
            raise SettingError('HTTPWatcher unsupported scheme: %s' % scheme)

    @staticmethod
    def __get_level(level_str):
        level = [l for l in Level.seq if l.get_keyword() == level_str]
        if not level:
            raise SettingError('HTTPWatcher invalid level: %s' % level_str)
        return level[0]

    @staticmethod
    def _connect_url(url, timeout):
        u = urllib2.urlopen(url, timeout=timeout)
        data = u.read()
        return u.getcode(), data

    @staticmethod
    def _should_alert(code, data, expect_code, expect_size, expect_regexp):
        return any([
            exists(expect_code, lambda x: x != code),
            exists(expect_size, lambda x: not x.check(len(data))),
            exists(expect_regexp, lambda x: not x.findall(data)),
        ])

    def watch(self):
        """
        :return: list of Alert instances
        """
        start_time = datetime.now()

        result = []
        for name, level, url, timeout, retry, additional_info, expect_code, expect_size, expect_regexp in self.settings:
            try:
                code, data = with_retry(retry)(lambda: self._connect_url(url, timeout))
                if self._should_alert(code, data, expect_code, expect_size, expect_regexp):
                    message = MSG_HTTP_ALERT_FORMAT % {
                        'level': level.get_text(),
                        'name': name,
                        'url': url,
                        'code': code,
                        'size': len(data),
                        'expect_code': expect_code,
                        'expect_size': expect_size,
                        'expect_regexp': expect_regexp.pattern if expect_regexp else None,
                        'additional_info': additional_info,
                    }
                    result.append((level, message))
            except Exception as e:
                message = MSG_HTTP_ALERT_FORMAT_ERR % {
                    'level': level.get_text(),
                    'name': name,
                    'url': url,
                    'error': '%s: %s' % (e.__class__.__name__,  e),
                    'additional_info': additional_info,
                }
                result.append((level, message))

        if result:
            max_level = max(r[0] for r in result)
            message = MSG_HTTP_ALERT % {'server_id': get_server_id(), 'result': '\n'.join(r[1] for r in result)}
            return [Alert(start_time, max_level, MSG_HTTP_ALERT_TITLE, message)]
        else:
            return []
