# -*- coding: utf-8 -*-

EMAIL_ENCODING = 'utf-8'

MSG_DEBUG = u"DEBUG"
MSG_INFO = u"INFO"
MSG_WARN = u"WARN"
MSG_ERROR = u"ERROR"
MSG_CRITICAL = u"CRITICAL"

MSG_PROC_NOT_RUNNING = u'not running'
MSG_PROC_RUNNING = u'%(count)d process(es) are running'
MSG_PROC_STATUS_FORMAT = u'[%(level)s] %(name)s: %(count)s (not %(condition)s)'
MSG_PROC_ALERT_TITLE = u'Found Process Abnormality'
MSG_PROC_ALERT = u'Found the following process abnormality on server %(server_id)r.\n\n%(result)s\n\n=='

MSG_LOG_SUMMARY = u'[%(tag)s]: %(count)d messages'
MSG_LOG_SNIP = u'(snip)'
MSG_LOG_ALERT_TITLE = u'Found Error Messages'
MSG_LOG_ALERT = u'Found the following errors on server %(server_id)r.\n\n%(result)s\n=='
MSG_LOG_ALERT_PENDING_TITLE = u'Possible Retention of Log Watcher'
MSG_LOG_ALERT_PENDING = u"""Found the possible retention of Log Watcher on server %(server_id)r.\n
There exist multiple files which matches the pattern %(pattern)s.\n\n%(paths)s\n
Please check the state of the files, then restart Fluentd or other applications if needed."""

MSG_SSH_STATUS_FORMAT = u'[%(name)s](%(user)s@%(host)s:%(port)d): %(msg)s'
MSG_SSH_ALERT_TITLE = u'Found SSH Connection Error'
MSG_SSH_ALERT = u'Failed to connect to the following servers using SSH from %(server_id)r.\n\n%(result)s\n\n=='

MSG_CMD_ALERT_FORMAT = u"""[%(level)s] Failed health check: %(name)s
  actual: {code:%(code)d, stdout:%(stdout)s, stderr:%(stderr)s}
  expect: {code:%(expect_code)s, stdout:%(expect_stdout)s, stderr:%(expect_stderr)s}"""
MSG_CMD_ALERT_TITLE = u'Found Health Check Error'
MSG_CMD_ALERT = u'Found the following errors on server %(server_id)r.\n\n%(result)s\n\n=='

MSG_HTTP_ALERT_FORMAT = u"""[%(level)s] Failed health check: %(name)s
  url    : %(url)s
  actual : {code:%(code)d, size:%(size)d}
  expect : {code:%(expect_code)d, size:%(expect_size)s, regexp:%(expect_regexp)s}
  message: %(additional_info)s"""
MSG_HTTP_ALERT_FORMAT_ERR = u"""[%(level)s] Failed health check: %(name)s
  url    : %(url)s
  error  : %(error)s
  message: %(additional_info)s"""
MSG_HTTP_ALERT_TITLE = u'Found HTTP Connection Error'
MSG_HTTP_ALERT = u'Found the following errors on server %(server_id)r.\n\n%(result)s\n\n=='

MSG_SUBJECT_FORMAT = u'[%(level)s] [%(group_id)s:%(server_id)s] %(title)s (%(start_time)s)'
