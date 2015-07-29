# -*- coding: utf-8 -*-

EMAIL_ENCODING = 'iso-2022-jp'

MSG_DEBUG = u"デバッグ"
MSG_INFO = u"情報"
MSG_WARN = u"警戒"
MSG_ERROR = u"危険"
MSG_CRITICAL = u"緊急"

MSG_PROC_NOT_RUNNING = u'起動していません'
MSG_PROC_RUNNING = u'%(count)d 個 起動しています'
MSG_PROC_STATUS_FORMAT = u'[%(level)s] %(name)s: %(count)s (%(condition)s に違反)'
MSG_PROC_ALERT_TITLE = u'プロセス異常を検知しました'
MSG_PROC_ALERT = u'サーバ %(server_id)s にて、以下のプロセス異常を検知しました。\n\n%(result)s\n\n以上'

MSG_LOG_SUMMARY = u'[%(tag)s]: %(count)d件'
MSG_LOG_SNIP = u'(省略されました)'
MSG_LOG_ALERT_TITLE = u'エラーログを検知しました'
MSG_LOG_ALERT = u'サーバ %(server_id)s にて、以下のエラーを検知しました。\n\n%(result)s\n以上'
MSG_LOG_ALERT_PENDING_TITLE = u'ログ監視が滞留している可能性があります'
MSG_LOG_ALERT_PENDING = u"""サーバ %(server_id)s にて、ログ監視滞留の兆候を検知しました。\n
パターン %(pattern)s にマッチするファイルが複数存在します。\n\n%(paths)s\n
ファイルの状態を確認し、問題があれば Fluentd および各アプリケーションの再起動を試みてください。"""

MSG_SSH_STATUS_FORMAT = u'[%(name)s](%(user)s@%(host)s:%(port)d): %(msg)s'
MSG_SSH_ALERT_TITLE = u'SSH疎通異常を検知しました'
MSG_SSH_ALERT = u'サーバ %(server_id)s から、以下のサーバに対する SSH 疎通確認に失敗しました。\n\n%(result)s\n\n以上'

MSG_CMD_ALERT_FORMAT = u"""[%(level)s] %(name)s のヘルスチェックに失敗
  actual: {code:%(code)d, stdout:%(stdout)s, stderr:%(stderr)s}
  expect: {code:%(expect_code)s, stdout:%(expect_stdout)s, stderr:%(expect_stderr)s}"""
MSG_CMD_ALERT_TITLE = u'ヘルスチェック異常を検知しました'
MSG_CMD_ALERT = u'サーバ %(server_id)s にて、以下のヘルスチェック異常を検知しました。\n\n%(result)s\n\n以上'

MSG_HTTP_ALERT_FORMAT = u"""[%(level)s] %(name)s のヘルスチェックに失敗
  url    : %(url)s
  actual : {code:%(code)d, size:%(size)d}
  expect : {code:%(expect_code)d, size:%(expect_size)s, regexp:%(expect_regexp)s}
  message: %(additional_info)s"""
MSG_HTTP_ALERT_FORMAT_ERR = u"""[%(level)s] %(name)s のヘルスチェックに失敗
  url    : %(url)s
  error  : %(error)s
  message: %(additional_info)s"""
MSG_HTTP_ALERT_TITLE = u'HTTP疎通異常を検知しました'
MSG_HTTP_ALERT = u'サーバ %(server_id)s にて、以下のヘルスチェック異常を検知しました。\n\n%(result)s\n\n以上'

MSG_SUBJECT_FORMAT = u'【%(level)s】[%(group_id)s:%(server_id)s] %(title)s (%(start_time)s)'
